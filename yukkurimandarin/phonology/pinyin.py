"""拼音获取与声调序列构造。

本模块只依赖 pypinyin，不涉及分词、数据库或假名；
分词（jieba）由 pipeline 层负责，便于单独测试音系规则。
"""

from __future__ import annotations

from typing import Sequence

from pypinyin import Style, pinyin

# 数据库查询用的 (音节, 三位声调序列)
Serial = tuple[str, str]

_TONE_CHARS = frozenset("012345")


def to_syllables(words: Sequence[str]) -> list[tuple[str, int]]:
    """把已分词的汉字序列转换为 (不带声调的拼音, 声调) 序列。

    Args:
        words: 已分词的汉字片段，如 ``["油库里", "普通话"]``。
            未启用分词时传入只含整段文本的单元素序列。

    Returns:
        逐字展开、与汉字总数等长的序列；声调用 1–5 表示（5 = 轻声）。

    Raises:
        ValueError: pypinyin 返回的拼音缺少声调数字（通常意味着混入了非汉字）。
    """
    entries = pinyin(list(words), style=Style.TONE3, neutral_tone_with_five=True)
    return [split_tone(entry[0]) for entry in entries]


def split_tone(pinyin: str) -> tuple[str, int]:
    """拆分带数字声调的拼音。

    Args:
        pinyin: TONE3 风格的拼音，如 ``"yi1"``、``"ma5"``。

    Returns:
        ``(不带声调的拼音, 声调)``。

    Raises:
        ValueError: pinyin 末尾不是 0–5 的声调数字。
    """
    if not pinyin or pinyin[-1] not in _TONE_CHARS:
        raise ValueError(f"拼音缺少声调数字：{pinyin!r}。")
    return pinyin[:-1], int(pinyin[-1])


def build_serial(syllables: Sequence[tuple[str, int]]) -> list[Serial]:
    """构造数据库查询用的 (音节, 三位声调序列)。

    三位序列为「前字调 + 本字调 + 后字调」；首字的前调与末字的后调记为 0，
    对应旧的片段边界标记。

    Args:
        syllables: 同一连续片段内的 (拼音, 声调) 序列。

    Returns:
        与输入等长的 Serial 列表。
    """
    if not syllables:
        return []
    tones = [tone for _, tone in syllables]
    serial: list[Serial] = []
    for index, (syllable, tone) in enumerate(syllables):
        previous = tones[index - 1] if index > 0 else 0
        following = tones[index + 1] if index + 1 < len(tones) else 0
        serial.append((syllable, f"{previous}{tone}{following}"))
    return serial
