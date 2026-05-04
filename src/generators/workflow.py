"""Generate workflow.md from a topic_card.

The workflow file is the navigation/dashboard layer for the
production pack. It contains two sections:

- EXECUTION WORKFLOW — step-by-step action list, each step
  pinned to an external tool and the exact file/section to
  copy-paste from.
- TOOLS PANEL — clickable links to every external tool the
  workflow uses, grouped by category.

This file is the entry point a creator opens first when they're
about to actually produce the video.
"""

from __future__ import annotations

from src.prompts import GENERIC_WORKFLOW_TEMPLATE, template_context


def generate(card: dict) -> str:
    if card.get("workflow_md"):
        return card["workflow_md"]
    return GENERIC_WORKFLOW_TEMPLATE.format(**template_context(card))
