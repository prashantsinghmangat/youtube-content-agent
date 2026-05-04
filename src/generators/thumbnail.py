"""Generate thumbnail.md from a topic_card.

Output covers Step 3 of the production spec: thumbnail concept,
emotional trigger, visual composition, text overlay, color
direction, and a ready-to-paste AI image prompt.
"""

from __future__ import annotations

from src.prompts import GENERIC_THUMBNAIL_TEMPLATE, template_context


def generate(card: dict) -> str:
    if card.get("thumbnail_md"):
        return card["thumbnail_md"]
    return GENERIC_THUMBNAIL_TEMPLATE.format(**template_context(card))
