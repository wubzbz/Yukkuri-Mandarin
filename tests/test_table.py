import csv

import pytest

from yukkurimandarin.db import read_table
from yukkurimandarin.db.transfer import CSV_HEADERS as DB_HEADERS
from yukkurimandarin.formats import CSV_HEADERS
from yukkurimandarin.tablegen import render, table


def test_valid_tones():
    tones = table.valid_tones()
    assert len(tones) == 6 * 5 * 6
    assert tones[0] == "010"
    assert tones[-1] == "555"


def test_iter_rows():
    rows = list(table.iter_rows())
    assert len(rows) == len(render.syllables()) * len(table.valid_tones())
    assert rows[0] == ("a", "010", render.render_hiragana("a", "010"))
    assert rows[-1][:2] == ("zuo", "555")


def test_fill_csv_absolute(tmp_path):
    target = tmp_path / "table.csv"
    count = table.fill_csv(target)
    assert count == len(render.syllables()) * 180
    assert target.exists()
    with target.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == list(CSV_HEADERS)
    assert CSV_HEADERS == DB_HEADERS
    assert len(rows) == count + 1
    assert len(read_table(target)) == count


def test_fill_csv_default_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    count = table.fill_csv()
    target = tmp_path / "gr_yinjie_table.csv"
    assert target.exists()
    assert count == len(render.syllables()) * 180


def test_fill_csv_fixes_suffix(tmp_path):
    target = tmp_path / "table.txt"
    table.fill_csv(target)
    assert (tmp_path / "table.csv").exists()
    assert not target.exists()


def test_fill_xlsx(monkeypatch, tmp_path):
    pytest.importorskip("openpyxl")
    target = tmp_path / "table.xlsx"
    count = table.fill_xlsx(target)
    assert target.exists()
    assert count == len(render.syllables()) * 180
    assert len(read_table(target)) == count
