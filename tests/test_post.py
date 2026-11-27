import pytest

import yukkurimandarin.pipeline.post as t


@pytest.mark.parametrize("text, expected", [
    ("'ゆっく/り_シていってね。", "ゆっくりしていってね。"),
    ("で_ス", "です"),
    ("あ'め", "あめ"),
    ("", ""),
])
def test_finalize_without_accent(text, expected):
    assert t.finalize(text, without_accent=True) == expected


@pytest.mark.parametrize("text", [
    "'ゆっく/り_シていってね。",
    "abc",
    "",
])
def test_finalize_keeps_text(text):
    assert t.finalize(text, without_accent=False) == text
