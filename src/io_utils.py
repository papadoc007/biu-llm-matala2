from __future__ import annotations

from pathlib import Path


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def read_markdown_body(path: str | Path) -> str:
    raw = read_text(path)
    lines = raw.splitlines()
    if lines and lines[0].startswith("#"):
        return "\n".join(lines[1:]).strip()
    return raw


def write_markdown(path: str | Path, title: str, body: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")
