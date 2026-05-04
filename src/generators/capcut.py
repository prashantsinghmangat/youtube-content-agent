"""Generate capcut.md from a topic_card.

Output covers Step 9 of the v3 production spec: CapCut-specific
timeline, transitions, B-roll, subtitle style, SFX, music,
and voiceover pacing.
"""

from __future__ import annotations

from src.prompts import GENERIC_CAPCUT_TEMPLATE, template_context


def generate(card: dict) -> str:
    if card.get("capcut_md"):
        return card["capcut_md"]
    return GENERIC_CAPCUT_TEMPLATE.format(**template_context(card))
