import pytest

from yukkurimandarin.db import (
    BUNDLED_DB_PATH,
    PinyinRepository,
    ReadOnlyDatabaseError,
)
from yukkurimandarin.tools import build_db

EXPECTED_ROWS = 74700


def test_build_database(tmp_path):
    path = tmp_path / "built.db"
    assert build_db.build_database(path) == EXPECTED_ROWS
    with PinyinRepository.open(path, readonly=True) as repo:
        assert repo.count() == EXPECTED_ROWS
        assert repo.get("ni", "131") is not None


def test_build_existing_fails(tmp_path):
    path = tmp_path / "built.db"
    build_db.build_database(path)
    with pytest.raises(FileExistsError):
        build_db.build_database(path)


def test_build_bundled_rejected():
    with pytest.raises(ReadOnlyDatabaseError):
        build_db.build_database(BUNDLED_DB_PATH, overwrite=True)


def test_main(tmp_path):
    path = tmp_path / "cli.db"
    assert build_db.main([str(path)]) == 0
    assert build_db.main([str(path)]) == 1


def test_main_reports_errors(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise ValueError("bad")

    monkeypatch.setattr(build_db, "build_database", boom)
    assert build_db.main([str(tmp_path / "x.db")]) == 1
