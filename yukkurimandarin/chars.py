"""字符识别、分类与规范化。"""

from __future__ import annotations

import re
import string
import unicodedata
from typing import Literal

# classify() 的返回值
CharType = Literal["gana", "latin", "punctuation", "others"]

# CJK 统一表意文字基本区
_HANZI_RE = re.compile(r"[\u4e00-\u9fff]+")

# 半角片假名（不含半角标点 ｡｢｣､･）
_HALF_WIDTH_KANA_RE = re.compile(r"[\uff66-\uff9f]+")

# 全角片假名 → 平假名，码位相差 0x60
_KATAKANA_TO_HIRAGANA = {
    chr(code): chr(code - 0x60) for code in range(0x30A1, 0x30F7)
}


def is_hanzi(text: str) -> bool:
    """判断字符串是否全部由汉字组成。

    Args:
        text: 待判断的字符串。

    Returns:
        空字符串、或含任意非汉字字符时返回 False，否则返回 True。

    Note:
        目前只覆盖 CJK 统一表意文字基本区（U+4E00–U+9FFF）；
        扩展 A 区（U+3400 起）、扩展 B 区及以后（U+20000 起）暂不视为汉字。
    """
    return _HANZI_RE.fullmatch(text) is not None


def is_digit(char: str) -> bool:
    """判断字符是否为阿拉伯数字。

    Args:
        char: 单个字符。

    Returns:
        仅当 char 是 "0"–"9" 之一时返回 True；空字符串或多字符返回 False。
    """
    return len(char) == 1 and "0" <= char <= "9"


def classify(char: str) -> CharType:
    """对非汉字字符分类。

    Args:
        char: 单个字符。

    Returns:
        分类结果：

        - ``"gana"``：平假名、片假名、半角片假名
        - ``"latin"``：26 个英文字母（大小写均归此类）
        - ``"punctuation"``：ASCII 标点，以及 Unicode 类别为
          Po / Pd / Ps / Pe / Pi / Pf / Pc 的字符
        - ``"others"``：以上都不是

    Raises:
        ValueError: char 不是单个字符。
    """
    if not isinstance(char, str) or len(char) != 1:
        raise ValueError("输入必须是单个字符。")
    code = ord(char)
    if (
        0x3040 <= code <= 0x309F  # 平假名
        or 0x30A0 <= code <= 0x30FF  # 片假名
        or 0xFF65 <= code <= 0xFF9F  # 半角片假名与半角标点
    ):
        return "gana"
    if 0x0041 <= code <= 0x005A or 0x0061 <= code <= 0x007A:
        return "latin"
    if char in string.punctuation:
        return "punctuation"
    if unicodedata.category(char) in {"Po", "Pd", "Ps", "Pe", "Pi", "Pf", "Pc"}:
        return "punctuation"
    return "others"


def normalize_kana(text: str) -> str:
    """把全角、半角片假名转换为对应的平假名。

    用于两处：处理输入里已有的日文假名；以及去掉音声记号后，把为
    无声化而故意写成片假名的字符转回平假名（如 ``で_ス`` → ``です``）。

    半角片假名先经 NFKC 归一化成全角（这样 ``ｶﾞ`` 会自动合成 ``ガ``），
    再按码位映射为平假名；其余字符原样保留。

    Args:
        text: 任意文本。

    Returns:
        转换后的文本；非假名字符原样保留。
    """
    normalized = _HALF_WIDTH_KANA_RE.sub(
        lambda match: unicodedata.normalize("NFKC", match.group()),
        text,
    )
    return "".join(_KATAKANA_TO_HIRAGANA.get(char, char) for char in normalized)
