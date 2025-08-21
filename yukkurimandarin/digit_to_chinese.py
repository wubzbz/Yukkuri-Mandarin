# 将阿拉伯数字转换为汉字。

# 数字映射表
NUMBER_MAP = {"0": "零", "1": "一", "2": "二", "3": "三", "4": "四", "5": "五",
              "6": "六", "7": "七", "8": "八", "9": "九", ".": "点"}

UNIT_MAP = ["", "十", "百", "千"]

def digit_to_chinese(number: str) -> str:
    if not number:
        return ""
    # 百分数
    if number.endswith("%"):
        return f"百分之{digit_to_chinese(number[:-1])}"
    # 以空格结尾、以0开头采用简读法
    if number.endswith(" ") or number.startswith("0"):
        return fractional_read(number)
    # 有小数部分
    if "." in number:
        integer_part, fractional_part = number.split(".", 1)
        return f"{integral_read(integer_part)}点{fractional_read(fractional_part)}"
    # 普通整数长度超过13位或只有一位都可以用简读法
    if len(number) > 13 or len(number) == 1:
        return fractional_read(number)
    # 普通整数长度不超过13位
    else:
        return integral_read(number)


def fractional_read(digit: str) -> str:
    """
    将任意整数阿拉伯数字字符串转换为中文数字简读法。
    """
    return "".join(NUMBER_MAP.get(d, d) for d in digit.strip())


def integral_read(digit: str) -> str:
    """
    将任意整数阿拉伯数字字符串转换为中文数字繁读法。
    """
    digit_reversed = digit[::-1]
    result = ""
    for idx, d in enumerate(digit_reversed):
        # 分级单位
        if idx == 4 or idx == 12:
            result = f"万{result}"
        if idx == 8:
            # 特殊：万级全为0
            if result[0] == "万":
                result = f"{result[1:]}"
            result = f"亿{result}"
        # 尾部无意义的零不出现，各节连续的0只保留一个“零”
        if d == "0":
            result = f"{NUMBER_MAP[d]}{result}" if result and result[0] not in "零万亿" else result
        else:
            result = f"{NUMBER_MAP[d]}{UNIT_MAP[idx%4]}{result}"
    # 10~19读“十x”而不是“一十x”
    if result[:2] == "一十":
        result = result[1:]
    return result