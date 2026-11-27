import pytest

from yukkurimandarin.phonology import sandhi
from yukkurimandarin.pipeline.hanzi import fill_pinyin
from yukkurimandarin.segments import Document


def build(sentence):
    return fill_pinyin(Document.from_text(sentence))


def tones(document):
    return [syllable.tone for syllable in document.syllables]


@pytest.mark.parametrize("sentence, expected", [
    ("你好", [2, 3]),
    ("展览馆", [2, 2, 3]),
    ("小老虎", [2, 2, 3]),
    ("我很好", [2, 2, 3]),  # 已知限制：机械 2+1 分组
    ("粉笔", [2, 3]),
])
def test_third_tone(sentence, expected):
    assert tones(sandhi.apply_third_tone(build(sentence))) == expected


@pytest.mark.parametrize("sentence, expected", [
    ("不对", [2, 4]),
    ("不好", [4, 3]),
    ("不要", [2, 4]),
    ("差不多", [4, 5, 1]),  # 轻声的“不”保持不变
    ("不不", [4, 4]),  # 连续否定保持原调
    ("对不起", [4, 4, 3]),
    ("不", [4]),
])
def test_bu(sentence, expected):
    assert tones(sandhi.apply_bu(build(sentence))) == expected


@pytest.mark.parametrize("sentence, expected", [
    ("一天", [4, 1]),
    ("一样", [2, 4]),
    ("一起", [4, 3]),
    ("一个", [2, 4]),
    ("第一", [4, 1]),
    ("十一", [2, 1]),
    ("一九九八", [1, 3, 3, 1]),
    ("一百一十", [4, 3, 1, 2]),
    ("一千一百一十一", [4, 1, 1, 3, 1, 2, 1]),
    ("看一看", [4, 5, 4]),
    ("想一想", [3, 5, 3]),
    ("一下子", [2, 4, 5]),
    ("一会儿", [2, 4, 5]),
    ("一万", [2, 4]),
    ("一楼", [4, 2]),  # 默认按数量词处理
    ("一五一十", [1, 3, 1, 2]),
    ("一步一步", [2, 4, 2, 4]),
    ("一年一年", [4, 2, 4, 2]),
    ("一个一个", [2, 4, 2, 4]),
    ("一百一百", [4, 3, 4, 3]),
])
def test_yi(sentence, expected):
    assert tones(sandhi.apply_yi(build(sentence))) == expected


def test_bu_yi_combination():
    assert tones(sandhi.apply(build("不一般"))) == [4, 4, 1]


def test_boundaries_break_sandhi():
    doc = build("你，好")
    assert tones(sandhi.apply_third_tone(doc)) == [3, 3]


def test_apply_combines_rules():
    doc = build("一天，不对。")
    assert tones(sandhi.apply(doc)) == [4, 1, 2, 4]
