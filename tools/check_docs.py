"""检查 README 与 docs 中的仓库内链接和锚点。

不访问网络：外部链接一律跳过；指向本仓库 GitHub blob 的链接会映射回本地文件。
``docs/archive/`` 是 1.0 历史文档，不参与检查。

用法::

    uv run python tools/check_docs.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SKIP_PARTS = {"archive"}

_GITHUB_BLOB = re.compile(
    r"^https?://github\.com/wubzbz/Yukkuri-Mandarin/blob/main/"
    r"(?P<path>[^#?]+)(?:#(?P<fragment>.*))?$"
)
_LINK = re.compile(r"\]\((?P<target>[^)]+)\)")
_HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+?)\s*$")
_FENCE = re.compile(r"^\s*```")
_TRAILING_HASHES = re.compile(r"\s+#+\s*$")


def github_slug(text: str) -> str:
    """按 GitHub 标题锚点规则生成 slug（近似实现）。"""
    text = _TRAILING_HASHES.sub("", text.strip()).lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def collect_anchors(path: Path) -> Set[str]:
    """收集 Markdown 文件中的标题锚点，重复标题按 GitHub 规则加序号。"""
    anchors: Set[str] = set()
    counts: Dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _HEADING.match(line)
        if match is None:
            continue
        base = github_slug(match.group("text"))
        index = counts.get(base, 0)
        counts[base] = index + 1
        anchors.add(base if index == 0 else f"{base}-{index}")
    return anchors


def iter_links(path: Path) -> Iterable[Tuple[int, str]]:
    """逐行产出 Markdown 链接目标（跳过围栏代码块）。"""
    in_fence = False
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in _LINK.finditer(line):
            yield line_no, normalize_target(match.group("target"))


def normalize_target(raw: str) -> str:
    """去掉链接目标两端的尖括号和可选的 title。"""
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        return target[1:-1]
    parts = target.split()
    return parts[0] if parts else ""


def resolve_target(
    target: str, source: Path
) -> Optional[Tuple[Path, str]]:
    """把链接目标解析成本地文件与锚点；外部链接返回 None。"""
    target = unquote(target)
    if not target or target.startswith("mailto:"):
        return None

    github = _GITHUB_BLOB.match(target)
    if github is not None:
        return (
            (ROOT / unquote(github.group("path"))).resolve(),
            unquote(github.group("fragment") or ""),
        )

    if target.startswith("#"):
        return source, target[1:]

    if target.startswith(("http://", "https://")):
        return None

    relative, _, fragment = target.partition("#")
    return (source.parent / relative).resolve(), fragment


def check_file(path: Path, anchor_cache: Dict[Path, Set[str]]) -> List[str]:
    """检查一个 Markdown 文件中的全部链接。"""
    errors: List[str] = []
    if not path.exists():
        return [f"{path}: 文件不存在"]

    for line_no, target in iter_links(path):
        resolved = resolve_target(target, path)
        if resolved is None:
            continue
        target_path, fragment = resolved
        location = f"{path.relative_to(ROOT)}:{line_no}"

        if not target_path.exists():
            errors.append(f"{location}: 找不到目标 {target}")
            continue
        if not fragment or target_path.suffix.lower() != ".md":
            continue

        if target_path not in anchor_cache:
            anchor_cache[target_path] = collect_anchors(target_path)
        if github_slug(fragment) not in anchor_cache[target_path]:
            errors.append(f"{location}: 找不到锚点 #{fragment}（{target_path.name}）")
    return errors


def iter_documents() -> Iterable[Path]:
    """产出需要检查的文档列表。"""
    yield ROOT / "README.md"
    for path in sorted(DOCS.rglob("*.md")):
        if SKIP_PARTS.isdisjoint(path.parts):
            yield path


def main() -> int:
    """执行检查；发现问题时返回 1。"""
    anchor_cache: Dict[Path, Set[str]] = {}
    errors: List[str] = []
    documents = list(iter_documents())

    for path in documents:
        errors.extend(check_file(path, anchor_cache))

    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"发现 {len(errors)} 个文档链接问题。", file=sys.stderr)
        return 1

    print(f"检查了 {len(documents)} 个文档，链接与锚点均有效。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
