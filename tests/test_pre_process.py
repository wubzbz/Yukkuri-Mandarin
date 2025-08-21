import pytest

import yukkurimandarin.pre_process as t


@pytest.mark.parametrize("input, expected", [
    # 有效阿拉伯数字
    ("0", True),
    ("1", True),
    ("5", True),
    ("9", True),
    # 非阿拉伯数字
    ("a", False),
    ("%", False),
    (" ", False),
    ("汉", False),
    ("あ", False),
    ("10", False),  # 多字符
    ("", False)
])
def test_is_num(input, expected):
    assert t.is_num(input) == expected


@pytest.mark.parametrize("input, expected", [
    # 空
    ("", ""),
    # 纯数字
    ("01234", "零一二三四"),
    ("1234", "一千二百三十四"),
    ("1234 ", "一二三四"),
    # 百分数与小数
    ("12.34%", "百分之十二点三四"),
    ("12.34%%", "百分之十二点三四%"),
    ("12..34", "十二..三十四"),
    ("1234.", "一千二百三十四."),
    ("%12 .03", "%一二.零三"),
    # 可读符号
    ("2+3=5", "二加三等于五"),
    # 混合
    ("#0729:我在2025 年基于python3.13.5开发了这个包，测试100%通过后发布1.0.版本.666",
     "井零七二九:我在二零二五年基于python三点一三点五开发了这个包，测试百分之一百通过后发布一点零.版本.六百六十六"),
    ("1去23 里，烟村45 家。亭台67 座，89 10枝花。", "一去二三里，烟村四五家。亭台六七座，八九十枝花。")
])
def test_pre_process(input, expected):
    assert t.pre_process(input) == expected