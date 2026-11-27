"""按规则生成假名映射表。

运行时不用这里的规则，一律查数据库；这里生成的是候选表，
随包发行的数据库可能包含人工修改，未必与生成结果一致。
"""

from __future__ import annotations

from .render import render_hiragana, syllables
from .table import fill_csv, fill_xlsx, iter_rows, valid_tones

__all__ = [
    "fill_csv",
    "fill_xlsx",
    "iter_rows",
    "render_hiragana",
    "syllables",
    "valid_tones",
]
