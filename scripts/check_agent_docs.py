"""Check curated agent guidance without importing Buzz or installing its dependencies.

Run: uv run --no-project --python 3.13 python scripts/check_agent_docs.py
Only inline Markdown file links and standalone @imports are checked; URL health,
Markdown heading anchors, command correctness and client discovery need review.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
GUIDANCE_ROOTS = ("buzz", "tests", ".github", "docs/development", "scripts")
REQUIRED = (
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    "docs/development/README.md",
    "docs/development/architecture.md",
    "docs/development/development.md",
    "docs/development/agent-workflow.md",
    "docs/development/fork.md",
    "docs/development/plugins.md",
    "buzz/widgets/AGENTS.md",
    "buzz/transcriber/AGENTS.md",
    "buzz/db/AGENTS.md",
    "buzz/plugins/AGENTS.md",
    "tests/AGENTS.md",
    ".github/AGENTS.md",
)
LINK = re.compile(r"\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\s*\)")
IMPORT = re.compile(r"^@([^\s]+)$", re.MULTILINE)


def prose(content: str) -> str:
    """Exclude fenced examples, whose links/imports need not exist."""
    fence = None
    lines = []
    for line in content.splitlines():
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)


def local_target(source: Path, raw: str, root: Path) -> Path | None:
    target = urlsplit(raw.strip("<>"))
    if target.scheme or target.netloc or not target.path:
        return None
    path = unquote(target.path)
    base = root if path.startswith("/") else source.parent
    return (base / path.lstrip("/")).resolve()


def check(root: Path) -> tuple[list[str], list[str]]:
    root = root.resolve()
    errors = []
    metrics = []
    instructions = {root / "AGENTS.md", root / "CLAUDE.md"}
    for directory in GUIDANCE_ROOTS:
        for name in ("AGENTS.md", "CLAUDE.md"):
            instructions.update((root / directory).rglob(name))
    documents = instructions | set((root / "docs/development").rglob("*.md"))
    copilot = root / ".github/copilot-instructions.md"
    documents.add(copilot)

    def label(path: Path) -> str:
        return path.relative_to(root).as_posix()

    for name in REQUIRED:
        if not (root / name).is_file():
            errors.append(f"Missing required entry: {name}")

    imports: dict[Path, list[Path]] = {}
    agent_sizes: dict[Path, int] = {}
    for path in sorted(documents):
        if not path.is_file():
            continue
        name = label(path)
        content = path.read_text(encoding="utf-8")
        size = len(content.encode("utf-8"))
        body = prose(content)
        references = LINK.findall(body)
        if path in instructions:
            references += IMPORT.findall(body)
            imports[path] = []
        for raw in references:
            target = local_target(path, raw, root)
            if target is None:
                continue
            if not target.is_relative_to(root):
                errors.append(f"{name}: reference escapes repository: {raw}")
            elif not target.exists():
                errors.append(f"{name}: missing local target: {raw}")
        if path in instructions:
            imports[path] = [
                target
                for raw in IMPORT.findall(body)
                if (target := local_target(path, raw, root)) is not None
            ]
        if path.name == "AGENTS.md":
            limit = 6000 if path.parent == root else 4000
            agent_sizes[path] = size
            if size > limit:
                errors.append(f"{name}: {size} bytes exceeds {limit}-byte budget")
            adapter = path.with_name("CLAUDE.md")
            if not adapter.is_file():
                errors.append(f"{name}: missing sibling CLAUDE.md adapter")
        elif path.name == "CLAUDE.md":
            if content != "@AGENTS.md\n":
                errors.append(f"{name}: adapter must contain only @AGENTS.md + newline")
            if not path.with_name("AGENTS.md").is_file():
                errors.append(f"{name}: missing sibling AGENTS.md")
        elif path == copilot:
            if size > 600 or "../AGENTS.md" not in references:
                errors.append(f"{name}: keep a <=600-byte pointer to ../AGENTS.md")

    visited: set[Path] = set()
    active: set[Path] = set()

    def visit(path: Path) -> None:
        if path in active:
            errors.append(f"Instruction import cycle at {label(path)}")
            return
        if path in visited:
            return
        active.add(path)
        for target in imports.get(path, []):
            visit(target)
        active.remove(path)
        visited.add(path)

    for path in imports:
        visit(path)

    if agent_sizes:
        largest_chain = max(
            sum(
                size
                for ancestor, size in agent_sizes.items()
                if path.parent.is_relative_to(ancestor.parent)
            )
            for path in agent_sizes
        )
        metrics.append(
            f"Root AGENTS.md: {agent_sizes.get(root / 'AGENTS.md', 0)} bytes"
        )
        metrics.append(f"Largest AGENTS.md ancestor chain: {largest_chain} bytes")
    metrics.append(f"Checked {len(documents)} guidance/reference files")
    return errors, metrics


def main() -> int:
    errors, metrics = check(ROOT)
    for metric in metrics:
        print(metric)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Agent documentation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
