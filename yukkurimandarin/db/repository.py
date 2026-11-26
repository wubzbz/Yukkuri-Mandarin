"""拼音数据仓储：唯一直接执行 SQL 的模块。

仓储只负责数据存取，不打印、不读文件、不做参数提示；
缺项、失败等情况通过返回值或异常交给调用方处理。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Union

from .connection import BUNDLED_DB_PATH, open_connection
from .errors import ReadOnlyDatabaseError
from .models import PinyinEntry

# SQLite 的变量上限约为 999，每行占 3 个参数
_CHUNK_SIZE = 250

_SELECT_ALL = "SELECT yinjie, tone, hiragana FROM pinyin_data"

_UPSERT_SQL = (
    "INSERT INTO pinyin_data (yinjie, tone, hiragana) VALUES (?, ?, ?) "
    "ON CONFLICT(yinjie, tone) DO UPDATE SET hiragana = excluded.hiragana"
)


class PinyinRepository:
    """拼音数据仓储。

    仓储持有一个连接，既能查询也能写入；它本身是上下文管理器：

        with PinyinRepository.open() as repo:
            entries = repo.list_by_yinjie("ni")
    """

    def __init__(self, conn: sqlite3.Connection, *, readonly: bool = False) -> None:
        """在已打开的连接上构造仓储。

        Args:
            conn: 由 :func:`yukkurimandarin.db.connection.connect` 打开、
                且已完成迁移的连接。
            readonly: 连接是否为只读；只读仓储拒绝写入。
        """
        self._conn = conn
        self._readonly = readonly

    @classmethod
    def open(
        cls,
        path: Optional[Union[str, Path]] = None,
        *,
        readonly: bool = False,
        create: bool = False,
    ) -> "PinyinRepository":
        """打开数据库并返回仓储。

        Args:
            path: 数据库路径；None 表示随包分发的内置库（强制只读）。
            readonly: 是否只读打开。
            create: 文件不存在时是否允许新建。

        Returns:
            仓储对象；应配合 ``with`` 使用，以保证连接被关闭。
        """
        if readonly or path is None:
            readonly = True
        elif Path(path).resolve() == BUNDLED_DB_PATH.resolve():
            readonly = True
        return cls(
            open_connection(path, readonly=readonly, create=create),
            readonly=readonly,
        )

    @classmethod
    def create(
        cls,
        path: Union[str, Path],
        entries: Iterable[PinyinEntry],
        *,
        overwrite: bool = False,
    ) -> None:
        """新建数据库文件并写入全部记录。

        Args:
            path: 目标路径。
            entries: 全部记录。
            overwrite: 目标已存在时是否覆盖。

        Raises:
            FileExistsError: 目标已存在且 overwrite 为 False。
            ReadOnlyDatabaseError: 目标是随包分发的内置数据库。
        """
        target = Path(path)
        if target.resolve() == BUNDLED_DB_PATH.resolve():
            raise ReadOnlyDatabaseError(
                "内置数据库是只读资源，不能覆盖；请指定其他路径。"
            )
        if target.exists():
            if not overwrite:
                raise FileExistsError(f"数据库已存在：{target}")
            target.unlink()
        conn = open_connection(target, create=True)
        try:
            repo = cls(conn)
            repo.upsert_many(entries)
        finally:
            conn.close()

    def close(self) -> None:
        """关闭底层连接。"""
        self._conn.close()

    def _ensure_writable(self) -> None:
        """只读仓储拒绝写入。"""
        if self._readonly:
            raise ReadOnlyDatabaseError("数据库以只读方式打开，不能写入。")

    def __enter__(self) -> "PinyinRepository":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def get(self, yinjie: str, tone: str) -> Optional[PinyinEntry]:
        """精确查询单条记录。

        Returns:
            命中的记录；不存在时为 None。
        """
        row = self._conn.execute(
            f"{_SELECT_ALL} WHERE yinjie = ? AND tone = ?", (yinjie, tone)
        ).fetchone()
        return None if row is None else _row_to_entry(row)

    def get_many(self, keys: Sequence[tuple[str, str]]) -> List[Optional[PinyinEntry]]:
        """批量精确查询。

        Args:
            keys: ``(yinjie, tone)`` 序列。

        Returns:
            与 keys 等长、顺序一致的列表；未命中的位置为 None。
        """
        if not keys:
            return []
        result: List[Optional[PinyinEntry]] = []
        for chunk in _chunks(list(keys), _CHUNK_SIZE):
            result.extend(self._get_chunk(chunk))
        return result

    def _get_chunk(self, chunk: List[tuple[str, str]]) -> List[Optional[PinyinEntry]]:
        """查询一个分块，返回与 chunk 等长的结果。"""
        placeholders = ",".join("(?,?,?)" for _ in chunk)
        params: List[object] = []
        for offset, (yinjie, tone) in enumerate(chunk):
            params.extend([offset, yinjie, tone])
        sql = (
            f"WITH input(ord, yinjie, tone) AS (VALUES {placeholders}) "
            "SELECT input.ord AS ord, p.yinjie AS yinjie, p.tone AS tone, "
            "p.hiragana AS hiragana "
            "FROM input LEFT JOIN pinyin_data AS p "
            "ON p.yinjie = input.yinjie AND p.tone = input.tone "
            "ORDER BY input.ord"
        )
        chunk_result: List[Optional[PinyinEntry]] = [None] * len(chunk)
        for row in self._conn.execute(sql, params):
            if row["hiragana"] is not None:
                chunk_result[row["ord"]] = _row_to_entry(row)
        return chunk_result

    def search(self, yinjie: str, tone: Optional[str] = None) -> List[PinyinEntry]:
        """按音节与声调模式查询。

        Args:
            yinjie: 音节。
            tone: 三位声调模式，``*`` 表示通配（如 ``"1*3"``）；
                None 表示不限声调。

        Returns:
            命中的记录，按声调升序排列。

        Raises:
            ValueError: tone 不是合法的三位模式。
        """
        if tone is None:
            rows = self._conn.execute(
                f"{_SELECT_ALL} WHERE yinjie = ? ORDER BY tone", (yinjie,)
            )
        else:
            _validate_tone_pattern(tone)
            rows = self._conn.execute(
                f"{_SELECT_ALL} WHERE yinjie = ? AND tone GLOB ? ORDER BY tone",
                (yinjie, tone.replace("*", "?")),
            )
        return [_row_to_entry(row) for row in rows]

    def list_by_yinjie(self, yinjie: str) -> List[PinyinEntry]:
        """查询某个音节的全部记录，按声调升序排列。"""
        return self.search(yinjie)

    def iter_all(self) -> Iterator[PinyinEntry]:
        """流式遍历全部记录，适合导出大表。"""
        for row in self._conn.execute(f"{_SELECT_ALL} ORDER BY yinjie, tone"):
            yield _row_to_entry(row)

    def upsert(self, entry: PinyinEntry) -> None:
        """插入或覆盖单条记录。"""
        self._ensure_writable()
        _validate_entry(entry)
        with self._conn:
            self._conn.execute(
                _UPSERT_SQL, (entry.yinjie, entry.tone, entry.hiragana)
            )

    def upsert_many(self, entries: Iterable[PinyinEntry]) -> int:
        """批量插入或覆盖，单事务完成。

        Returns:
            写入的行数。
        """
        self._ensure_writable()
        rows = [(entry.yinjie, entry.tone, entry.hiragana) for entry in _validated(entries)]
        if not rows:
            return 0
        with self._conn:
            self._conn.executemany(_UPSERT_SQL, rows)
        return len(rows)

    def replace_all(self, entries: Iterable[PinyinEntry]) -> int:
        """清空后写入全部记录，用于整库重建。

        Returns:
            写入的行数。
        """
        self._ensure_writable()
        rows = [(entry.yinjie, entry.tone, entry.hiragana) for entry in _validated(entries)]
        with self._conn:
            self._conn.execute("DELETE FROM pinyin_data")
            if rows:
                self._conn.executemany(_UPSERT_SQL, rows)
        return len(rows)

    def delete(self, yinjie: str, tone: str) -> bool:
        """删除单条记录。

        Returns:
            是否真的删掉了记录。
        """
        self._ensure_writable()
        with self._conn:
            cursor = self._conn.execute(
                "DELETE FROM pinyin_data WHERE yinjie = ? AND tone = ?", (yinjie, tone)
            )
        return cursor.rowcount > 0

    def delete_by_yinjie(self, yinjie: str) -> int:
        """删除某个音节的全部记录。

        Returns:
            删除的行数。
        """
        self._ensure_writable()
        with self._conn:
            cursor = self._conn.execute(
                "DELETE FROM pinyin_data WHERE yinjie = ?", (yinjie,)
            )
        return cursor.rowcount

    def count(self) -> int:
        """返回记录总数。"""
        row = self._conn.execute("SELECT COUNT(*) AS n FROM pinyin_data").fetchone()
        return int(row["n"])


def _row_to_entry(row: sqlite3.Row) -> PinyinEntry:
    """把查询结果转换为领域对象。"""
    return PinyinEntry(row["yinjie"], row["tone"], row["hiragana"])


def _chunks(items: List[tuple[str, str]], size: int) -> Iterator[List[tuple[str, str]]]:
    """按固定大小切分查询键。"""
    for start in range(0, len(items), size):
        yield items[start:start + size]


def _validated(entries: Iterable[PinyinEntry]) -> Iterator[PinyinEntry]:
    """逐条校验后透传，避免为校验再建一个列表。"""
    for entry in entries:
        _validate_entry(entry)
        yield entry


def _validate_entry(entry: PinyinEntry) -> None:
    """校验一条记录的基本格式。"""
    if not entry.yinjie:
        raise ValueError("音节不能为空。")
    if not _is_tone(entry.tone):
        raise ValueError(f"声调格式错误：{entry.tone!r}。")


def _validate_tone_pattern(tone: str) -> None:
    """校验查询用的声调模式。"""
    if len(tone) != 3 or any(char not in "012345*" for char in tone):
        raise ValueError(f"声调模式格式错误：{tone!r}。")
    if tone[1] == "0":
        raise ValueError(f"声调模式第二位不能为 0：{tone!r}。")


def _is_tone(tone: str) -> bool:
    """判断是否为合法的三位声调序列。"""
    return len(tone) == 3 and all(char in "012345" for char in tone) and tone[1] != "0"
