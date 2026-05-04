"""Generate script.md from a topic_card.

Decision tree:
  1. Seed-curated topic with matching length → return curated script.
  2. LLM provider available → ask the LLM to write the script.
  3. Otherwise → render from a length-aware deterministic template.

The LLM path is fail-silent: any error falls through to the
deterministic template. To let the pipeline tell the user which
path actually ran, we record the source on the card under
`_script_source` (one of: "seed", "llm:<provider>", "template").
"""

from __future__ import annotations

from src import llm
from src.prompts import (
    GENERIC_SCRIPT_BODY,
    GENERIC_SCRIPT_DEEP_DIVE_BODY,
    GENERIC_SCRIPT_SHORT_BODY,
    pick_opener,
    template_context,
)


_BODY_BY_LENGTH = {
    "short": GENERIC_SCRIPT_SHORT_BODY,
    "standard": GENERIC_SCRIPT_BODY,
    "deep_dive": GENERIC_SCRIPT_DEEP_DIVE_BODY,
}


def generate(card: dict) -> str:
    if card.get("script_md"):
        card["_script_source"] = "seed"
        return card["script_md"]

    # Try the LLM if available; silently fall through on any failure.
    llm_output = llm.generate_script(card)
    if llm_output:
        provider = llm.active_provider() or "unknown"
        card["_script_source"] = f"llm:{provider}"
        return llm_output

    card["_script_source"] = "template"
    return _render_template(card)


def _render_template(card: dict) -> str:
    ctx = template_context(card)
    body = _BODY_BY_LENGTH.get(ctx["video_length"], GENERIC_SCRIPT_BODY)
    body = body.format(**ctx)
    opener = pick_opener(card.get("tone", "documentary"), ctx["subject"])
    return (
        f"# Script: {ctx['raw_topic']}\n\n"
        f"*Estimated runtime: {ctx['runtime']} (~{ctx['word_target']}).*\n\n"
        f"## HOOK\n\n"
        f"{opener}\n\n"
        f"{body}"
    )
