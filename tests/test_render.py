import pytest

from yukkurimandarin.tablegen import render as t
from yukkurimandarin.tablegen.table import valid_tones


def test_syllables():
    syllables = t.syllables()
    assert len(syllables) == 415
    assert syllables[0] == "a"
    assert syllables[-1] == "zuo"
    assert len(set(syllables)) == len(syllables)


def test_invalid_yinjie_type():
    with pytest.raises(ValueError, match="参数类型错误！必须是字符串。"):
        t.render_hiragana(1, "010")  # type: ignore[arg-type]


@pytest.mark.parametrize("yinjie", ["", "wubzbz"])
def test_nonexistent_yinjie(yinjie):
    assert t.render_hiragana(yinjie, "010") == ""


@pytest.mark.parametrize("tone", ["", "0", "1234"])
def test_invalid_tone_length(tone):
    with pytest.raises(ValueError, match=f"声调必须是3位数字组成的字符串: {tone}."):
        t.render_hiragana("a", tone)


@pytest.mark.parametrize("tone", ["abc", "103", "126"])
def test_invalid_tone_format(tone):
    with pytest.raises(ValueError, match=f"声调格式错误: {tone}."):
        t.render_hiragana("a", tone)


@pytest.mark.parametrize("tone", valid_tones())
def test_without_accent(tone):
    hiragana = t.render_hiragana("a", tone, without_accent=True)
    assert hiragana == "ああ"
    assert "'" not in hiragana
    assert "/" not in hiragana


@pytest.mark.parametrize("yinjie, tone, expected", [
    ("a", "151", "ああ"),
    ("a", "051", "/っああ"),
    ("a", "121", "/ああ"),
    ("a", "141", "あ/あ"),
    ("ni", "131", "'に/い"),
    ("ni", "133", "'にい"),
    ("ni", "430", "にい"),
    ("ni", "431", "に/い"),
    ("ni", "142", "に'い"),
    ("ni", "144", "に/い"),
])
def test_known_renderings(yinjie, tone, expected):
    assert t.render_hiragana(yinjie, tone) == expected
