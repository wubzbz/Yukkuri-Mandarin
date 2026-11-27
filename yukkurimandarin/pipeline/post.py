"""输出收尾：去音声记号与假名归一化。"""

from __future__ import annotations

from ..chars import normalize_kana

# 要去掉的音声记号：重音、句切、无声化
_ACCENT_DELETE = str.maketrans("", "", "'/_")


def finalize(text: str, *, without_accent: bool = False) -> str:
    """对拼装结果做最后处理。

    Args:
        text: ``assemble`` 的输出。
        without_accent: 是否去掉音声记号；去掉后会把残留的片假名
            转回平假名（无声化写法留下的片假名）。

    Returns:
        最终输出文本。
    """
    if not without_accent:
        return text
    return normalize_kana(text.translate(_ACCENT_DELETE))
