"""控制台表格格式化。

纯展示层：只把记录渲染成字符串，不打印、不访问数据库。
"""

from __future__ import annotations

import unicodedata
from typing import Sequence

from .models import PinyinEntry

_HEADERS = ("音节", "声调", "平假名")
_GAP = "  "


def format_table(entries: Sequence[PinyinEntry]) -> str:
    """把记录渲染成对齐的文本表格。

    Args:
        entries: 要展示的记录。

    Returns:
        可直接 ``print`` 的字符串；全宽字符按两列宽度计算。
    """
    rows = [[entry.yinjie, entry.tone, entry.hiragana] for entry in entries]
    widths = [
        max([_display_width(header)] + [_display_width(row[column]) for row in rows])
        for column, header in enumerate(_HEADERS)
    ]
    lines = [_format_row(_HEADERS, widths), _GAP.join("-" * width for width in widths)]
    lines.extend(_format_row(row, widths) for row in rows)
    return "\n".join(lines)


def _format_row(cells: Sequence[str], widths: Sequence[int]) -> str:
    """按列宽拼出一行。"""
    return _GAP.join(_pad(cell, width) for cell, width in zip(cells, widths)).rstrip()


def _pad(text: str, width: int) -> str:
    """用空格补齐到指定显示宽度。"""
    return text + " " * (width - _display_width(text))


def _display_width(text: str) -> int:
    """计算字符串的显示宽度，全宽字符计为 2。"""
    return sum(2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in text)
