import sqlite3

import pytest

from yukkurimandarin.db.errors import SchemaError
from yukkurimandarin.db.schema import SCHEMA_VERSION, create_schema, migrate


def table_info(conn):
    return [row[1] for row in conn.execute("PRAGMA table_info(pinyin_data)")]


def test_create_schema(tmp_path):
    conn = sqlite3.connect(tmp_path / "new.db")
    try:
        create_schema(conn)
        conn.commit()
        assert table_info(conn) == ["yinjie", "tone", "hiragana"]
        assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    finally:
        conn.close()


def test_migrate_creates_missing_table(tmp_path):
    conn = sqlite3.connect(tmp_path / "new.db")
    try:
        migrate(conn)
        conn.commit()
        assert table_info(conn) == ["yinjie", "tone", "hiragana"]
        assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    finally:
        conn.close()


def test_migrate_from_v0(tmp_path):
    path = tmp_path / "legacy.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE pinyin_data ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "yinjie TEXT NOT NULL, tone TEXT NOT NULL, hiragana TEXT NOT NULL, "
        "UNIQUE (yinjie, tone) ON CONFLICT REPLACE)"
    )
    conn.execute("INSERT INTO pinyin_data (yinjie, tone, hiragana) VALUES ('ni', '121', 'にい')")
    conn.commit()
    conn.close()

    conn = sqlite3.connect(path)
    try:
        migrate(conn)
        conn.commit()
        assert table_info(conn) == ["yinjie", "tone", "hiragana"]
        assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        rows = conn.execute("SELECT yinjie, tone, hiragana FROM pinyin_data").fetchall()
        assert rows == [("ni", "121", "にい")]
    finally:
        conn.close()


def test_migrate_future_version_rejected(tmp_path):
    conn = sqlite3.connect(tmp_path / "future.db")
    try:
        conn.execute("PRAGMA user_version = 99")
        with pytest.raises(SchemaError):
            migrate(conn)
    finally:
        conn.close()
