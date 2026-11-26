"""声调变调规则（纯函数）。

变调是逆行的：前字的调值由后字决定。所有规则只在汉字片段内部生效，
片段边界视为停顿，与旧的 ``/0`` 标记等价。变调只修改 ``Syllable.tone``，
不改变拼音、假名等其他字段。

注意：pypinyin 的词组表已经对部分词做了变调（如“一个”“一起”“不对”），
所以规则必须按后字的声调**无条件重写**，不能只在“当前是原调”时才改；
这些规则本身是幂等的。
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..segments import Document, Syllable

# 数字语境：出现这些字符说明“一”处在数字/序数里
_NUMERAL_ALL = frozenset("零一二三四五六七八九十百千万亿")
# 直接修饰这些单位时，“一”是数字的首位，仍按普通规则变调
_LEADING_UNITS = frozenset("百千万亿")


def apply(doc: Document) -> Document:
    """依次应用全部变调规则，返回新的 Document。

    顺序：连读上声 → “不” → “一”。“不”先于“一”，因为“不”看的是
    “一”的本调（阴平），而不是“一”变调后的调值。
    """
    return apply_yi(apply_bu(apply_third_tone(doc)))


def apply_third_tone(doc: Document) -> Document:
    """连读上声变调：上声（3）在另一个上声前变阳平（2）。

    采用简化的两字组 / 三字组处理：连续上声按 2+1、1+2 的切分方式变调，
    与旧实现保持一致。
    """
    updated = list(doc.syllables)
    for run in doc.runs:
        if run.kind != "hanzi":
            continue
        tones = [syllable.tone for syllable in updated[run.syl_start:run.syl_end]]
        _third_tone(tones)
        _write_tones(updated, run.syl_start, tones)
    return doc.with_syllables(updated)


def apply_bu(doc: Document) -> Document:
    """“不”的变调：去声（4）在去声前变阳平（2），其余场合保持去声。

    片段末尾的“不”保持去声（相当于词句末尾）；轻声的“不”（如“差不多”）
    保持轻声；“不不”这样的连续否定保持原调。
    """
    updated = list(doc.syllables)
    for run in doc.runs:
        if run.kind != "hanzi":
            continue
        start, end = run.syl_start, run.syl_end
        chars = [updated[index].char for index in range(start, end)]
        tones = [updated[index].tone for index in range(start, end)]
        for index, char in enumerate(chars):
            if char != "不" or tones[index] == 5:
                continue
            if index + 1 < len(chars) and chars[index + 1] == "不":
                continue
            tones[index] = 2 if index + 1 < len(chars) and tones[index + 1] == 4 else 4
        _write_tones(updated, start, tones)
    return doc.with_syllables(updated)


def apply_yi(doc: Document) -> Document:
    """“一”的变调：去声前变阳平（2），阴平 / 阳平 / 上声前变去声（4）。

    片段末尾的“一”保持阴平（相当于词句末尾）。数字串与多位数按惯例处理：
    只有直接修饰百 / 千 / 万 / 亿的“一”参与变调，其余位置的“一”读阴平
    （如“一九九八”“一百一十”）。重叠动词中间的“一”读轻声（如“看一看”）。

    Note:
        序数（如“一楼”读第一层楼）与数量（读全楼）的歧义无法只靠字面判断，
        这里默认按数量词处理；“一楼”因此读去声。
    """
    updated = list(doc.syllables)
    for run in doc.runs:
        if run.kind != "hanzi":
            continue
        start, end = run.syl_start, run.syl_end
        chars = [updated[index].char for index in range(start, end)]
        tones = [updated[index].tone for index in range(start, end)]
        for index, char in enumerate(chars):
            if char != "一" or tones[index] == 5:
                continue
            tones[index] = _yi_tone(chars, tones, index)
        _write_tones(updated, start, tones)
    return doc.with_syllables(updated)


def _third_tone(tones: list[int]) -> None:
    """在单个汉字片段内就地应用连读上声规则。"""
    flag = 0
    for index in range(len(tones) - 1):
        if tones[index] == 3 and tones[index + 1] == 3:
            if flag == 0:
                flag = 1
            elif flag == 1:
                flag = 2
            else:
                tones[index - 1] = 3
                flag = 1
            tones[index] = 2
        else:
            flag = 0


def _yi_tone(chars: list[str], tones: list[int], index: int) -> int:
    """计算单个“一”的调值。"""
    previous = chars[index - 1] if index > 0 else ""
    following = chars[index + 1] if index + 1 < len(chars) else ""

    # 看一看、想一想：重叠动词中间读轻声
    if previous and previous == following and previous != "一":
        return 5
    # 多位数中非首位的“一”读阴平
    if previous in _NUMERAL_ALL:
        return 1
    # 数字首位直接修饰百 / 千 / 万 / 亿时仍按普通规则变调
    if following in _LEADING_UNITS:
        return 2 if tones[index + 1] == 4 else 4
    # 数字串、以及“一十”之类：读阴平
    if following in _NUMERAL_ALL:
        return 1
    # 片段末尾
    if not following:
        return 1
    return 2 if tones[index + 1] == 4 else 4


def _write_tones(syllables: list[Syllable], start: int, tones: list[int]) -> None:
    """把新的调值写回音节列表，只替换发生变化的项。"""
    for offset, tone in enumerate(tones):
        index = start + offset
        if syllables[index].tone != tone:
            syllables[index] = replace(syllables[index], tone=tone)
