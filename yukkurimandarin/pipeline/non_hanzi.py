"""非汉字段处理：按字符类别与配置转换。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union, Callable

from ..chars import normalize_kana

if TYPE_CHECKING:
    from ..chars import CharType
    from ..settings import NonHanziModes

_DEFAULT_CONFIG: Optional["NonHanziModes"] = None


def convert_run(
    text: str, kind: "CharType", config: Optional["NonHanziModes"] = None
) -> str:
    """按类别与配置转换一个非汉字片段。

    Args:
        text: 片段原文。
        kind: 片段类别（gana / latin / punctuation / others）。
        config: 非汉字处理模式；为 None 时使用默认配置。

    Returns:
        转换后的文本。

    Raises:
        ValueError: 处理模式不合法。
    """
    if config is None:
        config = default_config()
    if kind == "punctuation":
        mode, replace = config.pc
        return _apply_mode(text, mode, replace)
    if kind == "gana":
        mode, replace = config.ja
        return _apply_mode(text, mode, replace)
    if kind == "latin":
        mode, replace = config.en
        return _apply_mode(text, mode, replace)
    mode, replace = config.other
    return _apply_mode(text, mode, replace)


def default_config() -> "NonHanziModes":
    """返回非汉字处理的默认配置（模块内缓存）。"""
    global _DEFAULT_CONFIG
    if _DEFAULT_CONFIG is None:
        from ..settings import NonHanziModes

        _DEFAULT_CONFIG = NonHanziModes(
            pc_mode=clean_punctuation, ja_mode=normalize_kana
        )
    return _DEFAULT_CONFIG


def clean_punctuation(fragment: str) -> str:
    """只保留停顿类标点，并统一成中文全角形式。

    Args:
        fragment: 标点片段。

    Returns:
        转换后的标点；非停顿标点会被丢弃。
    """
    normal_stop = ",，、;；:：~-—…－·"
    full_stop = ".｡。!！"
    weak_stop = "()（）[]【】「」『』"
    question_mark = "?？"
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
    return "".join(result)


def _apply_mode(
    text: str, mode: Union[str, Callable[[str], str]], replace_text: str
) -> str:
    """按处理模式转换文本。"""
    if mode == "ignore":
        return ""
    if mode == "keep":
        return text
    if mode == "replace":
        return replace_text
    if callable(mode):
        return mode(text)
    raise ValueError(f"非汉字处理模式错误：{mode!r}。")
