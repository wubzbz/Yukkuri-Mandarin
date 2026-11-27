import sqlite3

import pytest

from yukkurimandarin.db import PinyinRepository
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


def test_migrate_failure_rolls_back(tmp_path):
    path = tmp_path / "bad.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE pinyin_data ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "yinjie TEXT NOT NULL, tone TEXT NOT NULL, hiragana TEXT NOT NULL, "
        "UNIQUE (yinjie, tone) ON CONFLICT REPLACE)"
    )
    conn.execute("INSERT INTO pinyin_data (yinjie, tone, hiragana) VALUES ('ni', '12', 'にい')")
    conn.commit()
    conn.close()

    with pytest.raises(SchemaError):
        PinyinRepository.open(path)

    conn = sqlite3.connect(path)
    try:
        tables = [
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            if not row[0].startswith("sqlite_")
        ]
        rows = conn.execute("SELECT yinjie, tone, hiragana FROM pinyin_data").fetchall()
        assert tables == ["pinyin_data"]
        assert rows == [("ni", "12", "にい")]
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 0
    finally:
        conn.close()


def test_migrate_recovers_incomplete_migration(tmp_path):
    path = tmp_path / "recover.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE pinyin_data_v0 ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "yinjie TEXT NOT NULL, tone TEXT NOT NULL, hiragana TEXT NOT NULL)"
    )
    conn.execute("INSERT INTO pinyin_data_v0 (yinjie, tone, hiragana) VALUES ('ni', '121', 'にい')")
    create_schema(conn)
    conn.execute("PRAGMA user_version = 0")  # 模拟中断在写入版本号之前
    conn.commit()
    conn.close()

    with PinyinRepository.open(path) as repo:
        assert repo.count() == 1

    conn = sqlite3.connect(path)
    try:
        tables = [
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            if not row[0].startswith("sqlite_")
        ]
        assert tables == ["pinyin_data"]
        assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    finally:
        conn.close()


def test_future_version_keeps_journal_mode(tmp_path):
    path = tmp_path / "future.db"
    conn = sqlite3.connect(path)
    create_schema(conn)
    conn.execute("PRAGMA user_version = 99")
    conn.commit()
    conn.close()

    with pytest.raises(SchemaError):
        PinyinRepository.open(path)

    conn = sqlite3.connect(path)
    try:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
    finally:
        conn.close()


def test_readonly_future_version_rejected(tmp_path):
    path = tmp_path / "future.db"
    conn = sqlite3.connect(path)
    create_schema(conn)
    conn.execute("PRAGMA user_version = 99")
    conn.commit()
    conn.close()

    with pytest.raises(SchemaError):
        PinyinRepository.open(path, readonly=True)
