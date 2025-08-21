# 预处理输入的文本。

from yukkurimandarin.digit_to_chinese import digit_to_chinese


def pre_process(sentence: str) -> str:
    """
    预处理输入的句子

    将阿拉伯数字和一些符号转换为汉字。
    
    Args:
        sentence: 输入的句子
    
    Returns:
        预处理后的句子
    """
    # 初始化变量
    result = []
    num_basket = []
    for next_idx, char in enumerate(sentence, 1):
        # 处理数字
        if is_num(char):
            num_basket.append(char)
        # 处理非数字
        else:
            # 可读符号
            char = SYMBOL.get(char, char)
            # 之前是数字
            if num_basket:
                # 数字末尾的空格或百分号
                if char == " " or char == "%":
                    num_basket.append(char)
                    result.append(digit_to_chinese("".join(num_basket)))
                    num_basket.clear()
                # 小数点且小数点后是数字（同时防止索引超范围）
                elif char == "." and next_idx < len(sentence) and is_num(sentence[next_idx]):
                    num_basket.append(char)
                # 不是数字
                else:
                    result.append(digit_to_chinese("".join(num_basket)))
                    num_basket.clear()
                    result.append(char)
            # 之前不是数字
            else:
                result.append(char)
    # 处理遗留数字
    if num_basket:
        result.append(digit_to_chinese("".join(num_basket)))
    return "".join(result)


def is_num(char: str) -> bool:
    """判断字符是否属于阿拉伯数字"""
    if char and len(char) == 1:
        return ord("0") <= ord(char) <= ord("9")
    else:
        return False


# 可读符号转换映射字典
SYMBOL = {
    "+": "加",
    "=": "等于",
    "#": "井"
    }
