import sqlite3

import pytest

from yukkurimandarin.db import (
    BUNDLED_DB_PATH,
    PinyinEntry,
    PinyinRepository,
    ReadOnlyDatabaseError,
)


@pytest.fixture
def entries():
    return [
        PinyinEntry("ni", "121", "にい"),
        PinyinEntry("ni", "131", "'に/い"),
        PinyinEntry("hao", "131", "'は/お"),
    ]


@pytest.fixture
def db_path(tmp_path, entries):
    path = tmp_path / "test.db"
    PinyinRepository.create(path, entries)
    return path


def test_create_and_count(db_path):
    with PinyinRepository.open(db_path, readonly=True) as repo:
        assert repo.count() == 3


def test_get(db_path, entries):
    with PinyinRepository.open(db_path, readonly=True) as repo:
        assert repo.get("ni", "121") == entries[0]
        assert repo.get("ni", "999") is None


def test_get_many_preserves_order(db_path, entries):
    with PinyinRepository.open(db_path, readonly=True) as repo:
        result = repo.get_many([("ni", "121"), ("xx", "111"), ("hao", "131")])
        assert result[0] == entries[0]
        assert result[1] is None
        assert result[2] == entries[2]


def test_get_many_empty(db_path):
    with PinyinRepository.open(db_path, readonly=True) as repo:
        assert repo.get_many([]) == []


def test_get_many_chunked(db_path, entries):
    keys = [("ni", "121")] * 300
    with PinyinRepository.open(db_path, readonly=True) as repo:
        result = repo.get_many(keys)
    assert len(result) == 300
    assert all(item == entries[0] for item in result)


def test_search(db_path):
    with PinyinRepository.open(db_path, readonly=True) as repo:
        assert [entry.tone for entry in repo.search("ni", "1*1")] == ["121", "131"]
        assert [entry.tone for entry in repo.search("ni", "121")] == ["121"]
        assert [entry.tone for entry in repo.search("ni")] == ["121", "131"]


def test_list_by_yinjie(db_path):
    with PinyinRepository.open(db_path, readonly=True) as repo:
        assert [entry.tone for entry in repo.list_by_yinjie("ni")] == ["121", "131"]
        assert repo.list_by_yinjie("none") == []


def test_iter_all(db_path):
    with PinyinRepository.open(db_path, readonly=True) as repo:
        assert len(list(repo.iter_all())) == 3


def test_upsert(db_path):
    with PinyinRepository.open(db_path) as repo:
        repo.upsert(PinyinEntry("ni", "121", "にー"))
        assert repo.get("ni", "121").hiragana == "にー"
        repo.upsert(PinyinEntry("ni", "141", "に/い"))
        assert repo.count() == 4


def test_upsert_many(db_path):
    with PinyinRepository.open(db_path) as repo:
        count = repo.upsert_many([
            PinyinEntry("a", "010", "ああ"),
            PinyinEntry("ni", "121", "にー"),
        ])
        assert count == 2
        assert repo.get("ni", "121").hiragana == "にー"
        assert repo.get("a", "010") is not None


def test_replace_all(db_path):
    with PinyinRepository.open(db_path) as repo:
        count = repo.replace_all([PinyinEntry("a", "010", "ああ")])
        assert count == 1
        assert repo.count() == 1
        assert repo.get("a", "010") is not None


def test_delete(db_path):
    with PinyinRepository.open(db_path) as repo:
        assert repo.delete("hao", "131") is True
        assert repo.delete("hao", "131") is False
        assert repo.count() == 2


def test_delete_by_yinjie(db_path):
    with PinyinRepository.open(db_path) as repo:
        assert repo.delete_by_yinjie("ni") == 2
        assert repo.list_by_yinjie("ni") == []


def test_create_existing_fails(db_path):
    with pytest.raises(FileExistsError):
        PinyinRepository.create(db_path, [])


def test_create_overwrite(db_path):
    PinyinRepository.create(db_path, [PinyinEntry("a", "010", "ああ")], overwrite=True)
    with PinyinRepository.open(db_path, readonly=True) as repo:
        assert repo.count() == 1


def test_create_overwrite_failure_keeps_old(db_path, entries):
    with pytest.raises(ValueError):
        PinyinRepository.create(
            db_path, [PinyinEntry("x", "bad", "x")], overwrite=True
        )
    with PinyinRepository.open(db_path, readonly=True) as repo:
        assert repo.count() == 3
        assert repo.get("ni", "121") == entries[0]
    assert not [p for p in db_path.parent.iterdir() if p.name.endswith(".tmp")]


@pytest.mark.parametrize("tone", ["1x1", "1211", "103", ""])
def test_invalid_entry(db_path, tone):
    with PinyinRepository.open(db_path) as repo:
        with pytest.raises(ValueError):
            repo.upsert(PinyinEntry("a", tone, "ああ"))


def test_read_only_rejects_writes(db_path):
    with PinyinRepository.open(db_path, readonly=True) as repo:
        with pytest.raises(ReadOnlyDatabaseError):
            repo.upsert(PinyinEntry("a", "010", "ああ"))


def test_create_bundled_rejected():
    with pytest.raises(ReadOnlyDatabaseError):
        PinyinRepository.create(BUNDLED_DB_PATH, [], overwrite=True)


def test_bundled_open_is_forced_readonly():
    with PinyinRepository.open(BUNDLED_DB_PATH) as repo:
        with pytest.raises(ReadOnlyDatabaseError):
            repo.upsert(PinyinEntry("a", "010", "x"))


def test_search_invalid_pattern(db_path):
    with PinyinRepository.open(db_path, readonly=True) as repo:
        for pattern in ("12", "1x1", "102", 123):
            with pytest.raises(ValueError):
                repo.search("ni", pattern)


def test_create_uses_delete_journal(db_path):
    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
    finally:
        conn.close()

    with PinyinRepository.open(db_path, readonly=True) as repo:
        assert repo.count() == 3
    sidecars = [
        path.name
        for path in db_path.parent.iterdir()
        if path.name.endswith(("-wal", "-shm"))
    ]
    assert sidecars == []
