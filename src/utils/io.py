"""Safe filesystem helpers used by the generators."""

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Create the directory if missing and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_write(path: Path, content: str) -> None:
    """Atomic-ish write: stage to a .tmp file then rename into place.

    Avoids leaving half-written markdown if the process is interrupted mid-write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")
    tmp.replace(path)
