import pytest

from yukkurimandarin.pipeline.assemble import assemble
from yukkurimandarin.pipeline.non_hanzi import clean_punctuation, convert_run
from yukkurimandarin.segments import Document
from yukkurimandarin.settings import NonHanziModes


def test_clean_punctuation():
    assert clean_punctuation("！。（？#,.】?@") == "。。,?、。,?"


def test_default_punctuation():
    assert convert_run("！。（？#,.】?@", "punctuation") == "。。,?、。,?"


def test_default_gana():
    assert convert_run("コンニチハー", "gana") == "こんにちはー"


def test_default_latin_ignored():
    assert convert_run("abc", "latin") == ""


@pytest.mark.parametrize("mode, expected", [
    ("ignore", ""),
    ("keep", "abc"),
    ("replace", "w"),
    (lambda text: text.upper(), "ABC"),
])
def test_modes(mode, expected):
    config = NonHanziModes(global_mode=mode, global_replace="w")
    assert convert_run("abc", "latin", config) == expected


def test_invalid_mode():
    config = NonHanziModes(global_mode="error")
    with pytest.raises(ValueError, match="非汉字处理模式错误"):
        convert_run("abc", "latin", config)


def test_assemble_default():
    doc = Document.from_text("モデル&@しての、readmeください。) ")
    assert assemble(doc) == "もでるしての、ください。,"


def test_assemble_keep():
    doc = Document.from_text("モデル&、readme")
    config = NonHanziModes(global_mode="keep")
    assert assemble(doc, config) == "モデル&、readme"
