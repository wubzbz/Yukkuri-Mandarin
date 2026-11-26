"""配置对象。

`Config` 是不可变的值对象；运行时资源（数据库连接、分词器）由
`api.Converter` 持有，不放进配置里。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Union

# 处理模式：字符串（ignore / keep / replace）或自定义函数
Mode = Union[str, Callable[[str], str]]


@dataclass(frozen=True)
class NonHanziModes:
    """设置如何处理各类非汉字字符。

    细分类别未指定时，回落到 ``global_mode`` / ``global_replace``。

    Args:
        global_mode: 默认处理模式，见各类别的 ``*_mode``。
        global_replace: 默认替换文本。
        en_mode: 英文字母的处理模式。
        ja_mode: 日文假名的处理模式。
        pc_mode: 标点符号的处理模式。
        other_mode: 其他字符的处理模式。

    模式取值：

        - ``"ignore"``：忽略该片段
        - ``"keep"``：保留原样
        - ``"replace"``：替换为对应的 ``*_replace``
        - 可调用对象：以片段为参数，返回替换文本
    """

    global_mode: Mode = "ignore"
    global_replace: str = ""
    en_mode: Optional[Mode] = None
    en_replace: Optional[str] = None
    ja_mode: Optional[Mode] = None
    ja_replace: Optional[str] = None
    pc_mode: Optional[Mode] = None
    pc_replace: Optional[str] = None
    other_mode: Optional[Mode] = None
    other_replace: Optional[str] = None

    def __post_init__(self) -> None:
        """把未指定的细分类别回落到全局设置。"""
        for prefix in ("en", "ja", "pc", "other"):
            mode_attr = f"{prefix}_mode"
            replace_attr = f"{prefix}_replace"
            if getattr(self, mode_attr) is None:
                object.__setattr__(self, mode_attr, self.global_mode)
            if getattr(self, replace_attr) is None:
                object.__setattr__(self, replace_attr, self.global_replace)


@dataclass(frozen=True)
class Config:
    """转换配置。

    Args:
        non_hanzi: 非汉字片段的处理方式；None 表示使用库的默认处理
            （清洗标点、归一化假名，其余类别忽略）。
        database: 拼音数据库路径；None 表示随包分发的内置只读库。
    """

    non_hanzi: Optional[NonHanziModes] = None
    database: Optional[Union[str, Path]] = None


#: 默认配置，可直接使用或用 dataclasses.replace() 派生
DEFAULT_CONFIG = Config()
