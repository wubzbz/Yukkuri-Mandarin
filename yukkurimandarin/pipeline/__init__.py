"""转换管线的各阶段。

一次完整的转换依次经过：

    normalize_text → Document.from_text → fill_pinyin
    → sandhi.apply → fill_kana → assemble → finalize
"""

from __future__ import annotations

from .assemble import assemble
from .hanzi import fill_kana, fill_pinyin
from .non_hanzi import convert_run
from .normalize import digit_to_chinese, normalize_text
from .post import finalize

__all__ = [
    "assemble",
    "convert_run",
    "digit_to_chinese",
    "fill_kana",
    "fill_pinyin",
    "finalize",
    "normalize_text",
]
