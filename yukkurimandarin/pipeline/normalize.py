"""输入归一化：阿拉伯数字与符号转换为汉字。"""

from __future__ import annotations

from ..chars import is_digit

# 数字映射表
_NUMBER_MAP = {
    "0": "零", "1": "一", "2": "二", "3": "三", "4": "四",
    "5": "五", "6": "六", "7": "七", "8": "八", "9": "九",
    ".": "点",
}

# 个、十、百、千
_UNIT_MAP = ("", "十", "百", "千")

# 可读符号
_SYMBOLS = {"+": "加", "=": "等于", "#": "井"}

# 数字串允许出现的字符
_VALID_CHARS = frozenset("0123456789.% ")


def normalize_text(sentence: str) -> str:
    """把输入中的阿拉伯数字和可读符号转换为汉字。

    Args:
        sentence: 原始输入。

    Returns:
        归一化后的文本；数字按中文读法展开，例如 "123" → "一百二十三"。
    """
    result: list[str] = []
    digits: list[str] = []
    for index, char in enumerate(sentence, 1):
        if is_digit(char):
            digits.append(char)
            continue
        char = _SYMBOLS.get(char, char)
        if not digits:
            result.append(char)
            continue
        # 数字末尾的空格或百分号属于数字的一部分
        if char in {" ", "%"}:
            digits.append(char)
            result.append(digit_to_chinese("".join(digits)))
            digits.clear()
        # 小数点，且后面紧跟数字
        elif char == "." and index < len(sentence) and is_digit(sentence[index]):
            digits.append(char)
        else:
            result.append(digit_to_chinese("".join(digits)))
            digits.clear()
            result.append(char)
    if digits:
        result.append(digit_to_chinese("".join(digits)))
    return "".join(result)


def digit_to_chinese(number: str) -> str:
    """把一段阿拉伯数字转换为中文读法。

    Args:
        number: 数字串，可包含小数点、末尾空格或百分号。

    Returns:
        对应的中文读法。

    Raises:
        ValueError: number 不是合法的数字串。
    """
    if not number:
        return ""
    if not set(number) <= _VALID_CHARS:
        raise ValueError(f"不是合法的数字串：{number!r}。")
    # 百分数
    if number.endswith("%"):
        return f"百分之{digit_to_chinese(number[:-1])}"
    # 以空格结尾或以 0 开头时采用简读法
    if number.endswith(" ") or number.startswith("0"):
        return _fractional_read(number)
    # 有小数部分
    if "." in number:
        integer_part, fractional_part = number.split(".", 1)
        return f"{_integral_read(integer_part)}点{_fractional_read(fractional_part)}"
    # 超过 13 位或只有一位，用简读法
    if len(number) > 13 or len(number) == 1:
        return _fractional_read(number)
    return _integral_read(number)


def _fractional_read(digits: str) -> str:
    """逐位简读，用于小数、编号、超长数字。"""
    return "".join(_NUMBER_MAP.get(char, char) for char in digits.strip())


def _integral_read(digits: str) -> str:
    """按十进制位值繁读整数。"""
    result = ""
    for index, char in enumerate(reversed(digits)):
        # 分级单位
        if index == 4 or index == 12:
            result = f"万{result}"
        if index == 8:
            # 万级全为 0 时不留“万”
            if result[:1] == "万":
                result = result[1:]
            result = f"亿{result}"
        # 尾部无意义的零不出现，各节连续的零只保留一个
        if char == "0":
            if result and result[0] not in "零万亿":
                result = f"零{result}"
        else:
            result = f"{_NUMBER_MAP[char]}{_UNIT_MAP[index % 4]}{result}"
    # 10~19 读“十x”而不是“一十x”
    if result[:2] == "一十":
        result = result[1:]
    return result
