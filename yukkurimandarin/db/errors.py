"""数据库层异常。

这一层不返回 bool、不打印错误信息，统一用异常表达失败，
由调用方决定如何呈现。
"""

from __future__ import annotations


from ..errors import MissingDependencyError as MissingDependencyError

__all__ = [
    "MissingDependencyError",
    "ReadOnlyDatabaseError",
    "SchemaError",
    "TransferError",
    "YukkuriDBError",
]


class YukkuriDBError(Exception):
    """数据库层异常的基类。"""


class SchemaError(YukkuriDBError):
    """数据库结构或版本与当前代码不匹配。"""


class TransferError(YukkuriDBError):
    """表格文件读写失败，或内容格式不正确。"""


class ReadOnlyDatabaseError(YukkuriDBError):
    """试图向只读数据库写入。"""
