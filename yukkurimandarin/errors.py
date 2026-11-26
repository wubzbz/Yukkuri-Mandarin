"""跨层共享的异常。"""

from __future__ import annotations


class MissingDependencyError(ImportError):
    """缺少可选依赖（例如读写 .xlsx 需要的 openpyxl）。"""
