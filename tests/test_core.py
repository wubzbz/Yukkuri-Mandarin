import pytest

import yukkurimandarin.core as t


@pytest.mark.parametrize("input, expected", [
    ("", ([], [], False)),
    ("油库里普通话ゆっくりしていってね", (["油库里普通话"], ["ゆっくりしていってね"], False)),
    #("", ([], [], True)),
    ("", ([], [], False)),
    #("", ([], [], True)),
])
def test_divide(input, expected):
    assert t.divide(input) == expected


@pytest.mark.parametrize("input, expected", [
    ((["A", "C"], ["B", "D"], False), "ABCD"),
    ((["B", "D"], ["A", "C"], True), "ABCD"),
    ((["B"], ["A", "C"], False), "ABC"),
    ((["A", "C"], ["B"], True), "ABC"),
])
def test_combine(input, expected):
    res_hanzi, res_non_hanzi, last_type = input
    assert t.combine(res_hanzi, res_non_hanzi, last_type) == expected


def test_text_convert():
    invalid_input = 2
    with pytest.raises(ValueError, match=f"参数sentence必须是字符串: {invalid_input}"):
        t.text_convert(invalid_input) # type: ignore
    empty_input = ""
    assert t.text_convert(empty_input) == empty_input