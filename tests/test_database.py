import pytest
from pathlib import Path
import sqlite3

from yukkurimandarin.database import Database

def test_is_db_exists():
    assert Database.DEFAULT_DB_PATH.exists(), "数据库不见了！"


@pytest.fixture
def temp_db(tmp_path):
    # 临时数据库路径
    temp_db_path = tmp_path / "temp_test.db"
    db = Database(temp_db_path)
    yield db
    db.close()


def test_close_connection(tmp_path):
    temp_db_path = tmp_path / "temp_test.db"
    db = Database(temp_db_path)
    db.close()
    # 验证连接已关闭
    with pytest.raises(sqlite3.ProgrammingError):
        db.insert_entry("yinjie1", "tone1", "hiragana1")


def test_database_initialization(temp_db):
    temp_db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pinyin_data'")
    table_exists = temp_db.cursor.fetchone() is not None
    assert table_exists, "未正确创建"


def test_insert_entry(temp_db):
    temp_db.insert_entry("a", "121", "hiragana1")
    
    result = temp_db.query_by_pinyin("a", "121")
    assert len(result) == 1, "单条数据插入失败"
    assert result[0] == ("a", "121", "hiragana1"), "插入数据不匹配"


def test_insert_batch_and_query_by_yinjie(temp_db):
    entries = [
        ("e", "111", "hiragana1"),
        ("e", "121", "hiragana2"),
        ("e", "222", "hiragana3")
    ]
    temp_db.insert_batch(entries)
    
    result = temp_db.query_by_yinjie("e")
    assert len(result) == 3, "批量插入数量不正确"
    for entry in entries:
        assert entry in result, f"批量插入的数据 {entry} 不存在"
    # 测试不存在的数据
    result = temp_db.query_by_yinjie("nonexistent")
    assert result == [], "查询不存在的客户端应返回空列表"


def test_query_by_pinyin(temp_db):
    temp_db.insert_entry("yi", "131", "hiragana1")
    
    # 正常查询
    result = temp_db.query_by_pinyin("yi", "131")
    assert result == [("yi", "131", "hiragana1")], "按组查询结果不正确"
    # 测试不存在的组
    result = temp_db.query_by_pinyin("nonexistent", "233")
    assert result == [], "查询不存在的组应返回空列表"
    

def test_query_batch(temp_db):
    temp_db.insert_entry("ou", "010", "hiragana1")
    temp_db.insert_entry("yu", "011", "hiragana3")
    
    # 查询条件
    query_entries = [
        ("ou", "010"),
        ("ou", "111"),  # 不存在
        ("yu", "011"),
        ("yu", "114")   # 不存在
    ]
    
    # 默认替换模式
    result = temp_db.query_batch(query_entries, "")
    assert result == ["hiragana1", "", "hiragana3", ""], "批量查询默认模式结果不正确"
    # keep模式
    result = temp_db.query_batch(query_entries, "keep")
    assert result == ["hiragana1", "ou", "hiragana3", "yu"], "批量查询keep模式结果不正确"
    # 测试空输入
    result = temp_db.query_batch([], "")
    assert result == [], "空输入应返回空列表"


def test_query_all(temp_db):
    # 初始状态应为空
    assert temp_db.query_all() == [], "新数据库不应包含数据"
    
    entries = [("yinjie1", "tone1", "hiragana1")]
    temp_db.insert_batch(entries)
    
    # 验证查询结果
    assert temp_db.query_all() == entries, "查询所有数据结果不正确"


def test_delete_by_pinyin(temp_db):
    temp_db.insert_entry("yinjie1", "tone1", "hiragana1")
    temp_db.insert_entry("yinjie1", "tone2", "hiragana2")
    
    temp_db.delete_by_pinyin("yinjie1", "tone1")
    
    remaining = temp_db.query_by_yinjie("yinjie1")
    assert len(remaining) == 1, "删除数据后剩余数量不正确"
    assert remaining == [("yinjie1", "tone2", "hiragana2")], "删除了错误的数据"


def test_delete_by_yinjie(temp_db):
    temp_db.insert_entry("yinjie1", "tone1", "hiragana1")
    temp_db.insert_entry("yinjie1", "tone2", "hiragana2")
    temp_db.insert_entry("yinjie2", "tone1", "hiragana3")
    
    temp_db.delete_by_yinjie("yinjie1")
    
    assert temp_db.query_by_yinjie("yinjie1") == [], "数据未完全删除"
    assert temp_db.query_by_yinjie("yinjie2") == [("yinjie2", "tone1", "hiragana3")], "误删了其他数据"


def test_unique_constraint(temp_db):
    # 测试唯一约束
    temp_db.insert_entry("yinjie1", "tone1", "hiragana1")
    temp_db.insert_entry("yinjie1", "tone1", "hiragana2")  # 替换前一条
    
    result = temp_db.query_by_pinyin("yinjie1", "tone1")
    assert len(result) == 1, "唯一约束未生效"
    assert result[0][2] == "hiragana2", "重复数据未正确替换"




