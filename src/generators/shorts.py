"""Generate shorts.md from a topic_card.

Output covers Step 8 of the production spec: 5–8 standalone
vertical Shorts extracted from the long-form script.
"""

from __future__ import annotations

from src.prompts import GENERIC_SHORTS_TEMPLATE, template_context


def generate(card: dict) -> str:
    if card.get("shorts_md"):
        return card["shorts_md"]
    return GENERIC_SHORTS_TEMPLATE.format(**template_context(card))
