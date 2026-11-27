import dataclasses

import pytest

from yukkurimandarin.segments import Document, Run, Syllable


def test_empty_document():
    doc = Document.from_text("")
    assert doc.runs == ()
    assert doc.syllables == ()


@pytest.mark.parametrize("text, kinds, texts", [
    ("你好", ["hanzi"], ["你好"]),
    ("abc", ["latin"], ["abc"]),
    ("あアｱ", ["gana"], ["あアｱ"]),
    ("123", ["others"], ["123"]),
    ("你好，world！", ["hanzi", "punctuation", "latin", "punctuation"],
     ["你好", "，", "world", "！"]),
    ("一，二。", ["hanzi", "punctuation", "hanzi", "punctuation"],
     ["一", "，", "二", "。"]),
])
def test_from_text_runs(text, kinds, texts):
    doc = Document.from_text(text)
    assert [run.kind for run in doc.runs] == kinds
    assert [doc.run_text(run) for run in doc.runs] == texts
    assert "".join(doc.run_text(run) for run in doc.runs) == text


def test_syllables_only_for_hanzi():
    doc = Document.from_text("你好，世界")
    assert [syllable.char for syllable in doc.syllables] == list("你好世界")
    hanzi_runs = [run for run in doc.runs if run.kind == "hanzi"]
    assert len(hanzi_runs) == 2
    assert doc.run_syllables(hanzi_runs[0]) == (Syllable("你"), Syllable("好"))
    assert doc.run_syllables(doc.runs[1]) == ()


def test_with_syllables():
    doc = Document.from_text("你好")
    filled = doc.with_syllables(
        [dataclasses.replace(syllable, kana="X") for syllable in doc.syllables]
    )
    assert [syllable.kana for syllable in filled.syllables] == ["X", "X"]
    assert [syllable.kana for syllable in doc.syllables] == ["", ""]


def test_with_syllables_rejects_wrong_length():
    doc = Document.from_text("你好")
    with pytest.raises(ValueError, match="音节数量不一致"):
        doc.with_syllables(doc.syllables[:1])


def test_with_syllables_rejects_char_change():
    doc = Document.from_text("你好")
    changed = [dataclasses.replace(doc.syllables[0], char="好"), doc.syllables[1]]
    with pytest.raises(ValueError, match="汉字不能改变"):
        doc.with_syllables(changed)


def test_join():
    doc = Document.from_text("你好，世界")
    parts = ["A", "B", "C"]
    assert doc.join(parts) == "ABC"


def test_join_rejects_wrong_count():
    doc = Document.from_text("你好，世界")
    with pytest.raises(ValueError, match="片段输出数量与片段数不一致"):
        doc.join(["A"])


def test_invalid_document():
    with pytest.raises(ValueError):
        Document("x", (), ())


def test_from_text_rejects_non_str():
    with pytest.raises(ValueError, match="参数text必须是字符串"):
        Document.from_text(None)  # type: ignore[arg-type]


def test_invalid_run_layouts():
    with pytest.raises(ValueError):
        Document("ab", (Run("latin", 0, 1, 0, 0),), ())
    with pytest.raises(ValueError):
        Document("abc", (Run("latin", 0, 1, 0, 0), Run("latin", 2, 3, 0, 0)), ())
    with pytest.raises(ValueError):
        Document("a", (Run("latin", 0, 2, 0, 0),), ())
    with pytest.raises(ValueError):
        Document("a", (Run("hanzi", 0, 1, 0, 0),), ())
    with pytest.raises(ValueError):
        Document("a", (Run("latin", 0, 1, 0, 1),), (Syllable("a"),))
    with pytest.raises(ValueError):
        Document("a", (Run("latin", 0, 1, 0, 0),), (Syllable("a"),))
