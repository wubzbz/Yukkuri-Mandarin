"""Yukkuri-Mandarin：用假名（五十音）模拟拼读现代汉语普通话。"""

from __future__ import annotations

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    __version__ = "dev"
else:
    try:
        __version__ = version("yukkuri-mandarin")
    except PackageNotFoundError:
        __version__ = "dev"

from .api import Converter, pinyin_convert, text_convert
from .db import PinyinEntry, PinyinRepository
from .settings import DEFAULT_CONFIG, Config, NonHanziModes
from .tablegen import fill_csv, fill_xlsx

__title__ = "yukkurimandarin"
__author__ = "wubzbz"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 wubzbz"

__all__ = [
    "Converter",
    "Config",
    "DEFAULT_CONFIG",
    "NonHanziModes",
    "PinyinEntry",
    "PinyinRepository",
    "fill_csv",
    "fill_xlsx",
    "pinyin_convert",
    "text_convert",
]
