from typing import Union, Tuple, List
from jieba import Tokenizer

from yukkurimandarin.pre_process import pre_process
from yukkurimandarin.hanzi_process import hanzi_process
from yukkurimandarin.non_hanzi_process import non_hanzi_process
from yukkurimandarin.settings import NonHanziModes


def text_convert(sentence: str, 
                 tokenizer: Union[Tokenizer, None] = None, 
                 non_hanzi_config: Union[NonHanziModes, None] = None) -> str:
    """
    将中文句子中的汉字转换为伪日本语，非汉字字符保持原样
    
    Args:
        sentence: 输入的句子
        tokenizer: jiaba分词器
        non_hanzi_config: 非汉字处理模式
    
    Returns:
        转换后的句子
    """
    # 参数类型检查
    if not isinstance(sentence, str):
        raise ValueError(f"参数sentence必须是字符串: {sentence}")
    # 空字符串检查
    if not sentence:
        return ""
    # 预处理
    sentence = pre_process(sentence)
    # 切分
    hanzi, non_hanzi, last_type = divide(sentence)
    # 分别处理汉字片段和非汉字片段
    res_hanzi = hanzi_process(hanzi, tokenizer)
    res_non_hanzi = non_hanzi_process(non_hanzi, non_hanzi_config)
    # 还原
    result = combine(res_hanzi, res_non_hanzi, last_type)
    return result


def divide(sentence: str) -> Tuple[List[str], List[str], bool]:
    """
    将输入的句子切分为汉字片段和非汉字片段

    Args:
        sentence: 输入的句子

    Returns:
        (hanzi, non_hanzi, last_type): 汉字片段、非汉字片段，以及最后一个片段的类型
    """
    # 初始化变量
    hanzi: List[str] = []
    non_hanzi: List[str] = []
    word_basket = []
    basket_type = is_hanzi(sentence[0])
    # 遍历句子
    for char in sentence:
        # 当前字符类型
        current_type = is_hanzi(char)

        if current_type == basket_type:
            # 加入字篮
            word_basket.append(char)
        else:
            # 处理字篮
            if basket_type:
                hanzi.append("".join(word_basket))
            else:
                non_hanzi.append("".join(word_basket))
            # 初始化下一个字篮
            word_basket = [char]
            basket_type = current_type
    # 处理最后一个字篮
    if basket_type:
        hanzi.append("".join(word_basket))
    else:
        non_hanzi.append("".join(word_basket))
    return (hanzi, non_hanzi, basket_type)


def combine(res_hanzi: List[str], res_non_hanzi: List[str], last_type: bool) -> str:
    """
    将处理后的汉字片段与非汉字片段重新合并为句子

    Args:
        res_hanzi: 处理后的汉字片段
        res_non_hanzi: 处理后的非汉字片段
        last_type: 最后一个片段的类型
    
    Returns:
        合并后的句子
    """
    len_hanzi = len(res_hanzi)
    len_non_hanzi = len(res_non_hanzi)
    result = []
    # 偶数型
    if len_hanzi == len_non_hanzi:
        # NHNH
        if last_type:
            for i in range(0, len_hanzi):
                result.append(res_non_hanzi[i])
                result.append(res_hanzi[i])
        # HNHN
        else:
            for i in range(0, len_hanzi):
                result.append(res_hanzi[i])
                result.append(res_non_hanzi[i])
    # HNH
    elif len_hanzi - len_non_hanzi == 1:
        for i in range(0, len_non_hanzi):
            result.append(res_hanzi[i])
            result.append(res_non_hanzi[i])
        result.append(res_hanzi[-1])
    # NHN
    elif len_non_hanzi - len_hanzi == 1:
        for i in range(0, len_hanzi):
            result.append(res_non_hanzi[i])
            result.append(res_hanzi[i])
        result.append(res_non_hanzi[-1])
    else:
        raise ValueError("转换过程出错")
    
    return "".join(result)


def is_hanzi(fragment: str) -> bool:
    """判断字符串是否为汉字"""
    if not fragment:
        return False
    for char in fragment:
        # 基本汉字范围
        if not 0x4E00 <= ord(char) <= 0x9FFF:
            return False
    return True
