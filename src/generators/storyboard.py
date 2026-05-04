"""Generate storyboard.md from a topic_card.

Seed-curated topics emit their hand-written storyboard verbatim
(only used when the requested length matches the seed's length).
Otherwise the storyboard is rendered from the shared scene
library, with scene count scaled to the requested video length.
"""

from __future__ import annotations

from src.prompts import render_storyboard_md


def generate(card: dict) -> str:
    if card.get("storyboard_md"):
        return card["storyboard_md"]
    return render_storyboard_md(card)
