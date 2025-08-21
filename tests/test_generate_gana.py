import pytest

import yukkurimandarin.generate_gana as t
from yukkurimandarin.generate_table import generate_valid_numbers


def test_invalid_yinjie():
    with pytest.raises(ValueError, match="参数类型错误！必须是字符串。"):
        t.generate_hiragana(1, "010") # type: ignore


@pytest.mark.parametrize("input, expected", [
    ("", ""),
    ("wubzbz", "")
])
def test_nonexistent_yinjie(input, expected):
    assert t.generate_hiragana(input, "010") == expected


@pytest.mark.parametrize("input", [
    "",
    "0",
    "1234"
])
def test_invalid_tone_1(input):
    with pytest.raises(ValueError, match=f"声调必须是3位数字组成的字符串: {input}."):
        t.generate_hiragana("a", input)


@pytest.mark.parametrize("input", [
    "abc",
    "103",
    "126"
])
def test_invalid_tone_2(input):
    with pytest.raises(ValueError, match=f"声调格式错误: {input}."):
        t.generate_hiragana("a", input)


@pytest.mark.parametrize("input", generate_valid_numbers())
def test_without_accent(input):
    hiragana = t.generate_hiragana("a", input, True)
    assert hiragana
    assert "\'" not in hiragana
    assert "/" not in hiragana

