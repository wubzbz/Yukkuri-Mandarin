"""领域对象。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PinyinEntry:
    """一条拼音数据。

    不变量：
        - ``yinjie`` 为非空音节（不含声调），如 "ni"；
        - ``tone`` 为三位声调序列，字符取自 0–5，且中间位不为 0；
        - ``hiragana`` 为对应的假名拟音，可含音声记号。
    """

    yinjie: str
    tone: str
    hiragana: str
