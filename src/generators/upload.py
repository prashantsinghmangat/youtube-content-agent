"""Generate upload.md from a topic_card.

Output covers Step 8 of the v3 production spec: SEO description,
tags, hashtags, filename, category, and a posting-time
recommendation.
"""

from __future__ import annotations

from src.prompts import GENERIC_UPLOAD_TEMPLATE, template_context


def generate(card: dict) -> str:
    if card.get("upload_md"):
        return card["upload_md"]
    return GENERIC_UPLOAD_TEMPLATE.format(**template_context(card))
