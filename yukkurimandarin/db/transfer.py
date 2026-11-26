"""表格文件与 :class:`PinyinEntry` 之间的转换。

按文件后缀自动分派：``.csv`` 与 ``.xlsx``。
CSV 使用 UTF-8 with BOM，方便 Excel 直接打开；xlsx 依赖可选的 openpyxl，
在真正读写时才导入。
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable, List, Union

from .errors import MissingDependencyError, TransferError
from .models import PinyinEntry

#: 表格文件的表头，顺序与 PinyinEntry 字段一致
CSV_HEADERS = ("拼音", "声调", "平假名")

#: 读取时也接受“音节”作为第一列名（旧文档两种叫法都出现过）
_ACCEPTED_HEADERS = {
    CSV_HEADERS,
    ("音节", "声调", "平假名"),
}


def read_table(path: Union[str, Path]) -> List[PinyinEntry]:
    """读取表格文件。

    Args:
        path: ``.csv`` 或 ``.xlsx`` 文件路径。

    Returns:
        文件中的全部记录。

    Raises:
        TransferError: 后缀不支持、表头不匹配或内容格式错误。
        MissingDependencyError: 读取 .xlsx 但未安装 openpyxl。
        FileNotFoundError: 文件不存在。
    """
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"文件不存在：{target}")
    suffix = target.suffix.lower()
    if suffix == ".csv":
        return _read_csv(target)
    if suffix == ".xlsx":
        return _read_xlsx(target)
    raise TransferError(f"不支持的文件类型：{target.suffix!r}，仅支持 .csv / .xlsx。")


def write_table(entries: Iterable[PinyinEntry], path: Union[str, Path]) -> int:
    """写出表格文件。

    Args:
        entries: 要写出的记录；可为迭代器，便于流式导出。
        path: ``.csv`` 或 ``.xlsx`` 文件路径。

    Returns:
        写出的数据行数（不含表头）。

    Raises:
        TransferError: 后缀不支持。
        MissingDependencyError: 写出 .xlsx 但未安装 openpyxl。
    """
    target = Path(path)
    suffix = target.suffix.lower()
    if suffix == ".csv":
        return _write_csv(entries, target)
    if suffix == ".xlsx":
        return _write_xlsx(entries, target)
    raise TransferError(f"不支持的文件类型：{target.suffix!r}，仅支持 .csv / .xlsx。")


def _read_csv(path: Path) -> List[PinyinEntry]:
    """读取 CSV 文件。"""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        _check_header(next(reader, None))
        entries: List[PinyinEntry] = []
        for line_no, row in enumerate(reader, 2):
            if not row or all(not cell.strip() for cell in row):
                continue
            entries.append(_make_entry(row, line_no))
        return entries


def _write_csv(entries: Iterable[PinyinEntry], path: Path) -> int:
    """写出 CSV 文件。"""
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADERS)
        count = 0
        for entry in entries:
            writer.writerow([entry.yinjie, entry.tone, entry.hiragana])
            count += 1
    return count


def _read_xlsx(path: Path) -> List[PinyinEntry]:
    """读取 xlsx 文件，仅在调用时导入 openpyxl。"""
    openpyxl = _load_openpyxl()
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = workbook.active.iter_rows(values_only=True)
        _check_header(next(rows, None))
        entries: List[PinyinEntry] = []
        for line_no, row in enumerate(rows, 2):
            cells = ["" if cell is None else str(cell) for cell in row or ()]
            while cells and not cells[-1]:
                cells.pop()
            if not cells:
                continue
            entries.append(_make_entry(cells, line_no))
        return entries
    finally:
        workbook.close()


def _write_xlsx(entries: Iterable[PinyinEntry], path: Path) -> int:
    """写出 xlsx 文件，仅在调用时导入 openpyxl。"""
    openpyxl = _load_openpyxl()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(list(CSV_HEADERS))
    count = 0
    for entry in entries:
        sheet.append([entry.yinjie, entry.tone, entry.hiragana])
        count += 1
    workbook.save(path)
    return count


def _load_openpyxl() -> Any:
    """导入可选的 openpyxl，缺失时给出明确异常。"""
    try:
        import openpyxl
    except ImportError as exc:
        raise MissingDependencyError(
            "未安装 openpyxl，请执行 pip install openpyxl 后再读写 xlsx。"
        ) from exc
    return openpyxl


def _check_header(header: object) -> None:
    """校验表头。"""
    actual = tuple(header or ())
    if actual not in _ACCEPTED_HEADERS:
        raise TransferError(f"表头不匹配：期望 {CSV_HEADERS}，实际 {actual}。")


def _make_entry(cells: List[str], line_no: int) -> PinyinEntry:
    """把一行单元格转换为记录。"""
    if len(cells) != len(CSV_HEADERS):
        raise TransferError(f"第 {line_no} 行列数不正确：{cells!r}。")
    yinjie, tone, hiragana = (cell.strip() for cell in cells)
    if not yinjie or not tone:
        raise TransferError(f"第 {line_no} 行缺少音节或声调。")
    return PinyinEntry(yinjie, tone, hiragana)
