"""汉字段处理：填拼音、查假名。

拼音与声调的获取、变调规则分别由 phonology 包负责；本模块只做
「把结果写回 Document」以及「按音节查数据库」。
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Optional

from ..phonology.pinyin import build_serial, to_syllables

if TYPE_CHECKING:
    from jieba import Tokenizer

    from ..db.repository import PinyinRepository
    from ..segments import Document


def fill_pinyin(doc: Document, tokenizer: Optional[Tokenizer] = None) -> Document:
    """为 Document 中的汉字填入拼音与声调。

    Args:
        doc: 由 ``Document.from_text`` 生成的文档。
        tokenizer: jieba 分词器；为 None 时使用默认分词器，未安装则不分词。

    Returns:
        音节已填充的新 Document；假名仍为空。

    Raises:
        ValueError: 拼音数量与汉字数量不一致。
    """
    updated = list(doc.syllables)
    for run in doc.runs:
        if run.kind != "hanzi":
            continue
        text = doc.run_text(run)
        words = tokenizer.lcut(text) if tokenizer is not None else [text]
        pairs = to_syllables([word for word in words if word])
        if len(pairs) != run.length:
            raise ValueError(
                f"拼音数量与汉字数量不一致：{len(pairs)} != {run.length}（{text!r}）。"
            )
        for offset, (syllable, tone) in enumerate(pairs):
            index = run.syl_start + offset
            updated[index] = replace(updated[index], syllable=syllable, tone=tone)
    return doc.with_syllables(updated)


def fill_kana(
    doc: Document, repository: PinyinRepository, *, default: str = ""
) -> Document:
    """查询数据库，为每个音节填入假名拟音。

    所有音节的查询合并为一次批量请求，避免逐字查库。

    Args:
        doc: 已完成拼音与变调的文档。
        repository: 拼音数据库仓储。
        default: 查询无结果时使用的假名。

    Returns:
        假名已填充的新 Document。
    """
    updated = list(doc.syllables)
    serials: list[tuple[str, str]] = []
    positions: list[int] = []
    for run in doc.runs:
        if run.kind != "hanzi":
            continue
        pairs = [
            (syllable.syllable, syllable.tone)
            for syllable in updated[run.syl_start:run.syl_end]
        ]
        for offset, serial in enumerate(build_serial(pairs)):
            serials.append(serial)
            positions.append(run.syl_start + offset)

    entries = repository.get_many(serials)
    if len(entries) != len(serials):
        raise ValueError(
            f"批量查询结果数量不一致：{len(entries)} != {len(serials)}。"
        )
    for index, entry in zip(positions, entries):
        kana = entry.hiragana if entry is not None else default
        if updated[index].kana != kana:
            updated[index] = replace(updated[index], kana=kana)
    return doc.with_syllables(updated)
