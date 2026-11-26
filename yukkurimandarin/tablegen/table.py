"""从规则生成完整音节表（构建工具）。

这里生成的是**候选表**，用于从零构建数据库或补齐缺失项。
随包发行的数据库可能经过人工调整，直接整表导入会覆盖这些调整；
需要保留已有改动时，应只增量导入缺失的行。
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterator, List, Optional, Tuple, Union

from ..errors import MissingDependencyError
from ..formats import CSV_HEADERS
from .render import render_hiragana, syllables

_DEFAULT_CSV = "gr_yinjie_table.csv"
_DEFAULT_XLSX = "gr_yinjie_table.xlsx"

# 三位声调：首位与末位可为 0，中间位不能为 0
_VALID_TONES = tuple(
    f"{first}{middle}{last}"
    for first in "012345"
    for middle in "12345"
    for last in "012345"
)


def valid_tones() -> List[str]:
    """返回全部合法声调组合。

    Returns:
        三位声调序列的列表，字符取自 0–5，且中间位不为 0。
    """
    return list(_VALID_TONES)


def iter_rows() -> Iterator[Tuple[str, str, str]]:
    """按规则逐行生成 ``(音节, 声调, 假名)``。

    惰性生成，便于直接流式写入表格文件。
    """
    for yinjie in syllables():
        for tone in _VALID_TONES:
            yield yinjie, tone, render_hiragana(yinjie, tone)


def fill_csv(file_path: Optional[Union[str, Path]] = None) -> int:
    """把规则生成的完整音节表写入 CSV。

    Args:
        file_path: 目标路径；None 时写入当前目录的 ``gr_yinjie_table.csv``。

    Returns:
        写出的数据行数（不含表头）。
    """
    target = _resolve(file_path, _DEFAULT_CSV, ".csv")
    count = 0
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADERS)
        for row in iter_rows():
            writer.writerow(row)
            count += 1
    return count


def fill_xlsx(file_path: Optional[Union[str, Path]] = None) -> int:
    """把规则生成的完整音节表写入 xlsx。

    Args:
        file_path: 目标路径；None 时写入当前目录的 ``gr_yinjie_table.xlsx``。

    Returns:
        写出的数据行数（不含表头）。

    Raises:
        MissingDependencyError: 未安装 openpyxl。
    """
    openpyxl = _load_openpyxl()
    target = _resolve(file_path, _DEFAULT_XLSX, ".xlsx")
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(list(CSV_HEADERS))
    count = 0
    for row in iter_rows():
        sheet.append(list(row))
        count += 1
    workbook.save(target)
    return count


def _resolve(file_path: Optional[Union[str, Path]], default: str, suffix: str) -> Path:
    """确定输出路径，并补齐正确的后缀。"""
    target = Path(file_path) if file_path is not None else Path(default)
    if target.suffix.lower() != suffix:
        target = target.with_suffix(suffix)
    return target


def _load_openpyxl() -> Any:
    """导入可选的 openpyxl，缺失时给出明确异常。"""
    try:
        import openpyxl
    except ImportError as exc:
        raise MissingDependencyError(
            "未安装 openpyxl，请执行 pip install openpyxl 后再导出 xlsx。"
        ) from exc
    return openpyxl
