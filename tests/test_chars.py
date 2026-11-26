import pytest

import yukkurimandarin.chars as t


@pytest.mark.parametrize("text, expected", [
    ("", False),
    ("一", True),
    ("汉字", True),
    ("汉a", False),
    ("abc", False),
    ("。", False),
    ("㐀", False),  # 扩展 A 区暂不视为汉字
])
def test_is_hanzi(text, expected):
    assert t.is_hanzi(text) is expected


@pytest.mark.parametrize("char, expected", [
    ("0", True),
    ("9", True),
    ("a", False),
    ("%", False),
    (" ", False),
    ("汉", False),
    ("あ", False),
    ("10", False),
    ("", False),
    ("１", False),
])
def test_is_digit(char, expected):
    assert t.is_digit(char) is expected


@pytest.mark.parametrize("chars, expected", [
    ("あをぁアヲァｱｦ", "gana"),
    ("azAZ", "latin"),
    ("!！,，、;；:：~-—…－·.｡。()（）[]【】「」『』?？", "punctuation"),
    ("Бβ一1", "others"),
])
def test_classify(chars, expected):
    for char in chars:
        assert t.classify(char) == expected


def test_classify_invalid():
    with pytest.raises(ValueError, match="输入必须是单个字符。"):
        t.classify("ab")
    with pytest.raises(ValueError):
        t.classify(1)  # type: ignore[arg-type]


@pytest.mark.parametrize("text, expected", [
    ("", ""),
    ("ヴ", "ゔ"),
    ("ｳﾞ", "ゔ"),
    ("コンニチハー", "こんにちはー"),
    ("ﾁｭｳｺﾞｸ", "ちゅうごく"),
    ("イナバテヰ", "いなばてゐ"),
    ("ABC１２３", "ABC１２３"),
])
def test_normalize_kana(text, expected):
    assert t.normalize_kana(text) == expected
