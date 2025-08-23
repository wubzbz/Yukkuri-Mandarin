import pytest

import yukkurimandarin.core as t


@pytest.mark.parametrize("input, expected", [
    ("", ([], [], False)),
    ("油库里普通话ゆっくりしていってね", (["油库里普通话"], ["ゆっくりしていってね"], False)),
    ("max-heap 中父节点值始终大于等于子节点值，min-heap 则相反", 
     (["中父节点值始终大于等于子节点值", "则相反"], ["max-heap ", "，min-heap "], True)),
    ("严格讲起来，他们不该叫哲学家philosophers，该叫‘哲学家学家’philophilosophers。", 
     (["严格讲起来", "他们不该叫哲学家", "该叫", "哲学家学家"], 
      ["，", "philosophers，", "‘", "’philophilosophers。"], False)),
    ("星座的主星之所以不一定是α星，是因为德国天文学家约翰・拜耳\n在以希腊字母为星座中的星星命名时，并非严格依据亮度排序", 
     (["星座的主星之所以不一定是", "星", "是因为德国天文学家约翰", "拜耳", "在以希腊字母为星座中的星星命名时", "并非严格依据亮度排序"], 
      ["α", "，", "・", "\n", "，"], True)),
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