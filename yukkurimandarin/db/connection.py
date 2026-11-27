"""SQLite 连接管理。

连接的生命周期只在这里管理：打开、PRAGMA 设置、关闭。
仓储层不直接创建连接。
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union

from .errors import DatabaseUnavailableError, SchemaError
from .schema import SCHEMA_VERSION, migrate

#: 随包分发的只读数据库
BUNDLED_DB_PATH = Path(__file__).parent.parent / "data" / "yinjie_database.db"

_BUSY_TIMEOUT_MS = 5000


def is_bundled_path(path: Union[str, Path]) -> bool:
    """判断路径是否指向内置数据库（包括硬链接）。"""
    candidate = Path(path)
    try:
        return os.path.samefile(candidate, BUNDLED_DB_PATH)
    except OSError:
        return candidate.resolve() == BUNDLED_DB_PATH.resolve()


def open_connection(
    path: Optional[Union[str, Path]] = None,
    *,
    readonly: bool = False,
    create: bool = False,
) -> sqlite3.Connection:
    """打开数据库连接并完成初始化。

    Args:
        path: 数据库路径；None 表示随包分发的内置库（强制只读）。
        readonly: 是否只读打开。
        create: 文件不存在时是否允许新建（仅对可写连接有效）。

    Returns:
        已设置 ``row_factory``、完成迁移（可写）或版本检查（只读）的连接。

    Raises:
        FileNotFoundError: 文件不存在且未允许新建。
        SchemaError: 数据库版本与当前代码不匹配。
    """
    if path is None:
        path = BUNDLED_DB_PATH
        readonly = True
    else:
        path = Path(path)
        # 内置库一律只读，即使调用方显式要求可写
        if is_bundled_path(path):
            readonly = True

    if not path.exists() and (readonly or not create):
        raise FileNotFoundError(f"数据库不存在：{path}")

    conn = _connect(path, readonly)
    try:
        _initialize(conn, readonly)
    except sqlite3.Error as exc:
        conn.close()
        raise DatabaseUnavailableError(f"数据库初始化失败：{exc}") from exc
    except Exception:
        conn.close()
        raise
    return conn


def _connect(path: Path, readonly: bool) -> sqlite3.Connection:
    """建立连接，并把 sqlite3 的打开错误包装成库内异常。"""
    try:
        if readonly:
            uri = f"{path.resolve().as_uri()}?mode=ro"
            return sqlite3.connect(uri, uri=True)
        return sqlite3.connect(path)
    except sqlite3.Error as exc:
        raise DatabaseUnavailableError(f"无法打开数据库：{exc}") from exc


def _initialize(conn: sqlite3.Connection, readonly: bool) -> None:
    """设置连接参数；只读时校验版本，可写时执行迁移。"""
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")
    if readonly:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version != SCHEMA_VERSION:
            raise SchemaError(
                f"数据库版本 {version} 与当前代码的版本 {SCHEMA_VERSION} 不一致。"
            )
    else:
        # 不强制 WAL：自定义库保持原有日志模式，避免只读打开产生 -wal/-shm
        migrate(conn)
        conn.commit()


@contextmanager
def connect(
    path: Optional[Union[str, Path]] = None,
    *,
    readonly: bool = False,
    create: bool = False,
) -> Generator[sqlite3.Connection, None, None]:
    """打开数据库连接，退出时确保关闭。

    Args:
        path: 数据库路径；None 表示随包分发的内置库。
        readonly: 是否只读打开；path 为 None 时强制只读。
        create: 文件不存在时是否允许新建。

    Yields:
        已初始化的连接；退出 ``with`` 时关闭。

    Raises:
        FileNotFoundError: 数据库文件不存在。
        SchemaError: 数据库版本与当前代码不匹配。
    """
    conn = open_connection(path, readonly=readonly, create=create)
    try:
        yield conn
    finally:
        conn.close()
