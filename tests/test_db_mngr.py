import pytest
from pathlib import Path
import csv

from yukkurimandarin.database_mngr import DatabaseManager, _HAS_OPENPYXL

@pytest.fixture(scope="function")
def temp_dm(tmp_path):
    temp_db_path = tmp_path / "tmp_test_mngr.db"
    dm = DatabaseManager(db_path=temp_db_path)
    yield dm


@pytest.fixture(scope="function")
def temp_csv(tmp_path):
    temp_csv_path = tmp_path / "tmp_yinjie_table.csv"
    yield temp_csv_path


@pytest.fixture(scope="function")
def temp_xlsx(tmp_path):
    temp_xlsx_path = tmp_path / "tmp_yinjie_table.xlsx"
    yield temp_xlsx_path


class TestAddPinyin:
    @pytest.mark.parametrize("yinjie, tone, hiragana, expected", [
        ("yinA", "123", "gana0", True),
        ("yinA", "150", "gana1", True),
        ("yinB", "054", "gana2", True),
        ("yinC", "103", "gana3", False), # 第二位为0
        ("yinD", "623", "gana4", False), # 包含无效字符
        ("yinE", "12", "gana5", False),  # 长度不足
    ])
    def test_add_pinyin(self, temp_dm, yinjie, tone, hiragana, expected):
        assert temp_dm.add_pinyin(yinjie, tone, hiragana, report=False) == expected

    def test_exact_search(self, temp_dm):
        temp_dm.add_pinyin("yinA", "123", "gana0", report=False)
        result = temp_dm.search_by_pinyin("yinA", "123", report=False)
        assert len(result) == 1
        assert result[0] == ("yinA", "123", "gana0")

    def test_wildcard_search(self, temp_dm):
        temp_dm.add_pinyin("yinA", "123", "gana0", report=False)
        temp_dm.add_pinyin("yinA", "153", "gana1", report=False)
        temp_dm.add_pinyin("yinA", "150", "gana1", report=False)
        # 测试通配符查询
        result = temp_dm.search_by_pinyin("yinA", "1*3", report=False)
        assert len(result) == 2

    def test_full_wildcard(self, temp_dm):
        temp_dm.add_pinyin("yinA", "123", "gana0", report=False)
        temp_dm.add_pinyin("yinA", "153", "gana1", report=False)
        temp_dm.add_pinyin("yinA", "150", "gana1", report=False)
        temp_dm.add_pinyin("yinB", "150", "gana1", report=False)
        # 测试全通配符
        result = temp_dm.search_by_pinyin("yinA", report=False)
        assert len(result) == 3

    def test_invalid_tone_format(self, temp_dm):
        temp_dm.add_pinyin("yinA", "150", "gana1", report=False)
        result = temp_dm.search_by_pinyin("yinA", "103", report=False)
        assert result == []

    def test_delete_exact(self, temp_dm):
        temp_dm.add_pinyin("yinA", "123", "gana1", report=False)
        assert temp_dm.delete_pinyin("yinC", "111", report=False)
        assert temp_dm.delete_pinyin("yinA", "123", report=False)
        result = temp_dm.search_by_pinyin("yinA", "123", report=False)
        assert result == []

    def test_delete_wildcard(self, temp_dm):
        temp_dm.add_pinyin("yinB", "155", "gana1", report=False)
        temp_dm.add_pinyin("yinB", "150", "gana1", report=False)
        # 测试通配符删除
        assert temp_dm.delete_pinyin("yinB", "**5", report=False)
        result = temp_dm.search_by_pinyin("yinB", "***", report=False)
        assert len(result) == 1

    def test_delete_all(self, temp_dm):
        temp_dm.add_pinyin("yinA", "123", "gana0", report=False)
        temp_dm.add_pinyin("yinA", "153", "gana1", report=False)
        temp_dm.add_pinyin("yinA", "150", "gana1", report=False)
        temp_dm.add_pinyin("yinB", "150", "gana1", report=False)
        assert temp_dm.delete_pinyin("yinA", "***", report=False)
        result = temp_dm.search_by_pinyin("yinA", report=False)
        assert len(result) == 0


class TestCSVOperations:
    def test_export_to_csv(self, temp_dm, temp_csv):
        temp_dm.add_pinyin("yinA", "123", "gana1", report=False)
        assert temp_dm.export_to_csv(temp_csv, report=False)
        
        # 验证文件内容
        assert temp_csv.exists()
        with open(temp_csv, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert rows[0] == ["拼音", "声调", "平假名"]
            assert rows[1] == ["yinA", "123", "gana1"]

    def test_import_from_csv(self, temp_dm, temp_csv):
        # 创建测试CSV
        with open(temp_csv, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["拼音", "声调", "平假名"])
            writer.writerow(["yinA", "123", "gana1"])
            writer.writerow(["yinB", "543", "gana2"])
        
        assert temp_dm.import_from_csv(temp_csv, report=False)
        
        # 验证数据
        result = temp_dm.search_by_pinyin("yinA", "123", report=False)
        assert len(result) == 1
        result = temp_dm.search_by_pinyin("yinB", "543", report=False)
        assert len(result) == 1

    def test_import_invalid_csv(self, temp_dm, temp_csv):
        # 创建无效CSV（表头错误）
        with open(temp_csv, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["错误表头", "?", "?"])
        assert not temp_dm.import_from_csv(temp_csv, report=False)
    

class TestExcelOperations:
    @pytest.mark.skipif(not _HAS_OPENPYXL, reason="可选模块")
    def test_export_to_excel(self, temp_dm, temp_xlsx):
        # 添加测试数据
        temp_dm.add_pinyin("yinA", "123", "gana1", report=False)
        
        # 导出
        assert temp_dm.export_to_excel(temp_xlsx, report=False)
        assert temp_xlsx.exists()

    @pytest.mark.skipif(not _HAS_OPENPYXL, reason="可选模块")
    def test_import_from_excel(self, temp_dm, temp_xlsx):
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        assert sheet, "缺少表单"
        sheet.title = "拼音数据"
        
        # 写入测试数据
        sheet["A1"] = "拼音"
        sheet["B1"] = "声调"
        sheet["C1"] = "平假名"
        sheet["A2"] = "yinA"
        sheet["B2"] = "123"
        sheet["C2"] = "gana1"
        workbook.save(temp_xlsx)
        
        # 导入
        assert temp_dm.import_from_excel(temp_xlsx, report=False)
        
        # 验证数据
        result = temp_dm.search_by_pinyin("yinA", "123", report=False)
        assert len(result) == 1


class TestSerialSearch:
    def test_serial_search(self, temp_dm):
        temp_dm.add_pinyin("yinA", "123", "gana1", report=False)
        temp_dm.add_pinyin("yinB", "153", "gana2", report=False)

        serial = [("yinA", "123"), ("yinB", "153")]
        result = temp_dm.serial_search(serial)
        assert len(result) == 2
        assert result == ["gana1", "gana2"]

    def test_serial_search_miss(self, temp_dm):
        serial = [("yinC", "213")]
        assert temp_dm.serial_search(serial) == [""]
        assert temp_dm.serial_search(serial, "keep") == ["yinC"]
        assert temp_dm.serial_search(serial, "_") == ["_"]
