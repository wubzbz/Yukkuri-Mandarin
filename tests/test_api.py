import sqlite3

import pytest

from yukkurimandarin import Config, Converter, pinyin_convert, text_convert
from yukkurimandarin.db import PinyinEntry, PinyinRepository


def test_text_convert_empty():
    assert text_convert("") == ""


def test_text_convert_invalid_input():
    with pytest.raises(ValueError, match="参数sentence必须是字符串: 2"):
        text_convert(2)  # type: ignore[arg-type]


def test_text_convert_basic():
    assert text_convert("你好") == "/にい'は/お"


def test_text_convert_without_accent():
    assert text_convert("你好", without_accent=True) == "にいはお"


def test_text_convert_yi():
    assert text_convert("一天", without_accent=True) == "いいてやん"


def test_text_convert_punctuation():
    assert text_convert("你好，世界！") == "/にい'は/お、す'/いじ'え。"


def test_pinyin_convert():
    assert pinyin_convert(", . ; ? invalid invalid1 ", error="@") == "、。,?@@"


def test_pinyin_convert_empty():
    assert pinyin_convert("") == ""


def test_pinyin_convert_without_accent():
    assert pinyin_convert("ni3 hao3", without_accent=True) == "にいはお"


def test_converter_reuse():
    with Converter() as converter:
        first = converter.text_convert("你好")
        second = converter.text_convert("你好")
        assert first == second


def test_converter_custom_database(tmp_path):
    path = tmp_path / "mine.db"
    # 变调后“你好”的 serial 是 ni 023 / hao 230
    PinyinRepository.create(path, [PinyinEntry("ni", "023", "にい")])
    config = Config(database=path)
    assert text_convert("你好", config=config) == "にい"


def test_default_tokenizer_is_cached(monkeypatch):
    from yukkurimandarin import api

    calls = []
    monkeypatch.setattr(api, "_TOKENIZER_INITIALIZED", False, raising=False)
    monkeypatch.setattr(api, "_DEFAULT_TOKENIZER", None, raising=False)

    def factory():
        calls.append(1)
        return object()

    monkeypatch.setattr(api, "_create_tokenizer", factory)
    first = api._default_tokenizer()
    second = api._default_tokenizer()
    assert first is second
    assert len(calls) == 1


def test_text_convert_non_hanzi_skips_resources(monkeypatch, tmp_path):
    from yukkurimandarin import api

    monkeypatch.setattr(api, "_TOKENIZER_INITIALIZED", False, raising=False)
    monkeypatch.setattr(api, "_DEFAULT_TOKENIZER", None, raising=False)
    calls = []

    def factory():
        calls.append(1)
        return object()

    monkeypatch.setattr(api, "_create_tokenizer", factory)
    config = Config(database=tmp_path / "missing.db")
    assert text_convert("abc", config=config) == ""
    assert text_convert("，。", config=config) == "、。"
    assert calls == []


def test_pinyin_convert_zero_tone_is_neutral(tmp_path):
    path = tmp_path / "db.db"
    PinyinRepository.create(path, [PinyinEntry("ma", "050", "ま")])
    config = Config(database=path)
    assert pinyin_convert("ma0", config=config) == "ま"


def test_pinyin_convert_keep_error(tmp_path):
    path = tmp_path / "db.db"
    PinyinRepository.create(path, [])
    config = Config(database=path)
    assert pinyin_convert("bad1", error="keep", config=config) == "bad"


def test_converter_migrates_legacy_database(tmp_path):
    path = tmp_path / "legacy.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE pinyin_data ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "yinjie TEXT NOT NULL, tone TEXT NOT NULL, hiragana TEXT NOT NULL, "
        "UNIQUE (yinjie, tone) ON CONFLICT REPLACE)"
    )
    conn.execute("INSERT INTO pinyin_data (yinjie, tone, hiragana) VALUES ('ni', '023', 'にい')")
    conn.commit()
    conn.close()

    config = Config(database=path)
    assert text_convert("你好", config=config) == "にい"

    conn = sqlite3.connect(path)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
    finally:
        conn.close()
    assert not [
        p for p in path.parent.iterdir() if p.name.endswith(("-wal", "-shm"))
    ]
