"""Generate titles.md from a topic_card.

Decision tree:
  1. Seed-curated topic → return curated titles.
  2. Claude API available → render the deterministic template, then
     ask Claude to sharpen it. If Claude fails, return the
     deterministic version unchanged.
  3. Otherwise → return the deterministic template.
"""

from __future__ import annotations

from src import llm
from src.prompts import GENERIC_TITLES_TEMPLATE, template_context


def generate(card: dict) -> str:
    if card.get("titles_md"):
        card["_titles_source"] = "seed"
        return card["titles_md"]

    deterministic = GENERIC_TITLES_TEMPLATE.format(**template_context(card))

    refined = llm.refine_titles(card, deterministic)
    if refined:
        provider = llm.active_provider() or "unknown"
        card["_titles_source"] = f"llm:{provider}"
        return refined

    card["_titles_source"] = "template"
    return deterministic
