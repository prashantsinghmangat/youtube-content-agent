"""Generate idea.md from a topic_card.

Output covers Step 1 of the v3 production spec: a single refined
viral video concept with hook angle and emotional curiosity angle.
"""

from __future__ import annotations

from src.prompts import GENERIC_IDEA_TEMPLATE, template_context


def generate(card: dict) -> str:
    if card.get("idea_md"):
        return card["idea_md"]
    return GENERIC_IDEA_TEMPLATE.format(**template_context(card))
