import csv

import pytest

from yukkurimandarin.db import PinyinEntry, TransferError, read_table, write_table


@pytest.fixture
def entries():
    return [
        PinyinEntry("ni", "121", "にい"),
        PinyinEntry("hao", "131", "'は/お"),
    ]


def test_csv_roundtrip(tmp_path, entries):
    path = tmp_path / "table.csv"
    assert write_table(entries, path) == 2
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["拼音", "声调", "平假名"]
    assert read_table(path) == entries


def test_read_accepts_yinjie_header(tmp_path, entries):
    path = tmp_path / "table.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["音节", "声调", "平假名"])
        writer.writerow(["ni", "121", "にい"])
    assert read_table(path) == [entries[0]]


def test_read_bad_header(tmp_path):
    path = tmp_path / "bad.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["错误表头", "?", "?"])
    with pytest.raises(TransferError):
        read_table(path)


def test_read_bad_columns(tmp_path):
    path = tmp_path / "bad.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["拼音", "声调", "平假名"])
        writer.writerow(["ni", "121"])
    with pytest.raises(TransferError):
        read_table(path)


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_table(tmp_path / "nope.csv")


def test_unsupported_suffix(tmp_path, entries):
    with pytest.raises(TransferError):
        write_table(entries, tmp_path / "table.txt")
    target = tmp_path / "table.txt"
    target.write_text("x", encoding="utf-8")
    with pytest.raises(TransferError):
        read_table(target)


def test_write_skips_empty_lines(tmp_path, entries):
    path = tmp_path / "table.csv"
    write_table(entries, path)
    with path.open("a", encoding="utf-8-sig", newline="") as handle:
        handle.write("\n")
    assert read_table(path) == entries


def test_xlsx_roundtrip(tmp_path, entries):
    pytest.importorskip("openpyxl")
    path = tmp_path / "table.xlsx"
    assert write_table(entries, path) == 2
    assert read_table(path) == entries
