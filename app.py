"""Flask entry point for youtube-content-agent.

Run:
    python app.py

Then open http://127.0.0.1:5000 in a browser.

The app keeps state in the local filesystem under ./outputs/. There
is no database, no browser automation. External APIs are optional:
the deterministic template path runs without anything but Flask.
"""

from __future__ import annotations

import re
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request

from src import llm
from src.pipeline import SUPPORTED_TONES, generate_pack
from src.prompts import SUPPORTED_LENGTHS


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"
OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)


app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "templates"),
)


_SAFE_NAME = re.compile(r"^[\w\-.]+$")


def _safe_path(folder: str, filename: str) -> Path:
    """Resolve a request path safely inside OUTPUTS_ROOT.

    Rejects anything with path separators, dot-segments, or
    non-allowed characters. Resolves the final path and confirms
    it stays under OUTPUTS_ROOT.
    """
    if not _SAFE_NAME.match(folder or ""):
        abort(400, "Invalid folder name.")
    if not _SAFE_NAME.match(filename or ""):
        abort(400, "Invalid file name.")
    if not filename.endswith(".md"):
        abort(400, "Only .md files can be served.")
    candidate = (OUTPUTS_ROOT / folder / filename).resolve()
    try:
        candidate.relative_to(OUTPUTS_ROOT.resolve())
    except ValueError:
        abort(400, "Path escapes outputs directory.")
    if not candidate.is_file():
        abort(404, "File not found.")
    return candidate


@app.get("/")
def index():
    return render_template(
        "index.html",
        tones=SUPPORTED_TONES,
        lengths=SUPPORTED_LENGTHS,
        topic="",
        selected_tone="documentary",
        selected_length="standard",
        status=None,
        result=None,
        error=None,
        llm_available=llm.is_available(),
        llm_label=llm.provider_label(),
    )


@app.post("/generate")
def generate():
    topic = (request.form.get("topic") or "").strip()
    tone = (request.form.get("tone") or "documentary").strip().lower()
    video_length = (
        request.form.get("video_length") or "standard"
    ).strip().lower()

    if not topic:
        return render_template(
            "index.html",
            tones=SUPPORTED_TONES,
            lengths=SUPPORTED_LENGTHS,
            topic="",
            selected_tone=tone,
            selected_length=video_length,
            status=None,
            result=None,
            error="Please enter a topic.",
            llm_available=llm.is_available(),
        llm_label=llm.provider_label(),
        ), 400

    try:
        result = generate_pack(topic, tone, OUTPUTS_ROOT, video_length)
    except Exception as exc:
        return render_template(
            "index.html",
            tones=SUPPORTED_TONES,
            lengths=SUPPORTED_LENGTHS,
            topic=topic,
            selected_tone=tone,
            selected_length=video_length,
            status="failed",
            result=None,
            error=f"Generation failed: {exc}",
            llm_available=llm.is_available(),
        llm_label=llm.provider_label(),
        ), 500

    folder_basename = result.folder.name
    rel_folder = result.folder.relative_to(PROJECT_ROOT).as_posix()
    return render_template(
        "index.html",
        tones=SUPPORTED_TONES,
        lengths=SUPPORTED_LENGTHS,
        topic=topic,
        selected_tone=tone,
        selected_length=video_length,
        status="complete",
        result={
            "folder_abs": str(result.folder),
            "folder_rel": rel_folder,
            "folder_name": folder_basename,
            "files": result.files,
            "used_seed": result.used_seed,
            "used_llm": result.used_llm,
            "llm_call_succeeded": result.llm_call_succeeded,
            "llm_provider": result.llm_provider,
            "script_source": result.script_source,
            "titles_source": result.titles_source,
            "video_length": result.video_length,
        },
        error=None,
        llm_available=llm.is_available(),
        llm_label=llm.provider_label(),
    )


@app.get("/health/models")
def health_models():
    """List models available for the active Gemini key.

    Calls Google's ListModels endpoint with the user's key and returns
    only the models that support generateContent. Used to diagnose
    'model not found' errors by showing what's actually callable from
    this key + region.
    """
    models = llm.list_gemini_models()
    if models is None:
        return jsonify({
            "models": None,
            "last_error": llm.last_error(),
        })
    # Sort: generate-capable first, then alphabetic.
    models.sort(key=lambda m: (not m.get("supports_generate"), m["name"]))
    return jsonify({
        "models": models,
        "current_model": llm.GEMINI_MODEL,
        "last_error": None,
    })


@app.get("/health/llm")
def health_llm():
    """Self-test endpoint: reports the LLM connection state.

    Use this to verify the API key is loaded and reachable. Returns
    JSON only — no UI. Hit it directly at /health/llm.
    """
    provider = llm.active_provider()
    payload = {
        "provider": provider,
        "label": llm.provider_label(),
        "is_available": llm.is_available(),
        "anthropic_sdk_installed": llm._HAS_ANTHROPIC,
        "google_sdk_installed": llm._HAS_GEMINI,
        "google_sdk_name": llm._GEMINI_SDK,
        "anthropic_key_set": bool(
            (__import__("os").environ.get("ANTHROPIC_API_KEY") or "").strip()
        ),
        "google_key_set": bool(
            (__import__("os").environ.get("GOOGLE_API_KEY") or "").strip()
        ),
        "anthropic_model": llm.ANTHROPIC_MODEL,
        "gemini_model": llm.GEMINI_MODEL,
    }

    # If a provider is configured, fire one tiny test call to confirm
    # the key actually reaches the API. This costs <1 cent on Claude
    # and is free on Gemini's free tier.
    if provider:
        test_response = llm._call(
            system="Reply with the single word: OK.",
            prompt="Test.",
            max_tokens=10,
        )
        payload["live_call_succeeded"] = bool(test_response)
        payload["live_call_response"] = (test_response or "").strip()[:80]
        payload["last_error"] = llm.last_error()
    else:
        payload["live_call_succeeded"] = False
        payload["live_call_response"] = None
        payload["last_error"] = None

    return jsonify(payload)


@app.get("/file/<folder>/<filename>")
def file_content(folder: str, filename: str):
    """Return the raw markdown body of a generated file as JSON.

    Used by the file viewer in the UI (View / MD / Copy modes).
    The viewer renders the markdown client-side.
    """
    path = _safe_path(folder, filename)
    text = path.read_text(encoding="utf-8")
    return jsonify({
        "folder": folder,
        "filename": filename,
        "content": text,
        "bytes": len(text),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
