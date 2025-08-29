# 处理非汉字片段。

from typing import List, Union, Callable, Optional
import string
import unicodedata

from yukkurimandarin.settings import NonHanziModes


def non_hanzi_process(fragments: List[str], config: Optional[NonHanziModes] = None) -> List[str]:
    """
    处理非汉字片段

    Args:
        fragments: 非汉字片段
        config: 设置如何处理各类非汉字片段
        
    Returns:
        处理结果
    """
    if not fragments:
        return []
    if config is None: # 如果用户未定义处理模式设置，使用默认设置模式
        config = NonHanziModes(pc_mode=clean_punctuation, ja_mode=normalize_gana)
    result = []
    for fragment in fragments:
        if not fragment:
            result.append("")
            continue
        processed_fragment = []
        char_basket = [fragment[0]]
        basket_flag = classify(fragment[0])
        for char in fragment[1:]:
            current_flag = classify(char)
            if current_flag == basket_flag:
                char_basket.append(char)
            else:
                processed_fragment.append(convertor_handler("".join(char_basket),
                                                            basket_flag,                                                             
                                                            config))
                char_basket = [char]
                basket_flag = current_flag
        processed_fragment.append(convertor_handler("".join(char_basket),
                                                    basket_flag,                                                             
                                                    config))
        result.append("".join(processed_fragment))
    return result


def classify(char: str) -> str:
    """
    对非汉字字符进行分类。
    
    Args:
        char: 待判断的字符

    Returns:
        判断结果
        * `gana`: 平假名、片假名和半角片假名
        * `latin`: 26个英文字母（大小写）
        * `punctuation`: 常用中英文标点
        * `others`: 其他符号

    """
    if len(char) != 1:
        raise ValueError("输入必须是单个字符。")
    code = ord(char)
    if (0x3040 <= code <= 0x309F) or \
        (0x30A0 <= code <= 0x30FF) or \
        (0xFF65 <= code <= 0xFF9F):
        return "gana"
    if (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
        return "latin"
    if char in string.punctuation:
        return "punctuation"
    category = unicodedata.category(char)
    if category in {'Po', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Pc'}:
        return "punctuation"
    return "others"


def mode_handler(char: str, mode: Union[str, Callable[[str], str]], replace: str = "") -> str:
    """
    处理模式。

    Args:
        char: 输入的字符(串)
        mode: 处理模式

            - `ignore`: 忽略掉片段
            - `keep`: 保留片段
            - `replace`: 用自定义字符串代替片段
            - 可调用的函数：用于处理片段

        replace: 仅当mode为 `replace` 时此参数有效。将所有片段替换为该字符串。
        
    Returns:
        处理结果
    """
    # 忽略模式
    if mode == "ignore":
        return ""
    # 保留模式
    elif mode == "keep":
        return char
    # 替换模式
    elif mode == "replace":
        return replace
    # 函数处理
    elif callable(mode):
        return mode(char)
    else:
        raise ValueError("参数mode错误！请查看说明。")
    

def convertor_handler(fragment: str, type: str, config: NonHanziModes) -> str:
    """根据字符种类选择处理函数"""
    if type == "punctuation":
        return punctuation_convert(fragment, config.pc_mode, config.pc_replace)
    elif type == "gana":
        return gana_convert(fragment, config.ja_mode, config.ja_replace)
    elif type =="latin":
        return latin_convert(fragment, config.en_mode, config.en_replace)
    elif type == "others":
        return others_convert(fragment, config.other_mode, config.other_replace)
    else:
        raise ValueError("参数type错误，请查看说明。")


def punctuation_convert(fragment: str, mode: Union[str, Callable[[str], str]], replace: str) -> str:
    return mode_handler(fragment, mode, replace)


def clean_punctuation(fragment: str) -> str:
    """
    处理标点符号。仅保留字符串中的停顿符号（气口）。
    
    Args:
        fragment: 输入的字符串

    Returns:
        处理后的字符串
    """
    if not fragment:
        return ""
    # 常见标点符号
    normal_stop = ",，、;；:：~-—…－·"
    full_stop = ".｡。!！" # 小数点在预处理部分处理过了
    weak_stop = "()（）[]【】「」『』"
    question_mark = "?？"
    
    # 遍历字符串并替换标点
    result = []
    for char in fragment:
        if char in normal_stop:
            result.append("、")
        elif char in full_stop:
            result.append("。")
        elif char in weak_stop:
            result.append(",")
        elif char in question_mark:
            result.append("?")
        else:
            continue
    return "".join(result)


def gana_convert(fragment: str, mode: Union[str, Callable[[str], str]], replace: str) -> str:
    return mode_handler(fragment, mode, replace)


def normalize_gana(fragment: str) -> str:
    """
    将全角和半角片假名转换为平假名。
    
    Args:
        fragment: 输入的字符串

    Returns:
        处理后的字符串
    """
    if not fragment:
        return ""
    # 全角片假名
    full_width_katakana = ["ア", "イ", "ウ", "エ", "オ", "カ", "キ", "ク", "ケ", "コ", 
                           "サ", "シ", "ス", "セ", "ソ", "タ", "チ", "ツ", "テ", "ト",
                           "ナ", "ニ", "ヌ", "ネ", "ノ", "ハ", "ヒ", "フ", "ヘ", "ホ", 
                           "マ", "ミ", "ム", "メ", "モ", "ヤ", "ユ", "ヨ", "ラ", "リ", 
                           "ル", "レ", "ロ", "ワ", "ヲ", "ン", "ガ", "ギ", "グ", "ゲ", 
                           "ゴ", "ザ", "ジ", "ズ", "ゼ", "ゾ", "ダ", "ヂ", "ヅ", "デ", 
                           "ド", "バ", "ビ", "ブ", "ベ", "ボ", "パ", "ピ", "プ", "ペ", 
                           "ポ", "ー", "ァ", "ィ", "ゥ", "ェ", "ォ", "ャ", "ュ", "ョ", 
                           "ッ", "ヴ","ヰ", "ヱ"]
    # 半角片假名
    half_width_katakana = ["ｱ", "ｲ", "ｳ", "ｴ", "ｵ", "ｶ", "ｷ", "ｸ", "ｹ", "ｺ", "ｻ", 
                           "ｼ", "ｽ", "ｾ", "ｿ", "ﾀ", "ﾁ", "ﾂ", "ﾃ", "ﾄ", "ﾅ", "ﾆ", 
                           "ﾇ", "ﾈ", "ﾉ", "ﾊ", "ﾋ", "ﾌ", "ﾍ", "ﾎ", "ﾏ", "ﾐ", "ﾑ", 
                           "ﾒ", "ﾓ", "ﾔ", "ﾕ", "ﾖ", "ﾗ", "ﾘ", "ﾙ", "ﾚ", "ﾛ", "ﾜ", 
                           "ｦ", "ﾝ", "ｶﾞ", "ｷﾞ", "ｸﾞ", "ｹﾞ", "ｺﾞ", "ｻﾞ", "ｼﾞ", "ｽﾞ", 
                           "ｾﾞ", "ｿﾞ", "ﾀﾞ", "ﾁﾞ", "ﾂﾞ", "ﾃﾞ", "ﾄﾞ", "ﾊﾞ", "ﾋﾞ", "ﾌﾞ", 
                           "ﾍﾞ", "ﾎﾞ", "ﾊﾟ", "ﾋﾟ", "ﾌﾟ", "ﾍﾟ", "ﾎﾟ", "ｰ", "ｧ", "ｨ", 
                           "ｩ", "ｪ", "ｫ", "ｬ", "ｭ", "ｮ", "ｯ", "ｳﾞ"]
    hiragana = ["あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ", "さ", "し", 
                "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に","ぬ", "ね", 
                "の", "は", "ひ", "ふ", "へ", "ほ", "ま", "み", "む", "め", "も", "や",
                "ゆ", "よ", "ら", "り", "る", "れ", "ろ", "わ", "を", "ん", "が", "ぎ", 
                "ぐ", "げ", "ご", "ざ", "じ", "ず", "ぜ", "ぞ", "だ", "ぢ", "づ", "で", 
                "ど", "ば", "び", "ぶ", "べ", "ぼ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ", "ー", 
                "ぁ", "ぃ", "ぅ", "ぇ", "ぉ", "ゃ", "ゅ", "ょ", "っ", "ゔ", "ゐ", "ゑ"]
    # 转换映射
    conversion_map = {}
    for k, h in zip(full_width_katakana, hiragana):
        conversion_map[k] = h
    for k, h in zip(half_width_katakana, hiragana):
        conversion_map[k] = h
    result = []
    for i, char in enumerate(fragment):
        if char in "ﾟﾞ" and i > 0:
            char = f"{fragment[i-1]}{char}"
            result[-1] = conversion_map.get(char, char)
        else:
            result.append(conversion_map.get(char, char))
    return ''.join(result)


def latin_convert(fragment: str, mode: Union[str, Callable[[str], str]], replace: str) -> str:
    return mode_handler(fragment, mode, replace)


def others_convert(fragment: str, mode: Union[str, Callable[[str], str]], replace: str) -> str:
    return mode_handler(fragment, mode, replace)


# def more_func(fragment: str, mode: Union[str, Callable[[str], str]], replace: str) -> str:
# TODO: 添加更多处理函数：比如英文读音等。