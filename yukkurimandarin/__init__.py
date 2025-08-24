# Yukkuri-Mandarin

try:
    from importlib.metadata import version
    __version__ = version("yukkuri-mandarin")
except ImportError:
    __version__ = "dev"

__title__ = "yukkurimandarin"
__author__ = "wubzbz"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 wubzbz"
__all__ = [
    "text_convert",
    "pinyin_convert",
    "DatabaseManager",
    "fill_xlsx",
    "fill_csv",
    "NonHanziModes",
    ]

from yukkurimandarin.core import text_convert,pinyin_convert
from yukkurimandarin.database_mngr import DatabaseManager
from yukkurimandarin.generate_table import fill_csv, fill_xlsx
from yukkurimandarin.settings import NonHanziModes




