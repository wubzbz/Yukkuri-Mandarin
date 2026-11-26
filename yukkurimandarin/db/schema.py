"""数据库结构与迁移。"""

from __future__ import annotations

import sqlite3

from .errors import SchemaError

#: 当前代码使用的 schema 版本，写入 ``PRAGMA user_version``
SCHEMA_VERSION = 1

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pinyin_data (
    yinjie   TEXT NOT NULL,
    tone     TEXT NOT NULL CHECK (length(tone) = 3),
    hiragana TEXT NOT NULL,
    PRIMARY KEY (yinjie, tone)
) WITHOUT ROWID
"""


def create_schema(conn: sqlite3.Connection) -> None:
    """创建当前版本的表结构。

    表以 ``(yinjie, tone)`` 为复合主键（WITHOUT ROWID），不再有 id 列。

    Args:
        conn: 可写连接。
    """
    conn.execute(_SCHEMA_SQL)
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def migrate(conn: sqlite3.Connection) -> None:
    """把数据库迁移到 :data:`SCHEMA_VERSION`。

    依据 ``PRAGMA user_version`` 判断当前版本；0 → 1 会重建表以去掉旧的
    id 列并改用复合主键。已是当前版本时不做任何事。

    Args:
        conn: 可写连接。

    Raises:
        SchemaError: 数据库版本高于当前代码支持的版本。
    """
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version == SCHEMA_VERSION:
        return
    if version > SCHEMA_VERSION:
        raise SchemaError(
            f"数据库版本 {version} 高于当前代码支持的版本 {SCHEMA_VERSION}。"
        )
    _migrate_from_v0(conn)


def _migrate_from_v0(conn: sqlite3.Connection) -> None:
    """从无版本号（v0）的库迁移到当前结构。"""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'pinyin_data'"
    ).fetchone()
    if row is None:
        create_schema(conn)
        return

    # 旧表可能带 id 列与 UNIQUE 约束，改名后按新结构重建
    conn.execute("ALTER TABLE pinyin_data RENAME TO pinyin_data_v0")
    conn.execute(_SCHEMA_SQL)
    conn.execute(
        "INSERT INTO pinyin_data (yinjie, tone, hiragana) "
        "SELECT yinjie, tone, hiragana FROM pinyin_data_v0"
    )
    conn.execute("DROP TABLE pinyin_data_v0")
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
