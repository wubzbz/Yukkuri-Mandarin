from pathlib import Path
import sqlite3
from typing import List, Tuple


class Database:
    """拼音数据库基础类"""

    # 默认数据库路径
    DEFAULT_DB_PATH = Path(__file__).parent / "data" / "yinjie_database.db"

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        """初始化数据库连接"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()


    def _create_table(self) -> None:
        """创建拼音数据表"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS pinyin_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            yinjie TEXT NOT NULL,
            tone TEXT NOT NULL,
            hiragana TEXT NOT NULL,
            UNIQUE (yinjie, tone) ON CONFLICT REPLACE
        )
        """)
        self.conn.commit()


    def insert_entry(self, yinjie: str, tone: str, hiragana: str) -> None:
        """插入单条拼音数据
        
        Usage:

          >>> db = Database()
          >>> db.insert_entry("a", "151", "あ")
        """
        self.cursor.execute(
            "INSERT INTO pinyin_data (yinjie, tone, hiragana) VALUES (?, ?, ?)",
            (yinjie, tone, hiragana)
        )
        self.conn.commit()


    def insert_batch(self, entries: List[Tuple[str, str, str]]) -> None:
        """批量插入拼音数据
        
        Usage:

          >>> db = Database()
          >>> batch_data = [
            ("hao", "131", "'は/お"),
            ("ni", "121", "/にい"),
            ("ni", "111", "にい"),
            ("ni", "141", "に/い"),
            ]  # 三元组列表
          >>> db.insert_batch(batch_data)
        """
        self.cursor.executemany(
            "INSERT INTO pinyin_data (yinjie, tone, hiragana) VALUES (?, ?, ?)",
            entries
        )
        self.conn.commit()


    def query_by_pinyin(self, yinjie: str, tone: str) -> List[Tuple[str, str, str]]:
        """通过音节和声调查询拼音数据
        
        Usage:
        
          >>> results = db.query_by_pinyin("ni", "155")
          >>> print(f"音节为'ni'且声调为155的结果: {results}")
        """
        self.cursor.execute(
            "SELECT yinjie, tone, hiragana FROM pinyin_data WHERE yinjie = ? AND tone = ?",
            (yinjie, tone)
        )
        return self.cursor.fetchall()


    def query_by_yinjie(self, yinjie: str) -> List[Tuple[str, str, str]]:
        """查询音节对应的所有拼音数据
        
        Usage:
        
          >>> results = db.query_by_yinjie("ni")
          >>> print(f"音节为'ni'的所有结果: {results}")
        """
        self.cursor.execute(
            "SELECT yinjie, tone, hiragana FROM pinyin_data WHERE yinjie = ?",
            (yinjie,)
        )
        return self.cursor.fetchall()


    def query_batch(self, entries: List[Tuple[str, str]], default: str) -> List[str]:
        """批量查询数据，无结果返回默认值"""
        if not entries:
            return []
        cur = self.cursor
        # 建临时表
        cur.execute("DROP TABLE IF EXISTS _tmp_query")
        cur.execute("CREATE TEMP TABLE _tmp_query(yinjie TEXT, tone TEXT, ord INTEGER PRIMARY KEY)")
        cur.executemany(
            "INSERT INTO _tmp_query(yinjie, tone, ord) VALUES (?,?,?)",
            [(yinjie, tone, idx) for idx, (yinjie, tone) in enumerate(entries)]
        )
        # 保留模式
        if default == "keep":
            cur.execute("""
                SELECT COALESCE(p.hiragana, input.yinjie)
                FROM _tmp_query AS input
                LEFT JOIN "pinyin_data" AS p ON input.yinjie = p.yinjie AND input.tone = p.tone
                ORDER BY input.ord
            """)
        # 替换模式
        else:
            cur.execute("""
                SELECT COALESCE(p.hiragana, ?)
                FROM _tmp_query AS input
                LEFT JOIN "pinyin_data" AS p ON input.yinjie = p.yinjie AND input.tone = p.tone
                ORDER BY input.ord
            """, (default,))
        rows = cur.fetchall()
        # 清理临时表
        cur.execute("DROP TABLE _tmp_query")
        return [row[0] for row in rows]


    def query_all(self) -> List[Tuple[str, str, str]]:
        """查询所有数据"""
        self.cursor.execute(
            "SELECT yinjie, tone, hiragana FROM pinyin_data"
        )
        return self.cursor.fetchall()


    def delete_by_pinyin(self, yinjie: str, tone: str) -> None:
        """删除该音节和声调对应的拼音数据"""
        self.cursor.execute(
            "DELETE FROM pinyin_data WHERE yinjie = ? AND tone = ?",
            (yinjie, tone)
        )
        self.conn.commit()


    def delete_by_yinjie(self, yinjie: str) -> None:
        """删除该音节对应的所有数据"""
        self.cursor.execute(
            "DELETE FROM pinyin_data WHERE yinjie = ?",
            (yinjie,)
        )
        self.conn.commit()


    def close(self) -> None:
        """关闭数据库连接"""
        self.cursor.close()
        self.conn.close()

