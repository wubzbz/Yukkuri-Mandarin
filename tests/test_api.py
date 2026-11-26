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
