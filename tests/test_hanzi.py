import logging

import pytest

from yukkurimandarin.db import PinyinEntry, PinyinRepository
from yukkurimandarin.pipeline.hanzi import fill_kana, fill_pinyin
from yukkurimandarin.segments import Document


def test_fill_pinyin_without_tokenizer():
    doc = fill_pinyin(Document.from_text("你好"))
    assert [(s.syllable, s.tone) for s in doc.syllables] == [("ni", 3), ("hao", 3)]


def test_fill_pinyin_skips_non_hanzi():
    doc = fill_pinyin(Document.from_text("你好abc"))
    assert [s.char for s in doc.syllables] == ["你", "好"]
    assert all(s.syllable for s in doc.syllables)


def test_fill_pinyin_with_jieba():
    jieba = pytest.importorskip("jieba")
    jieba.setLogLevel(logging.WARNING)
    tokenizer = jieba.Tokenizer()
    doc = fill_pinyin(Document.from_text("有一个人前来买瓜"), tokenizer)
    assert [s.char for s in doc.syllables] == list("有一个人前来买瓜")
    assert all(s.syllable for s in doc.syllables)


def test_fill_kana(tmp_path):
    path = tmp_path / "test.db"
    PinyinRepository.create(path, [
        PinyinEntry("ni", "033", "にい"),
        PinyinEntry("hao", "330", "'は/お"),
    ])
    doc = fill_pinyin(Document.from_text("你好"))
    with PinyinRepository.open(path, readonly=True) as repo:
        doc = fill_kana(doc, repo)
    assert [s.kana for s in doc.syllables] == ["にい", "'は/お"]


def test_fill_kana_missing_uses_default(tmp_path):
    path = tmp_path / "test.db"
    PinyinRepository.create(path, [PinyinEntry("ni", "033", "にい")])
    doc = fill_pinyin(Document.from_text("你好"))
    with PinyinRepository.open(path, readonly=True) as repo:
        doc = fill_kana(doc, repo, default="?")
    assert [s.kana for s in doc.syllables] == ["にい", "?"]


def test_fill_kana_multiple_runs(tmp_path):
    path = tmp_path / "test.db"
    PinyinRepository.create(path, [
        PinyinEntry("ni", "033", "K1"),
        PinyinEntry("hao", "330", "K2"),
        PinyinEntry("shi", "044", "K3"),
        PinyinEntry("jie", "440", "K4"),
    ])
    doc = fill_pinyin(Document.from_text("你好，世界"))
    with PinyinRepository.open(path, readonly=True) as repo:
        doc = fill_kana(doc, repo)
    assert [s.kana for s in doc.syllables] == ["K1", "K2", "K3", "K4"]


def test_fill_kana_length_mismatch():
    class ShortRepository:
        def get_many(self, keys):
            return []

    doc = fill_pinyin(Document.from_text("你好"))
    with pytest.raises(ValueError, match="批量查询结果数量不一致"):
        fill_kana(doc, ShortRepository())  # type: ignore[arg-type]


def test_fill_pinyin_length_mismatch(monkeypatch):
    import yukkurimandarin.pipeline.hanzi as module

    monkeypatch.setattr(module, "to_syllables", lambda words: [])
    with pytest.raises(ValueError, match="拼音数量与汉字数量不一致"):
        module.fill_pinyin(Document.from_text("你好"))
