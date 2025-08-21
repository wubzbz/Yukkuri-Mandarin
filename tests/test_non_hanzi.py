import pytest

from yukkurimandarin.settings import NonHanziModes
import yukkurimandarin.non_hanzi_process as t


@pytest.mark.parametrize("input, expected", [
    ("あをぁアヲァｱｦ", "gana"),
    ("azAZ", "latin"),
    ("!！,，、;；:：~-—…－·.｡。()（）[]【】「」『』?？", "punctuation"),
    ("Бβ一1", "others")
])
def test_classify(input, expected):
    for char in input:
        assert t.classify(char) == expected


@pytest.mark.parametrize("input, expected", [
    ("ignore", ""),
    ("keep", "char"),
    ("replace", "w"),
    (lambda c: c.upper(), "CHAR")
])
def test_mode_handler(input, expected):
    assert t.mode_handler("char", input, "w") == expected


@pytest.mark.parametrize("input, expected", [
    ("ignore", ""),
    ("keep", "！。（？#,.】?@"),
    ("replace", "w"),
    (t.clean_punctuation, "、。,?、。,?")
])
def test_punctuation_convert(input, expected):
    assert t.punctuation_convert("！。（？#,.】?@", input, "w") == expected


@pytest.mark.parametrize("input, expected, mode", [
    ([], [], "default"),
    ([""], [""], "default"),
    (["モデル&", "@しての", "、readme", "ください。", ") "], 
     ["", "", "、", "。", ","], "default"),
    (["モデル&", "@しての", "、readme", "ください。", ") "], 
     ["モデル&", "@しての", "、readme", "ください。", ") "], "keep"),
    (["モデル&", "@しての"], ["", ""], "ignore"),
    (["モデル&", "@しての"], ["ww", "ww"], "replace"), # TODO: 全局替换模式与部分替换模式
])
def test_non_hanzi_process(input, expected, mode):
    if mode == "default":
        config = None
    else:
        config = NonHanziModes(mode, "w")
    assert t.non_hanzi_process(input, config) == expected


def test_invalid_mode():
    with pytest.raises(ValueError, match="参数mode错误！请查看说明。"):
        config = NonHanziModes("error")
        t.non_hanzi_process(["111"], config)