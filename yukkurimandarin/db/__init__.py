"""拼音数据库访问层。

对外只暴露仓储、领域对象与少量工具函数；SQL、连接、文件格式都封装在内部。
"""

from __future__ import annotations

from .connection import BUNDLED_DB_PATH, connect
from .errors import (
    DatabaseUnavailableError,
    MissingDependencyError,
    ReadOnlyDatabaseError,
    SchemaError,
    TransferError,
    YukkuriDBError,
)
from .models import PinyinEntry
from .report import format_table
from .repository import PinyinRepository
from .schema import SCHEMA_VERSION
from .transfer import read_table, write_table

__all__ = [
    "BUNDLED_DB_PATH",
    "SCHEMA_VERSION",
    "DatabaseUnavailableError",
    "MissingDependencyError",
    "PinyinEntry",
    "PinyinRepository",
    "ReadOnlyDatabaseError",
    "SchemaError",
    "TransferError",
    "YukkuriDBError",
    "connect",
    "format_table",
    "read_table",
    "write_table",
]
