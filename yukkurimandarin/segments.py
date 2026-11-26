"""文本切分与音节轨道。

用区间（fence）表示片段边界，避免把文本拆成大量子串；
用与汉字一一对应的 `Syllable` 承载「汉字 / 拼音 / 假名」三大序列。

术语：
    run      连续同类字符构成的片段，只记录 `text` 中的区间
    syllable 一个汉字对应的音节记录，与汉字字符严格一一对应

不变量（构造时校验）：
    - runs 首尾相接，覆盖整个 text；
    - 非汉字 run 的 syl_start == syl_end；
    - 汉字 run 满足 end - start == syl_end - syl_start；
    - syllables 的总长度等于所有汉字 run 的长度之和。
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal, Sequence

from .chars import classify, is_hanzi

Kind = Literal["hanzi", "gana", "latin", "punctuation", "others"]


@dataclass(frozen=True)
class Run:
    """文本中的一个连续同类片段，用区间表示。"""

    kind: Kind
    start: int  # 在 text 中的起始下标（含）
    end: int  # 在 text 中的结束下标（不含）
    syl_start: int  # 在 syllables 中的起始下标（含），非汉字片段两者相等
    syl_end: int  # 在 syllables 中的结束下标（不含）

    @property
    def length(self) -> int:
        """片段包含的字符数。"""
        return self.end - self.start


@dataclass(frozen=True)
class Syllable:
    """一个汉字的音节记录，包含拼音、声调与假名。"""

    char: str  # 汉字本身，如 "一"
    syllable: str = ""  # 不带声调的拼音，如 "yi"；未填充时为空串
    tone: int = 0  # 0–5，5 表示轻声；0 表示尚未填充
    kana: str = ""  # 数据库查得的假名拟音；未填充时为空串


@dataclass(frozen=True)
class Document:
    """切分后的文本及其音节轨道。"""

    text: str  # 预处理后的原文
    runs: tuple[Run, ...]
    syllables: tuple[Syllable, ...]

    def __post_init__(self) -> None:
        _validate(self)

    @classmethod
    def from_text(cls, text: str) -> Document:
        """扫描文本，按字符类别生成 runs，并为汉字建立占位音节。

        Args:
            text: 预处理后的文本。

        Returns:
            音节尚未填充（syllable 为空、tone 为 0）的 Document。

        Raises:
            ValueError: text 不是字符串，或生成的 runs/syllables 不满足不变量。
        """
        if not isinstance(text, str):
            raise ValueError(f"参数text必须是字符串: {text}")
        if not text:
            return cls(text, (), ())

        runs: list[Run] = []
        syllables: list[Syllable] = []
        run_start = 0
        run_kind = _kind_of(text[0])
        syl_start = 0
        for index, char in enumerate(text):
            kind = _kind_of(char)
            if kind != run_kind:
                runs.append(Run(run_kind, run_start, index, syl_start, len(syllables)))
                run_start = index
                run_kind = kind
                syl_start = len(syllables)
            if kind == "hanzi":
                syllables.append(Syllable(char))
        runs.append(Run(run_kind, run_start, len(text), syl_start, len(syllables)))
        return cls(text, tuple(runs), tuple(syllables))

    def run_text(self, run: Run) -> str:
        """返回片段对应的原文子串。"""
        return self.text[run.start:run.end]

    def run_syllables(self, run: Run) -> tuple[Syllable, ...]:
        """返回片段内的音节记录；非汉字片段返回空元组。"""
        return self.syllables[run.syl_start:run.syl_end]

    def with_syllables(self, syllables: Sequence[Syllable]) -> Document:
        """替换音节轨道，返回新的 Document。

        Args:
            syllables: 新的音节序列，长度与对应汉字必须与当前一致。

        Returns:
            音节已更新的新 Document（其余字段不变）。

        Raises:
            ValueError: 长度不一致，或汉字字符被改动。
        """
        new_syllables = tuple(syllables)
        if len(new_syllables) != len(self.syllables):
            raise ValueError(
                f"音节数量不一致：期望 {len(self.syllables)}，实际 {len(new_syllables)}。"
            )
        for old, new in zip(self.syllables, new_syllables):
            if old.char != new.char:
                raise ValueError(f"音节对应的汉字不能改变：{old.char} -> {new.char}。")
        return replace(self, syllables=new_syllables)

    def join(self, parts: Sequence[str]) -> str:
        """把各片段的输出按顺序拼接为最终字符串。

        Args:
            parts: 与 runs 一一对应的片段输出。

        Returns:
            拼接结果，等价于 ``"".join(parts)``。

        Raises:
            ValueError: parts 的数量与 runs 不一致。
        """
        if len(parts) != len(self.runs):
            raise ValueError(
                f"片段输出数量与片段数不一致：期望 {len(self.runs)}，实际 {len(parts)}。"
            )
        return "".join(parts)


def _kind_of(char: str) -> Kind:
    """返回单个字符所属的片段类别。"""
    if is_hanzi(char):
        return "hanzi"
    return classify(char)


def _validate(doc: Document) -> None:
    """校验 Document 的不变量，不满足时抛 ValueError。"""
    if not doc.runs:
        if doc.text or doc.syllables:
            raise ValueError("空片段列表与非空文本或音节不一致。")
        return

    text_cursor = 0
    syl_cursor = 0
    for run in doc.runs:
        _validate_run(run, text_cursor, syl_cursor, len(doc.text))
        text_cursor = run.end
        syl_cursor = run.syl_end
    _validate_totals(doc, text_cursor, syl_cursor)


def _validate_run(run: Run, text_cursor: int, syl_cursor: int, text_length: int) -> None:
    """校验单个片段与累计游标是否衔接。"""
    if run.start != text_cursor:
        raise ValueError(f"片段区间不连续：期望起点 {text_cursor}，实际 {run.start}。")
    if run.end <= run.start or run.end > text_length:
        raise ValueError(f"片段区间非法：[{run.start}, {run.end})。")
    if run.syl_start != syl_cursor or run.syl_end < run.syl_start:
        raise ValueError(f"音节区间非法：[{run.syl_start}, {run.syl_end})。")
    if run.kind == "hanzi":
        if run.syl_end - run.syl_start != run.end - run.start:
            raise ValueError("汉字片段长度与音节数不一致。")
    elif run.syl_start != run.syl_end:
        raise ValueError("非汉字片段不应包含音节。")


def _validate_totals(doc: Document, text_cursor: int, syl_cursor: int) -> None:
    """校验片段是否覆盖整个文本与全部音节。"""
    if text_cursor != len(doc.text):
        raise ValueError(f"片段未覆盖整个文本：末尾为 {text_cursor}，文本长度为 {len(doc.text)}。")
    if syl_cursor != len(doc.syllables):
        raise ValueError(f"音节总数与片段不一致：{syl_cursor} != {len(doc.syllables)}。")
