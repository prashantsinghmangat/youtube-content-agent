"""Topic-to-pack orchestration.

The pipeline is a thin coordinator. Real generation work is delegated
to per-section modules under src/generators/. The pipeline owns:

- topic-card construction (seed match or generic derivation)
- output folder creation
- atomic markdown writing
- a small audit log so the UI can show what was produced
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src import llm
from src.prompts import (
    SUPPORTED_LENGTHS,
    derive_card,
    find_seed,
    length_or_default,
)
from src.utils.io import ensure_dir, safe_write
from src.utils.timestamp import folder_name
from src.generators import (
    ai_prompts,
    capcut,
    idea,
    script,
    shorts,
    storyboard,
    thumbnail,
    titles,
    upload,
    workflow,
)


SUPPORTED_TONES = ("analytical", "curious", "tense", "documentary")


@dataclass
class GenerationResult:
    folder: Path
    files: list[str]
    used_seed: bool
    used_llm: bool                 # provider was configured at generation time
    llm_call_succeeded: bool       # the LLM actually returned text for the script
    llm_provider: str | None       # 'anthropic' / 'google' / None
    script_source: str             # 'seed' / 'llm:<provider>' / 'template'
    titles_source: str             # 'seed' / 'llm:<provider>' / 'template'
    video_length: str


def build_topic_card(topic: str, tone: str, video_length: str) -> dict:
    """Construct the topic_card dict consumed by every generator.

    Seed entries override defaults only when the requested length
    matches the seed's natural length (default "standard"). When the
    user requests a different length on a seed topic, we fall through
    to the generic length-aware path so they actually get the length
    they asked for.
    """
    if tone not in SUPPORTED_TONES:
        tone = "documentary"
    video_length = length_or_default(video_length)

    base = derive_card(topic, tone, video_length)
    seed = find_seed(topic)
    if seed and seed.get("length", "standard") == video_length:
        merged = dict(base)
        merged.update(seed)
        merged["raw_topic"] = base["raw_topic"]
        merged["tone"] = base["tone"]
        merged["video_length"] = video_length
        merged["is_seed"] = True
        return merged
    return base


def generate_pack(
    topic: str,
    tone: str,
    outputs_root: Path,
    video_length: str = "standard",
) -> GenerationResult:
    """Run the full pipeline for one topic and return the output folder."""
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("Topic is required.")

    card = build_topic_card(topic, tone, video_length)
    folder = ensure_dir(outputs_root / folder_name(topic))

    # v3 strict order with v4 dashboard at the end:
    # idea → titles → thumbnail → script → storyboard →
    # ai_prompts → shorts → upload → capcut → workflow.
    sections = [
        ("idea.md", idea.generate(card)),
        ("titles.md", titles.generate(card)),
        ("thumbnail.md", thumbnail.generate(card)),
        ("script.md", script.generate(card)),
        ("storyboard.md", storyboard.generate(card)),
        ("ai_prompts.md", ai_prompts.generate(card)),
        ("shorts.md", shorts.generate(card)),
        ("upload.md", upload.generate(card)),
        ("capcut.md", capcut.generate(card)),
        ("workflow.md", workflow.generate(card)),
    ]

    for filename, content in sections:
        safe_write(folder / filename, content)

    script_source = card.get("_script_source", "template")
    titles_source = card.get("_titles_source", "template")

    return GenerationResult(
        folder=folder,
        files=[name for name, _ in sections],
        used_seed=bool(card.get("is_seed")),
        used_llm=llm.is_available(),
        llm_call_succeeded=script_source.startswith("llm:"),
        llm_provider=llm.active_provider(),
        script_source=script_source,
        titles_source=titles_source,
        video_length=card["video_length"],
    )
