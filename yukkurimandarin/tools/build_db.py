"""从全局规则重建拼音数据库（构建工具）。

内置数据库（随包分发）是只读资源，本工具拒绝把它作为输出路径；
目标应是用户自己维护的可写数据库。重建会整库覆盖目标文件的现有记录，
执行前请确认已备份，或确认那份数据库本来就可以丢弃。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence, Union

from ..db import PinyinEntry, PinyinRepository, ReadOnlyDatabaseError
from ..tablegen.render import render_hiragana, syllables
from ..tablegen.table import valid_tones

_DEFAULT_OUTPUT = "yinjie_database.db"


def build_database(
    path: Union[str, Path], *, overwrite: bool = False
) -> int:
    """按规则生成全部记录并写入新的数据库。

    Args:
        path: 目标数据库路径。
        overwrite: 目标已存在时是否覆盖。

    Returns:
        写入的记录数。

    Raises:
        FileExistsError: 目标已存在且 overwrite 为 False。
        ReadOnlyDatabaseError: 目标是随包分发的内置数据库。
    """
    entries = (
        PinyinEntry(yinjie, tone, render_hiragana(yinjie, tone))
        for yinjie in syllables()
        for tone in valid_tones()
    )
    PinyinRepository.create(path, entries, overwrite=overwrite)
    return len(syllables()) * len(valid_tones())


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        description="按全局规则重建拼音数据库（会覆盖已有记录）。"
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=_DEFAULT_OUTPUT,
        help=f"输出数据库路径，默认 {_DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="目标文件已存在时覆盖",
    )
    args = parser.parse_args(argv)
    try:
        count = build_database(Path(args.output), overwrite=args.overwrite)
    except FileExistsError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    except ReadOnlyDatabaseError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    print(f"已写入 {count} 条记录：{args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
