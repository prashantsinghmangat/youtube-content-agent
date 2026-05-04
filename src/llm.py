"""Optional LLM hybrid mode — supports Anthropic Claude AND Google Gemini.

The system runs **without** an LLM by default. Deterministic templates
are the fallback. When a provider is configured, the script and title
generators swap to that provider for higher-quality output.

Provider precedence (first match wins):

    1. Anthropic Claude     (ANTHROPIC_API_KEY + `pip install anthropic`)
    2. Google Gemini        (GOOGLE_API_KEY    + `pip install google-generativeai`)

Gemini is the recommended free option — Google's free tier on
`gemini-2.0-flash` covers 15 requests / minute and 1,500 / day with
no credit card. Get a key at https://aistudio.google.com/app/apikey.

Failure mode:
    Any error during the API call returns None. The caller falls
    back to the deterministic template silently — the system never
    breaks because the API is unreachable.
"""

from __future__ import annotations

import os

try:
    from anthropic import Anthropic  # type: ignore
    _HAS_ANTHROPIC = True
except ImportError:
    Anthropic = None  # type: ignore
    _HAS_ANTHROPIC = False

# Two Google SDKs exist:
#   - google-genai (NEW, preferred — the supported path going forward)
#   - google-generativeai (LEGACY, deprecated by Google but still works)
# Prefer the new one when both are installed.
_GEMINI_SDK: str | None = None
try:
    from google import genai as google_genai  # type: ignore  # new SDK
    _GEMINI_SDK = "google-genai"
except ImportError:
    google_genai = None  # type: ignore
    try:
        import google.generativeai as legacy_genai  # type: ignore
        _GEMINI_SDK = "google-generativeai"
    except ImportError:
        legacy_genai = None  # type: ignore

_HAS_GEMINI = _GEMINI_SDK is not None


# Override these via env if you want a different model.
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


# Most recent provider error message. Set by the call wrappers, read
# by the /health/llm endpoint so the UI can show the actual failure
# reason instead of a silent fall-through.
_last_error: str | None = None


def last_error() -> str | None:
    """Return the most recent provider error message, or None."""
    return _last_error


def active_provider() -> str | None:
    """Return 'anthropic', 'google', or None."""
    if _HAS_ANTHROPIC and os.environ.get("ANTHROPIC_API_KEY", "").strip():
        return "anthropic"
    if _HAS_GEMINI and os.environ.get("GOOGLE_API_KEY", "").strip():
        return "google"
    return None


def is_available() -> bool:
    """True when any supported provider is configured."""
    return active_provider() is not None


def provider_label() -> str:
    """Human-readable label for the UI pill."""
    p = active_provider()
    if p == "anthropic":
        return f"claude — {ANTHROPIC_MODEL}"
    if p == "google":
        return f"gemini — {GEMINI_MODEL}"
    return "local mode"


# ---------------------------------------------------------------------------
# Provider call wrappers
# ---------------------------------------------------------------------------

def _call_anthropic(system: str, prompt: str, max_tokens: int) -> str | None:
    global _last_error
    try:
        client = Anthropic()
        msg = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        _last_error = None
        return msg.content[0].text  # type: ignore[index]
    except Exception as e:
        _last_error = f"{type(e).__name__}: {e}"
        return None


def _call_gemini(system: str, prompt: str, max_tokens: int) -> str | None:
    """Dispatch the call to whichever Gemini SDK is installed.

    Prefers the new `google-genai` SDK when present; falls back to the
    deprecated `google-generativeai` SDK for backward compatibility.
    """
    global _last_error
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        _last_error = "GOOGLE_API_KEY is not set."
        return None

    try:
        if _GEMINI_SDK == "google-genai":
            client = google_genai.Client(api_key=api_key)  # type: ignore
            response = client.models.generate_content(  # type: ignore
                model=GEMINI_MODEL,
                contents=prompt,
                config={
                    "system_instruction": system,
                    "max_output_tokens": max_tokens,
                    "temperature": 0.85,
                },
            )
            text = getattr(response, "text", None)

        elif _GEMINI_SDK == "google-generativeai":
            legacy_genai.configure(api_key=api_key)  # type: ignore
            model = legacy_genai.GenerativeModel(  # type: ignore
                GEMINI_MODEL,
                system_instruction=system,
            )
            response = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.85,
                },
            )
            # Legacy SDK raises on `.text` access if the response was
            # blocked by a safety filter — treat that as an error.
            try:
                text = response.text
            except Exception as inner:
                _last_error = (
                    f"empty response (likely blocked): "
                    f"{type(inner).__name__}: {inner}"
                )
                return None

        else:
            _last_error = (
                "No Gemini SDK installed. Run "
                "`pip install google-genai`."
            )
            return None

        if not text:
            _last_error = "Empty response from Gemini."
            return None
        _last_error = None
        return text

    except Exception as e:
        _last_error = f"{type(e).__name__}: {e}"
        return None


def _call(system: str, prompt: str, max_tokens: int = 4096) -> str | None:
    """Dispatch to whichever provider is currently active."""
    p = active_provider()
    if p == "anthropic":
        return _call_anthropic(system, prompt, max_tokens)
    if p == "google":
        return _call_gemini(system, prompt, max_tokens)
    return None


# ---------------------------------------------------------------------------
# Public API used by generators
# ---------------------------------------------------------------------------

def generate_script(card: dict) -> str | None:
    """Use the active LLM to write the full script. None on failure."""
    if not is_available():
        return None

    system = (
        "You are a senior documentary YouTube writer.\n"
        "\n"
        "WRITING RULES:\n"
        "- No AI tone. No 'in conclusion'. No 'in this video'.\n"
        "  No 'let's dive in'. No 'fascinating'. No 'amazing'.\n"
        "- No bullet-list feel. The document is markdown, but the\n"
        "  prose itself must read like spoken paragraphs, not\n"
        "  bulleted points.\n"
        "- Short sentences only. Spoken rhythm.\n"
        "- Every paragraph must create curiosity or tension.\n"
        "  No filler paragraphs. No paragraph that just\n"
        "  re-states what was said.\n"
        "- Never explain directly. Reveal gradually. Lead the\n"
        "  audience to the conclusion one half-step at a time.\n"
        "- Use contrast pairs sparingly: 'At first... but...' /\n"
        "  'On paper this looks simple. The reality is stranger.'\n"
        "- Natural transitions only: 'At first...',\n"
        "  'But here's the catch...', 'That's where things\n"
        "  change.', 'On paper this looks simple.', 'Here's the\n"
        "  part most people miss.'\n"
        "- Editorial frame: **invisible systems / hidden-truth\n"
        "  storytelling**. Show the audience something that was\n"
        "  always in front of them, that they never quite saw.\n"
        "\n"
        "MONETIZATION SAFETY:\n"
        "- Original narration only. Do not paraphrase any single\n"
        "  source closely.\n"
        "- No fabricated statistics. If the topic needs a number\n"
        "  you don't know, write around it ('roughly', 'a small\n"
        "  number of', 'most') rather than inventing a precise\n"
        "  figure.\n"
        "- Educational documentary framing. No defamation, no\n"
        "  unverified claims about specific people or companies.\n"
        "\n"
        "SOUND LIKE: a thoughtful narrator who recently learned\n"
        "this and is explaining it to a curious friend in their\n"
        "kitchen. Calm. Specific. Slightly unsettled by what\n"
        "they've found."
    )

    length_targets = {
        "short": ("3–4 minutes", "500–700 words"),
        "standard": ("6–8 minutes", "900–1200 words"),
        "deep_dive": ("10–12 minutes", "1400–1800 words"),
    }
    runtime, words = length_targets.get(
        card.get("video_length", "standard"), length_targets["standard"]
    )
    tone = card.get("tone", "documentary")
    prompt = (
        f"Topic: {card.get('raw_topic')}\n"
        f"Subject (noun phrase): {card.get('subject')}\n"
        f"Tone: {tone}\n"
        f"Target runtime: {runtime}\n"
        f"Target length: {words}\n\n"
        "Write the full script in markdown.\n\n"
        "STRUCTURE (use these exact H2 headers, in this order):\n"
        "## HOOK\n"
        "    2–4 short lines. State the everyday picture the\n"
        "    audience holds about the topic, then break it.\n"
        "## MYSTERY\n"
        "    A few short paragraphs that pose the question the\n"
        "    rest of the script will answer. Don't answer it yet.\n"
        "    Build the feeling that something doesn't add up.\n"
        "## SYSTEM EXPLANATION\n"
        "    Explain how the thing actually works, in plain\n"
        "    language. A narrator's explanation, not a textbook.\n"
        "    Reveal one half-step at a time.\n"
        "## HIDDEN TRUTH\n"
        "    The reveal. The thing the audience didn't know.\n"
        "    The part that recontextualises everything before it.\n"
        "## IMPACT\n"
        "    Why this matters now. Connect the hidden truth to\n"
        "    something the audience already cares about. Stakes,\n"
        "    not panic.\n"
        "## FINAL INSIGHT\n"
        "    One strong reflective line — the kind a viewer\n"
        "    would repeat to someone else the next day. No\n"
        "    summary. Let it land.\n\n"
        f"Begin with: # Script: {card.get('raw_topic')}\n"
        f"Then a one-line italic note: *Estimated runtime: {runtime}.*\n"
        "Then the H2 sections. Output only the markdown — no\n"
        "preamble, no section descriptions, just header + prose."
    )

    return _call(system, prompt, max_tokens=4096)


def list_gemini_models() -> list[dict] | None:
    """Return [{name, supports_generate, display_name}, ...] for the active key.

    Used by the UI's "List models" button to discover which model IDs
    actually work with the user's project/region — model availability
    varies by both account and region. None on any failure.
    """
    global _last_error
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        _last_error = "GOOGLE_API_KEY is not set."
        return None
    if not _HAS_GEMINI:
        _last_error = (
            "No Gemini SDK installed. Run `pip install google-genai`."
        )
        return None

    try:
        if _GEMINI_SDK == "google-genai":
            client = google_genai.Client(api_key=api_key)  # type: ignore
            out: list[dict] = []
            for m in client.models.list():  # type: ignore
                # The new SDK's Model objects expose `supported_actions`
                # rather than the legacy `supported_generation_methods`.
                actions = getattr(m, "supported_actions", []) or []
                out.append({
                    "name": getattr(m, "name", str(m)),
                    "display_name": getattr(m, "display_name", None),
                    "supports_generate": (
                        "generateContent" in actions or not actions
                    ),
                })
            _last_error = None
            return out

        if _GEMINI_SDK == "google-generativeai":
            legacy_genai.configure(api_key=api_key)  # type: ignore
            out = []
            for m in legacy_genai.list_models():  # type: ignore
                methods = getattr(m, "supported_generation_methods", []) or []
                out.append({
                    "name": m.name,
                    "display_name": getattr(m, "display_name", None),
                    "supports_generate": "generateContent" in methods,
                })
            _last_error = None
            return out

        _last_error = "Unknown Gemini SDK state."
        return None
    except Exception as e:
        _last_error = f"list_models: {type(e).__name__}: {e}"
        return None


def refine_titles(card: dict, draft_titles_md: str) -> str | None:
    """Pass deterministic titles through the LLM for sharpening."""
    if not is_available():
        return None

    system = (
        "You are a YouTube CTR specialist. You sharpen titles "
        "and narration hooks until they feel native to YouTube. "
        "Curiosity over hype. Specificity over abstraction. "
        "No clickbait exaggeration. No emoji. No all-caps. "
        "Keep titles under 70 characters."
    )
    prompt = (
        f"Topic: {card.get('raw_topic')}\n\n"
        "Below is a draft titles file. Sharpen it. Keep the same "
        "structure (12 titles across 6 categories + 5 narration "
        "hooks). Tighten the prose. Remove anything generic. "
        "Output only the refined markdown.\n\n"
        "---\n"
        f"{draft_titles_md}"
    )
    return _call(system, prompt, max_tokens=2048)
