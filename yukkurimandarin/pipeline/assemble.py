"""把 Document 组装成最终字符串。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .non_hanzi import convert_run

if TYPE_CHECKING:
    from ..segments import Document
    from ..settings import NonHanziModes


def assemble(doc: Document, config: Optional[NonHanziModes] = None) -> str:
    """按片段顺序拼装输出。

    汉字段拼接各自音节的假名；非汉字段交给 :mod:`pipeline.non_hanzi` 处理。

    Args:
        doc: 已完成拼音、变调与假名填充的文档。
        config: 非汉字处理模式；为 None 时使用默认配置。

    Returns:
        拼装后的文本（尚未做音声记号收尾）。
    """
    parts = []
    for run in doc.runs:
        if run.kind == "hanzi":
            parts.append("".join(syllable.kana for syllable in doc.run_syllables(run)))
        else:
            parts.append(convert_run(doc.run_text(run), run.kind, config))
    return doc.join(parts)
