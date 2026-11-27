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

    依据 ``PRAGMA user_version`` 判断当前版本；0 → 1 会在事务中重建表，
    失败时回滚，数据库保持迁移前的状态。已是当前版本时不做任何事。

    Args:
        conn: 可写连接。

    Raises:
        SchemaError: 版本高于当前代码，或迁移失败。
    """
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version == SCHEMA_VERSION:
        return
    if version > SCHEMA_VERSION:
        raise SchemaError(
            f"数据库版本 {version} 高于当前代码支持的版本 {SCHEMA_VERSION}。"
        )
    try:
        _migrate_from_v0(conn)
    except sqlite3.Error as exc:
        raise SchemaError(f"数据库迁移失败：{exc}") from exc


def _migrate_from_v0(conn: sqlite3.Connection) -> None:
    """从无版本号（v0）的库迁移到当前结构。"""
    tables = _table_names(conn)
    if "pinyin_data_v0" in tables:
        _recover_incomplete_migration(conn, tables)
        tables = _table_names(conn)
    if "pinyin_data" not in tables:
        create_schema(conn)
        return
    _rebuild_from_v0(conn)


def _rebuild_from_v0(conn: sqlite3.Connection) -> None:
    """在 SAVEPOINT 中重建表；失败时回滚到旧表。"""
    conn.execute("SAVEPOINT migrate_v0")
    try:
        conn.execute("ALTER TABLE pinyin_data RENAME TO pinyin_data_v0")
        conn.execute(_SCHEMA_SQL)
        conn.execute(
            "INSERT INTO pinyin_data (yinjie, tone, hiragana) "
            "SELECT yinjie, tone, hiragana FROM pinyin_data_v0"
        )
        conn.execute("DROP TABLE pinyin_data_v0")
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.execute("RELEASE migrate_v0")
    except Exception:
        conn.execute("ROLLBACK TO migrate_v0")
        conn.execute("RELEASE migrate_v0")
        raise


def _recover_incomplete_migration(
    conn: sqlite3.Connection, tables: set[str]
) -> None:
    """恢复上一次中断的迁移：把 pinyin_data_v0 还原成 pinyin_data。"""
    if "pinyin_data" in tables:
        rows = conn.execute("SELECT COUNT(*) FROM pinyin_data").fetchone()[0]
        if rows:
            raise SchemaError(
                "检测到未完成的迁移：pinyin_data 与 pinyin_data_v0 同时存在，"
                "请从备份恢复数据库。"
            )
        conn.execute("SAVEPOINT recover_v0")
        try:
            conn.execute("DROP TABLE pinyin_data")
            conn.execute("ALTER TABLE pinyin_data_v0 RENAME TO pinyin_data")
            conn.execute("RELEASE recover_v0")
        except Exception:
            conn.execute("ROLLBACK TO recover_v0")
            conn.execute("RELEASE recover_v0")
            raise
    else:
        conn.execute("ALTER TABLE pinyin_data_v0 RENAME TO pinyin_data")


def _table_names(conn: sqlite3.Connection) -> set[str]:
    """返回数据库中的表名集合。"""
    return {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
