"""Timestamped folder naming for outputs."""

from __future__ import annotations

import re
from datetime import datetime


def now_slug() -> str:
    """Filesystem-safe timestamp like 20260503-141523."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def slugify(text: str, max_length: int = 60) -> str:
    """Convert arbitrary text into a filesystem-safe slug."""
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:max_length].strip("-") or "untitled"


def folder_name(topic: str) -> str:
    """Build a deterministic timestamped folder name from a topic string."""
    return f"{now_slug()}_{slugify(topic)}"
