import pytest
import tempfile, os
from pathlib import Path

import yukkurimandarin.generate_table as t


def test_gr_tone():
    assert len(t.generate_valid_numbers()) == 6 * 5 * 6


def test_fill_csv_1():
    # 相对路径
    relative_path = "tests/test_data/gr_yinjie_table"
    t.fill_csv(relative_path)
    assert Path(f"{relative_path}.csv").exists(), "csv文件未成功创建在相对路径"


def test_fill_csv_2():
    # 默认路径(temp)
    with tempfile.TemporaryDirectory() as tmpdir:
        # 获取当前工作目录并临时更改
        original_cwd = Path.cwd()
        try:
            os.chdir(tmpdir)
            t.fill_csv()
            # 验证文件在当前工作目录下创建
            expected_file = Path(tmpdir) / "gr_yinjie_table.csv"
            assert expected_file.exists(), "csv文件未成功创建在默认路径"
        finally:
            # 恢复原工作目录
            os.chdir(original_cwd)


def test_fill_csv_3():
    # 绝对路径(temp)
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_gr_csv.csv"
        absolute_path = str(test_file.absolute())
        t.fill_csv(absolute_path)
        assert test_file.exists(), "csv文件未成功创建在绝对路径"


@pytest.mark.skipif(not t._HAS_OPENPYXL, reason="可选模块")
def test_fill_xlsx_1():
    # 相对路径
    relative_path = "tests/test_data/gr_yinjie_table"
    t.fill_xlsx(relative_path)
    assert Path(f"{relative_path}.xlsx").exists(), "xlsx文件未成功创建在相对路径"


@pytest.mark.skipif(not t._HAS_OPENPYXL, reason="可选模块")
def test_fill_xlsx_2():
    # 默认路径(temp)
    with tempfile.TemporaryDirectory() as tmpdir:
        # 获取当前工作目录并临时更改
        original_cwd = Path.cwd()
        try:
            os.chdir(tmpdir)
            t.fill_xlsx()
            # 验证文件在当前工作目录下创建
            expected_file = Path(tmpdir) / "gr_yinjie_table.xlsx"
            assert expected_file.exists(), "xlsx文件未成功创建在默认路径"
        finally:
            # 恢复原工作目录
            os.chdir(original_cwd)


@pytest.mark.skipif(not t._HAS_OPENPYXL, reason="可选模块")
def test_fill_xlsx_3():
    # 绝对路径(temp)
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_gr_xlsx.xlsx"
        absolute_path = str(test_file.absolute())
        t.fill_xlsx(absolute_path)
        assert test_file.exists(), "xlsx文件未成功创建在绝对路径"