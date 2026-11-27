import pytest

from yukkurimandarin.phonology.pinyin import build_serial, split_tone, to_syllables


@pytest.mark.parametrize("words, expected", [
    ([], []),
    (["你好"], [("ni", 3), ("hao", 3)]),
    (["一个"], [("yi", 2), ("ge", 4)]),
    (["银行", "重庆"], [("yin", 2), ("hang", 2), ("chong", 2), ("qing", 4)]),
    (["嗯"], [("n", 2)]),
    (["衣", "裳"], [("yi", 1), ("shang", 5)]),
])
def test_to_syllables(words, expected):
    assert to_syllables(words) == expected


def test_to_syllables_rejects_non_hanzi():
    with pytest.raises(ValueError):
        to_syllables(["abc"])


@pytest.mark.parametrize("pinyin, expected", [
    ("ni1", ("ni", 1)),
    ("ma5", ("ma", 5)),
    ("bu4", ("bu", 4)),
])
def test_split_tone(pinyin, expected):
    assert split_tone(pinyin) == expected


@pytest.mark.parametrize("pinyin", ["ni", "", "ni6"])
def test_split_tone_invalid(pinyin):
    with pytest.raises(ValueError):
        split_tone(pinyin)


@pytest.mark.parametrize("syllables, expected", [
    ([], []),
    ([("a", 1)], [("a", "010")]),
    ([("ni", 3), ("hao", 3)], [("ni", "033"), ("hao", "330")]),
    ([("yi", 2), ("ge", 5)], [("yi", "025"), ("ge", "250")]),
])
def test_build_serial(syllables, expected):
    assert build_serial(syllables) == expected
