# YouTube Content Agent — Faceless Documentary Production Pipeline

> **Turn one topic into a complete YouTube production pack — script, storyboard,
> AI image & video prompts, thumbnail concept, viral shorts, SEO metadata, and a
> step-by-step CapCut edit guide. Self-hosted Python web app, free to run, optional
> Gemini or Claude integration for higher-quality scripts.**

[![GitHub stars](https://img.shields.io/github/stars/prashantsinghmangat/youtube-content-agent?style=social)](https://github.com/prashantsinghmangat/youtube-content-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/built%20with-Flask-000.svg)](https://flask.palletsprojects.com/)
[![Local-first](https://img.shields.io/badge/local--first-✓-green.svg)](#)
[![Author](https://img.shields.io/badge/author-Prashant%20Singh-blueviolet.svg)](https://prashantsinghmangat.netlify.app/)

YouTube Content Agent is a **local-first, open-source content production system**
built for faceless YouTube documentary channels. Type a topic, pick a video
length, click generate. Ten markdown files come out — ready to feed into
Midjourney, Leonardo, Ideogram, Runway, Pika, ElevenLabs, CapCut, and YouTube
Studio.

It is **not a chatbot wrapper**. The pipeline is deterministic, scene-aware, and
length-aware. Same topic produces the same output. Optional Gemini or Claude
hybrid mode upgrades only the script writer and the title refiner — everything
else stays on a fast, predictable local template path.

[**📁 See the bundled sample output →**](outputs/sample_undersea-cables/)

---

## Table of contents

- [Who this is for](#who-this-is-for)
- [What you get for one topic](#what-you-get-for-one-topic)
- [Features](#features)
- [Quick start (Windows)](#quick-start-windows)
- [Run](#run)
- [Optional — enable LLM hybrid mode](#optional--enable-llm-hybrid-mode)
- [Configuration](#configuration)
- [Project structure](#project-structure)
- [How it works](#how-it-works)
- [Adding a new seed topic](#adding-a-new-seed-topic)
- [FAQ](#faq)
- [GitHub topics](#github-topics)
- [Versions](#versions)
- [Author](#author)
- [License](#license)

---

## Who this is for

- **Faceless YouTube documentary creators** who want to batch-produce systems / hidden-truth / mystery / explainer videos.
- **Solo content creators** replacing manual scripting and storyboarding with a deterministic pipeline.
- **AI-video producers** using Midjourney, Leonardo, Ideogram, Runway, Pika, or Luma who need consistent per-scene prompts at the right aspect ratio.
- **YouTube SEO operators** who want production-ready titles, descriptions, tags, and posting-time recommendations from a single command.
- **CapCut editors** who want timeline guides, B-roll suggestions, and music style direction shipped alongside the script.

---

## What you get for one topic

For every generation the system writes **10 markdown files** to a timestamped folder under `./outputs/`:

| # | File              | Role                                                                                       |
|---|-------------------|--------------------------------------------------------------------------------------------|
| 1 | `idea.md`         | One refined viral concept — hook angle + emotional curiosity angle                         |
| 2 | `titles.md`       | 12 CTR-optimised YouTube titles (across 6 categories) + 5 narration hooks                  |
| 3 | `thumbnail.md`    | Concept + composition + text overlay + colour direction + ready-to-paste AI image prompt   |
| 4 | `script.md`       | A 6–8 minute spoken documentary script (length-aware: short, standard, deep-dive)          |
| 5 | `storyboard.md`   | Script broken into 5–10 second visual segments with footage type per scene                 |
| 6 | `ai_prompts.md`   | One image prompt + one video prompt per scene, framed for **16:9 horizontal at 1920×1080+**|
| 7 | `shorts.md`       | 5–8 standalone vertical YouTube Shorts (**9:16 1080×1920**) derived from the long-form     |
| 8 | `upload.md`       | YouTube SEO description + 18 tags + hashtags + filename + posting-time recommendation      |
| 9 | `capcut.md`       | CapCut timeline + transitions + B-roll suggestions + subtitle style + SFX + music style    |
| 10| `workflow.md`    | Step-by-step execution guide + clickable tools panel (Claude, Gemini, Leonardo, Runway, …) |

[Open the bundled `script.md` →](outputs/sample_undersea-cables/script.md) to see the writing bar the system targets.

---

## Features

- **🎯 Topic → 10-file production pack** in one click.
- **📏 Three video lengths** — `short` (3–4 min, 13 scenes), `standard` (6–8 min, 25 scenes), `deep_dive` (10–12 min, 40 scenes). Length controls script length, scene count, AI prompt count, and CapCut cut pacing automatically.
- **🎨 Tone selector** — `analytical` / `curious` / `tense` / `documentary`.
- **🤖 Optional LLM hybrid mode** — defaults to deterministic templates; plug in **Gemini (free)** or **Claude (paid)** to upgrade the script writer and the title refiner. Storyboard, AI prompts, SEO, and workflow stay local either way.
- **📺 YouTube-ready prompts** — every image and video prompt is framed for 16:9 horizontal long-form. Thumbnail prompts include burned-in headline text + runtime label. Shorts pack ships at 9:16 vertical.
- **🔍 Connection diagnostics** — built-in **Test connection** and **List models** buttons hit `/health/llm` and `/health/models`. See exactly which provider is active, which models your API key can call, and the actual error if something fails.
- **👁️ File viewer** — every output file has **View** (clean text), **MD** (raw markdown), and **Copy** buttons in the UI. No need to open Windows Explorer.
- **♻️ Reset button** — clears the form and collapses every result panel without a page reload.
- **🔁 Determinism** — same input produces the same output (except the timestamp in the folder name). No randomness, no flaky generations.
- **⚛️ Atomic writes** — every file stages to `.tmp` and renames into place. An interrupted run never leaves half-written markdown.
- **🚫 No vendor lock-in** — runs fully offline by default. Use any AI image / video / voice tool downstream.

---

## Quick start (Windows)

```powershell
git clone https://github.com/prashantsinghmangat/youtube-content-agent.git
cd youtube-content-agent

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks the activation script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**Requirements**

- Windows 10 / 11 (macOS and Linux work too — adjust the venv activation path)
- Python 3.11 or newer
- ~10 MB of disk space

---

## Run

```powershell
python app.py
```

Open <http://127.0.0.1:5000>, type a topic, pick a length, click **Generate pack**.
`Ctrl+C` in the terminal stops the server.

---

## Optional — enable LLM hybrid mode

The system runs without any LLM. Configure either provider to upgrade the script writer and the title refiner.

### Free — Google Gemini (recommended)

Free tier: **15 requests/minute, 1,500 requests/day** on `gemini-flash-latest`. No credit card required.

1. Get a key at <https://aistudio.google.com/app/apikey> → **Create API key in new project**.
2. Install the SDK and set the env var **in the same shell** you'll run `app.py` from:

   ```powershell
   pip install google-genai
   $env:GOOGLE_API_KEY = "AIza..."
   $env:GEMINI_MODEL = "gemini-flash-latest"   # optional override
   python app.py
   ```

The legacy `google-generativeai` SDK also works — the system auto-detects whichever is installed.

### Paid — Anthropic Claude

```powershell
pip install anthropic
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:ANTHROPIC_MODEL = "claude-sonnet-4-5"    # optional override
python app.py
```

If both keys are set, Anthropic takes precedence. To force Gemini, unset the Anthropic key: `$env:ANTHROPIC_API_KEY = $null`.

### Verify the connection

In the UI, click **Test connection** (next to the header pill). You should see:

```
✓ active provider              google
✓ google SDK installed         google-genai
✓ google key set               true
✓ live API call                succeeded
✓ test reply                   OK
```

If the live call fails, the panel surfaces the actual provider error message.
Click **List models** to see which model IDs your key can call.

---

## Configuration

| Variable             | Purpose                                                | Default                |
|----------------------|--------------------------------------------------------|------------------------|
| `GOOGLE_API_KEY`     | Enables Gemini provider                                | unset                  |
| `GEMINI_MODEL`       | Override the Gemini model                              | `gemini-2.0-flash`     |
| `ANTHROPIC_API_KEY`  | Enables Claude provider (precedence over Gemini)       | unset                  |
| `ANTHROPIC_MODEL`    | Override the Claude model                              | `claude-sonnet-4-5`    |

To switch the server port, edit the `app.run(...)` call at the bottom of `app.py`.

---

## Project structure

```
youtube-content-agent/
├── app.py                       # Flask entry + /health/llm + /health/models routes
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── src/
│   ├── pipeline.py              # Topic → 10-file pack orchestration
│   ├── prompts.py               # Templates + scene library + seed library
│   ├── llm.py                   # Optional Anthropic / Gemini hybrid (auto-detect)
│   │
│   ├── generators/              # One module per output file (10 generators)
│   │   ├── idea.py
│   │   ├── titles.py
│   │   ├── thumbnail.py
│   │   ├── script.py
│   │   ├── storyboard.py
│   │   ├── ai_prompts.py
│   │   ├── shorts.py
│   │   ├── upload.py
│   │   ├── capcut.py
│   │   └── workflow.py
│   │
│   └── utils/
│       ├── io.py                # Atomic file writes
│       └── timestamp.py         # Folder naming
│
├── templates/
│   └── index.html               # Single-page web UI (no JS framework)
│
└── outputs/
    └── sample_undersea-cables/  # Bundled sample output (10 markdown files)
```

---

## How it works

The pipeline is a thin orchestrator. For each topic:

1. **Parse the topic** — strip question prefixes (`Why`, `How`, `What`) and leading determiners (`most`, `the`) to derive a clean noun-phrase subject.
2. **Match against `SEED_LIBRARY`** in `src/prompts.py`. If the seed's declared length matches the requested length, emit hand-curated content for every section. Otherwise fall through to the generic length-aware path.
3. **Render from a single 40-scene `GENERIC_SCENES` list.** Each scene declares a `tier` (1, 2, or 3); the slicer picks scenes by tier to match the requested video length: 13 / 25 / 40 scenes for short / standard / deep_dive. The same list drives both `storyboard.md` and `ai_prompts.md`, so scene counts always align.
4. **Optionally swap in an LLM** — if `GOOGLE_API_KEY` or `ANTHROPIC_API_KEY` is set, `script.py` and `titles.py` use the API for generation. Failures fall through silently to templates — the pipeline never breaks because of an unreachable API.
5. **Atomic write** — all ten files are written to a timestamped folder under `./outputs/`. The result panel surfaces which generator path was used per file (`seed`, `llm:google`, `llm:anthropic`, or `template`).

---

## Adding a new seed topic

Open `src/prompts.py`, find `SEED_LIBRARY`, and add an entry:

```python
"my_topic_id": {
    "match_keywords": ["topic phrase", "alternate phrasing"],
    "subject": "topic as a noun phrase",
    "subject_short": "the thing",
    "length": "standard",        # or "short" / "deep_dive"
    "idea_md":      """# Refined Idea: ...""",
    "titles_md":    """# Titles: ...""",
    "thumbnail_md": """# Thumbnail Strategy: ...""",
    "script_md":    """# Script: ...""",
    "storyboard_md":"""# Storyboard: ...""",
    "ai_prompts_md":"""# AI Prompts: ...""",
    "shorts_md":    """# Shorts Pack: ...""",
    "upload_md":    """# Upload Pack: ...""",
    "capcut_md":    """# CapCut Edit Guide: ...""",
    "workflow_md":  """# Workflow & Tools: ...""",
}
```

Any topic input containing one of `match_keywords` (case-insensitive substring) routes to this entry when the requested video length matches `length`. Otherwise the generic path is used.

---

## FAQ

**Is this a YouTube script generator?**
Yes — and storyboard generator, AI prompt generator, thumbnail prompt generator, SEO description generator, CapCut edit-guide generator, and Shorts extractor. One topic produces all of it together.

**Does it work without an API key?**
Yes. The default path is fully deterministic — no network calls, no API keys, no quotas. Optional Gemini or Claude integration only upgrades the script writer and the title refiner.

**How is this different from ChatGPT writing my script?**
ChatGPT gives you a script. This gives you a **production pack** — script *plus* matching storyboard, *plus* per-scene image and video prompts at the right aspect ratio, *plus* shorts, *plus* upload metadata, *plus* a CapCut edit guide — all numbered and aligned so an editor can drop AI clips straight into a timeline.

**Can I use this for YouTube Shorts only?**
The system optimises for long-form 16:9 first and re-frames Shorts from the same horizontal clips in `shorts.md`. If you produce only Shorts, you'd typically run `short` length and skip the long-form export step.

**Is it monetisation-safe?**
The script LLM system prompt enforces original narration, no fabricated statistics, and educational documentary framing. Combined with the stylistic rules (no AI tone, gradual reveal, contrast pairs), output is structured to meet YouTube's monetisation policies for original educational content. You're still responsible for fact-checking and rights clearance on any visuals you generate.

**What AI tools does the workflow integrate with?**
Image: **Midjourney**, **Leonardo**, **Ideogram**, **Bing Image Creator**.
Video: **Runway**, **Pika**, **Luma**.
Voice: **ElevenLabs**, **PlayHT**.
Script (optional): **Claude**, **Gemini**, **ChatGPT**, **Grok**.
Editing: **CapCut**, **Canva**.
YouTube: **YouTube Studio**, **VidIQ**, **TubeBuddy**.

The `workflow.md` file ships clickable links to every tool, mapped to the step in the pipeline where each one is used.

**Why Flask and not React/Next.js?**
Single-page UI, no JS framework, no build step. Clone, install, run. The whole web layer is one HTML file.

---

## GitHub topics

When you publish this repo, set these topics in the repository settings to surface the project in GitHub search:

```
youtube
youtube-automation
youtube-content-creator
faceless-youtube
content-pipeline
script-generator
storyboard-generator
ai-prompts
documentary
viral-shorts
seo-tools
capcut
midjourney
runway
gemini-api
anthropic-claude
python
flask
self-hosted
local-first
```

And in the repo description (the short tagline shown at the top of the GitHub page):

> Local-first YouTube content production tool. Topic → script + storyboard + AI prompts + thumbnail + shorts + SEO + CapCut guide. Optional Gemini/Claude integration. Faceless documentary channels.

---

## Versions

| Version | Highlights                                                                                  |
|---------|---------------------------------------------------------------------------------------------|
| 4.1     | LLM error reporting, `/health/models` lister, Reset button, both Gemini SDKs supported      |
| 4.0     | Video-length system, LLM hybrid mode, file viewer, `/health/llm`                            |
| 3.0     | Strict 9-file pack, per-scene AI prompts, scene library, workflow dashboard                 |
| 2.0     | One file per role (added thumbnail, ideas, shorts, editing); 12-title format                |
| 1.0     | 6-file editorial pack (research, angle, titles, script, storyboard, assets)                 |

---

## Author

Built and maintained by **Prashant Singh**.

- GitHub: [@prashantsinghmangat](https://github.com/prashantsinghmangat)
- Repository: [github.com/prashantsinghmangat/youtube-content-agent](https://github.com/prashantsinghmangat/youtube-content-agent)
- Portfolio: [prashantsinghmangat.netlify.app](https://prashantsinghmangat.netlify.app/)

If this saved you hours of manual scripting and storyboarding, a ⭐ on GitHub
helps other creators find it.

---

## License

[MIT](LICENSE) — free for personal and commercial use.
