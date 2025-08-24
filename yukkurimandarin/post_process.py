# 在结果输出前进行的处理。

from yukkurimandarin.non_hanzi_process import normalize_gana


def post_process(sentence: str, without_accent: bool) -> str:
    """
    处理输出前的句子

    Args:
        sentence: 输入的句子
        without_accent: 是否去除音声记号
    
    Returns:
        后处理后的句子
    """
    if not without_accent:
        return sentence
    # 音声记号
    accent_symbols = "\'/_"
    result_list = []
    for char in sentence:
        if char in accent_symbols:
            continue
        result_list.append(char)
    result =  "".join(result_list)
    result = normalize_gana(result)
    return result