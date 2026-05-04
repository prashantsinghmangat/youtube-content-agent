"""Generate ai_prompts.md from a topic_card.

Seed-curated topics emit their hand-written prompts verbatim.
Otherwise prompts are rendered from the same scene library that
powers storyboard.md — so scene counts always match.
"""

from __future__ import annotations

from src.prompts import render_ai_prompts_md


def generate(card: dict) -> str:
    if card.get("ai_prompts_md"):
        return card["ai_prompts_md"]
    return render_ai_prompts_md(card)
