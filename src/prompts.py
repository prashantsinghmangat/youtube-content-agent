"""Templates and curated content for the youtube-content-agent.

Two layers live here:

1. SEED_LIBRARY — hand-curated, richly written content for known topics.
   Whenever a user's input matches a seed entry, generators emit the
   curated markdown directly. This is the "showcase quality" path.

2. GENERIC_TEMPLATES — structural prose templates for everything else.
   These are written so the substituted output still reads like a
   thoughtful narrator, never a listicle or chatbot. The templates use
   the {subject} field of the topic_card.

The SEPARATION matters. Without an LLM, naive Mad-Libs templates always
sound generic. The seed layer carries the editorial bar; the generic
layer carries the skeleton.
"""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Topic card derivation
# ---------------------------------------------------------------------------

_QUESTION_PREFIXES = re.compile(
    r"^\s*(why does|why do|why is|why are|how does|how do|how is|how are|"
    r"what is|what are|why|how|what|where|when|"
    r"the truth about|the real story of|the secret of|the secret behind|"
    r"inside)\s+",
    re.IGNORECASE,
)

_LEADING_DETERMINERS = {
    "most", "all", "every", "this", "that", "these", "those",
    "many", "some", "the", "a", "an",
}

# Words that mark the boundary between "what we're talking about" and
# "what's being said about it." If we hit one of these, the noun phrase
# has ended. Tuned for explainer-channel topic strings, not full English.
_STOP_VERBS = {
    "is", "are", "was", "were", "be", "being", "been", "am",
    "has", "have", "had",
    "do", "does", "did",
    "will", "would", "can", "could", "should", "may", "might", "must",
    "control", "controls", "controlled",
    "work", "works", "worked",
    "function", "functions", "functioned",
    "operate", "operates", "operated",
    "happen", "happens", "happened",
    "shift", "shifts", "shifted",
    "change", "changes", "changed",
    "fail", "fails", "failed",
    "break", "breaks", "broke", "broken",
    "succeed", "succeeds", "succeeded",
    "rule", "rules", "ruled",
    "run", "runs", "ran",
    "exist", "exists", "existed",
    "become", "becomes", "became",
    "get", "gets", "got",
    "make", "makes", "made",
    "keep", "keeps", "kept",
    "stay", "stays", "stayed",
    "remain", "remains", "remained",
    "fall", "falls", "fell", "fallen",
    "rise", "rises", "rose", "risen",
    "decide", "decides", "decided",
    "decline", "declines", "declined",
    "matter", "matters", "mattered",
    "predict", "predicts", "predicted",
    "explain", "explains", "explained",
    "shape", "shapes", "shaped",
    "drive", "drives", "drove", "driven",
    "stop", "stops", "stopped",
    "start", "starts", "started",
    "kill", "kills", "killed",
    "save", "saves", "saved",
    "cause", "causes", "caused",
    "actually", "really", "quietly", "secretly", "slowly", "almost",
    "barely", "just",
}


def derive_subject(topic: str) -> str:
    """Pull a clean noun-phrase subject out of an arbitrary topic string.

    Examples:
        "Why undersea cables quietly control the internet"
            -> "undersea cables"
        "How weather forecasts actually work"
            -> "weather forecasts"
        "Why most pension funds are quietly underwater"
            -> "pension funds"
        "Pension funds"
            -> "pension funds"
    """
    cleaned = (topic or "").strip().rstrip("?.!")
    cleaned = _QUESTION_PREFIXES.sub("", cleaned, count=1).strip()
    if not cleaned:
        return ((topic or "").strip().lower()) or "this topic"

    words = cleaned.split()
    # Drop a single leading determiner ("most pension funds" -> "pension funds")
    if words and words[0].lower() in _LEADING_DETERMINERS:
        words = words[1:]

    collected: list[str] = []
    for w in words:
        wl = w.lower().rstrip(",.;:")
        # Stop at common stop-verbs / -ly adverbs.
        if wl in _STOP_VERBS:
            break
        if wl.endswith("ly") and len(wl) > 3 and collected:
            break
        collected.append(w)

    result = " ".join(collected) if collected else cleaned
    result = result.rstrip(",.;:").strip()
    if result and result[0].isupper() and not result[:3].isupper():
        result = result[0].lower() + result[1:]
    return result or "this topic"


def derive_short_subject(subject: str) -> str:
    """Tightest possible reference to the topic for repeated mentions.

    Picks the first 2-3 content words; falls back to a generic stand-in.
    """
    words = subject.split()
    if not words:
        return "this system"
    head = " ".join(words[: min(3, len(words))])
    head = head.rstrip(",.;:")
    return head or "this system"


def derive_card(topic: str, tone: str, video_length: str = "standard") -> dict:
    """Build a topic_card for any topic, seed or generic.

    The card is the single source of truth that all generators consume.
    Seed entries override these defaults via SEED_LIBRARY.
    """
    subject = derive_subject(topic)
    return {
        "raw_topic": (topic or "").strip(),
        "subject": subject,
        "subject_short": derive_short_subject(subject),
        "tone": (tone or "documentary").lower().strip(),
        "video_length": video_length,
        "is_seed": False,
    }


# ---------------------------------------------------------------------------
# Video-length system
# ---------------------------------------------------------------------------

SUPPORTED_LENGTHS = ("short", "standard", "deep_dive")

LENGTH_RUNTIME = {
    "short": "3–4 minutes",
    "standard": "6–8 minutes",
    "deep_dive": "10–12 minutes",
}

LENGTH_WORD_TARGET = {
    "short": "500–700 words",
    "standard": "900–1200 words",
    "deep_dive": "1400–1800 words",
}

LENGTH_SCENE_COUNT = {
    "short": 13,
    "standard": 25,
    "deep_dive": 40,
}

# CapCut pacing per length.
LENGTH_CUT_PACING = {
    "short": "fast cuts (2–4 seconds per scene)",
    "standard": "medium pacing (5–7 seconds per scene)",
    "deep_dive": "documentary pacing (8–12 seconds per scene)",
}

# Thumbnail emotional hook style per length.
LENGTH_THUMBNAIL_HOOK = {
    "short": "high-CTR punch hook — one strong shock-of-recognition image, "
             "the text overlay is the line that earns the click in 2 seconds",
    "standard": "scale + mystery hook — one clean image that suggests "
                "something larger and slightly uncomfortable behind it",
    "deep_dive": "curiosity / mystery hook — composition that asks an "
                 "open question the viewer can't answer without watching",
}

# Short numeric runtime label burned into the thumbnail (e.g. "8 MIN").
# Single digit for `short`/`standard`, slightly higher for `deep_dive`.
LENGTH_THUMBNAIL_RUNTIME_LABEL = {
    "short": "4 MIN",
    "standard": "8 MIN",
    "deep_dive": "11 MIN",
}


def length_or_default(length: str | None) -> str:
    if (length or "").lower().strip() in SUPPORTED_LENGTHS:
        return length.lower().strip()
    return "standard"


# ---------------------------------------------------------------------------
# Tone-specific opening lines (used by the generic script generator)
# ---------------------------------------------------------------------------

TONE_OPENERS: dict[str, list[str]] = {
    "documentary": [
        "Most of us go through life never really thinking about {subject}. "
        "That's the strange part. It's everywhere — and almost invisible.",
        "There's a fact about {subject} that even the people closest to it "
        "tend to leave unsaid. Not because it's secret. Because it's "
        "uncomfortable.",
        "The story of {subject} is told in pieces. Each piece sounds "
        "reasonable. Put together, they describe something none of us "
        "quite signed up for.",
    ],
    "curious": [
        "Here's something strange about {subject}.",
        "The first time you really try to understand {subject}, the "
        "explanation falls apart in your hands.",
        "There's a puzzle at the heart of {subject}, and almost no one "
        "talks about it directly.",
    ],
    "tense": [
        "Right now, while you're watching this, something is shifting "
        "around {subject} — and most people aren't noticing it yet.",
        "Something is going wrong with {subject}, and the people closest "
        "to it have started talking about it more carefully than they "
        "used to.",
        "There's a quiet problem inside {subject}. It isn't urgent yet. "
        "That's the part that should worry you.",
    ],
    "analytical": [
        "There are three things you need to understand about {subject}, "
        "and the third one is the one that surprises people.",
        "If you actually look closely at {subject}, a strange pattern "
        "emerges — one that's hard to unsee.",
        "The surface story about {subject} is not wrong. It's incomplete, "
        "in a very specific way.",
    ],
}


# ---------------------------------------------------------------------------
# Generic markdown templates (fallback path)
# ---------------------------------------------------------------------------

GENERIC_IDEA_TEMPLATE = """\
# Refined Idea: {raw_topic}

## The video concept

A 6–8 minute documentary on {subject} that gets the viewer to
feel the gap between the version they think they understand and
the version that's actually true.

The promise to the audience: *by the end of this video, you will
look at {subject} differently — and you won't be able to go back.*

## Hook angle

Open with a contradiction. Say the everyday picture of {subject}
in one sentence, then break it in the next. The first 5–8 seconds
must earn the next 30, and the next 30 must earn the rest of the
video. No throat-clearing. No "in this video..." opening.

## Emotional curiosity angle

The viewer should feel a slow, building unease. Not panic — the
quiet kind of unease that comes from realising a system you
trusted is not what you thought it was. That feeling is what
makes the video get shared. People don't share information; they
share the feeling of having seen something other people haven't.

## Why this concept works

- **Curiosity gap** — the audience already has a mental model of
  {subject}; the video promises to break it.
- **Stakes** — {subject} touches something the audience already
  cares about. That connection has to be made explicit, not
  implied.
- **Visual handle** — the topic gives an editor something
  specific to film, animate, or generate. Abstract topics don't
  retain.
- **Closing payoff** — the viewer leaves with one strong sentence
  they can repeat. That's the unit of word-of-mouth on YouTube.
"""


GENERIC_TITLES_TEMPLATE = """\
# Titles: {raw_topic}

## 12 CTR-Optimized Titles

*Two per category: curiosity gap, hidden truth, contradiction,
fear / risk, "what no one tells you", simple explanation.*

### Curiosity gap
1. The Real Map of {subject_title} Looks Nothing Like You'd Expect
2. There's One Thing About {subject_title} That Almost No One Notices

### Hidden truth
3. The Quiet Truth About {subject_title}
4. The Part of {subject_title} No One Wants to Explain Out Loud

### Contradiction
5. {subject_title} Is Stranger Than You Think
6. The Story Everyone Tells About {subject_title} Is Mostly Wrong

### Fear / risk
7. What Happens When {subject_title} Quietly Breaks
8. {subject_title}: The Failure No One Sees Coming

### What no one tells you
9. {subject_title}: The Version You Don't Hear in the News
10. The Side of {subject_title} You Were Never Told About

### Simple explanation
11. {subject_cap}, Explained in a Way That Actually Makes Sense
12. The One Thing You Need to Understand About {subject_title}

## 5 Narration Hooks

*Opening lines for the script. Each lands in 3–5 seconds.*

1. Most of what you've heard about {subject} is the version that
   fits into a sentence. The version that fits into reality is
   more interesting, and slightly more uncomfortable.

2. There's a story everyone agrees on about {subject}. Then
   there's the story the people closest to it tell more carefully.
   They are not the same story.

3. {subject_cap}: it works. That's the strange part. It works
   under conditions that, if you understood them, you'd be a
   little more nervous about how thin the margins actually are.

4. The picture you have of {subject} is probably about ten years
   out of date. Not because anyone hid the change. Because the
   change happened quietly, and quietly is hard to cover.

5. Here's the question almost no one asks about {subject}: what
   happens when one of the assumptions underneath it stops being
   true? That's the real story.
"""


GENERIC_THUMBNAIL_TEMPLATE = """\
# Thumbnail Strategy: {raw_topic}

*Hook style for this length: {thumbnail_hook}*

## Concept

A single, sharply-lit object that represents {subject} placed
against a quiet, slightly oppressive background. The viewer should
feel one beat of *"wait, that's it?"* before they read a word.

## Emotional Trigger

**Mystery + scale.** The composition should suggest that something
small is responsible for something much larger — that's the
gravitational pull of the topic.

## Visual Composition

- **Foreground (left third):** the single object representing
  {subject}, in sharp focus, slightly off-center.
- **Midground:** soft, atmospheric — particles, dust, water,
  whatever fits the topic. No clutter.
- **Background:** dark, fading toward the edges. One subtle
  light source from the upper right.
- **Subject focus:** the eye must land on the foreground object
  within 0.5 seconds. Test this by looking at the thumbnail at
  thumbnail size, not full size.

## Text Overlay

The thumbnail carries **two text elements**, both burned into the
image:

1. **Headline (2–5 words, max).** A single tight phrase that
   creates tension. Pick one of these for {subject}:
   - `THE QUIET PART`
   - `NO ONE IS WATCHING`
   - `THIS IS IT`
   - `WHAT YOU MISSED`

   Use it in **white condensed sans-serif, slight weathering,
   upper-right or lower-third**.

2. **Runtime label.** `{thumbnail_runtime_label}` — small, in
   the opposite corner from the headline. White on dark, thin
   stroke, ~30% size of the headline. This is the YouTube
   convention for explainer / documentary thumbnails — it
   improves CTR by setting a clear time commitment up front.

Avoid full sentences. Avoid question marks. Avoid more than two
font weights. No yellow highlighter underline.

## Color Direction

Cool dominant palette (deep blue, charcoal, near-black) with
**one** warm accent — a single highlight, not a wash. High
contrast. No teal-and-orange grading; it reads as generic.

## AI Image Prompt

> **Recommended tool: Ideogram** (best at text rendering). If
> the AI output's text comes out mangled, regenerate with
> `no text` appended and add the text yourself in CapCut or
> Canva.

cinematic close-up representing {subject}, **16:9 horizontal
YouTube thumbnail aspect ratio (1280×720)**, single sharply-lit
subject in the foreground, dark atmospheric background with
subtle neon accents, subtle particles or texture in the air,
one warm rim light from upper right, photorealistic, anamorphic
35mm lens, shallow depth of field, ultra-detailed 4K, glowing
infrastructure / data-flow accents, high contrast, mystery and
investigation atmosphere. **Text overlay burned into the image:
white condensed sans-serif headline reading "NO ONE IS WATCHING"
in the upper-right, plus a smaller "{thumbnail_runtime_label}"
runtime label in the bottom-right corner — both white on dark,
crisp legible kerning, slight weathered texture.** No people, no
logos, no other text. Designed for YouTube thumbnail
click-through. --ar 16:9
"""


GENERIC_SHORTS_TEMPLATE = """\
# Shorts Pack: {raw_topic}

*Six standalone vertical clips, each designed to land on its own
as a viral Short. Total runtime: 15–25 seconds each.*

## Format target — YouTube Shorts

| Surface | Aspect ratio | Resolution     |
| ------- | ------------ | -------------- |
| Shorts  | **9:16**     | 1080×1920      |

Shorts are **vertical**, unlike the long-form 16:9 video. In
CapCut, open a **second project at 9:16 1080×1920**, drop in the
relevant scene clips you already generated for the long-form,
zoom + reposition for vertical, burn in subtitles, export.

Do **not** generate separate AI clips for Shorts — re-frame the
horizontal long-form clips you already have. That keeps visual
consistency across the long-form and the Shorts.

---

## Short 1 — The headline contradiction

- **Hook (0–2s):** "The story you've heard about {subject} is
  mostly wrong."
- **Beat 1 (2–7s):** Stylized animation of the "official" version
  of {subject}.
- **Beat 2 (7–14s):** Hard cut to the actual version.
- **Punch (14–20s):** "The interesting truth is the one underneath
  the obvious one."

## Short 2 — The single statistic

- **Hook (0–2s):** "Here's a number about {subject} that should
  surprise you."
- **Beat 1 (2–8s):** Counter ticks up to a key statistic from the
  research brief, with supporting b-roll.
- **Beat 2 (8–14s):** Brief context — why this number is the one
  that matters.
- **Punch (14–20s):** "And almost no one knows it."

## Short 3 — The hidden actor

- **Hook (0–2s):** "Most people don't realize who actually shapes
  {subject}."
- **Beat 1 (2–9s):** Quick reveal of the under-discussed players.
- **Beat 2 (9–14s):** One concrete example of their influence.
- **Punch (14–20s):** "It isn't the names you'd expect."

## Short 4 — The fragility moment

- **Hook (0–2s):** "The system around {subject} bends before it
  breaks. That's the eerie part."
- **Beat 1 (2–9s):** Visualization of the system absorbing stress.
- **Beat 2 (9–15s):** The moment the bending starts to matter.
- **Punch (15–22s):** "By the time you'd feel it, something would
  already be very wrong."

## Short 5 — The one decision

- **Hook (0–2s):** "The shape of {subject} looks like a fact. It's
  actually a decision."
- **Beat 1 (2–8s):** Brief origin moment — when the choice was
  made.
- **Beat 2 (8–15s):** What the alternative would have looked like.
- **Punch (15–22s):** "The shape of the world is full of decisions
  you never voted on."

## Short 6 — The closing thought

- **Hook (0–2s):** "The next time someone explains {subject} in
  one sentence, listen carefully."
- **Beat 1 (2–10s):** Quiet b-roll, slow camera move.
- **Beat 2 (10–16s):** The line under the line — what the
  one-sentence version is leaving out.
- **Punch (16–22s):** "The interesting part is always the part
  they leave out."
"""


GENERIC_SCRIPT_SHORT_BODY = """\
## SETUP

Most people carry a quick mental picture of {subject}. The picture
is reassuring. It's also incomplete in a very specific direction.

This is a short documentary about that direction.

## WHY IT EXISTS

At first, {subject} sounds straightforward. There's a need. There's
a system that fills the need.

But systems don't show up because they're obvious. They show up
because, at some specific moment, a particular choice was made that
seemed less crazy than the alternatives. That choice locks in.
Decades later, the rest of us live inside the consequences and
treat them as fixed facts.

That's the part of {subject} most explanations skip — not what the
system does today, but why it ever started to look this way in the
first place.

## WHAT MOST PEOPLE MISS

Here's the part that surprises people.

The interesting question about {subject} isn't usually the one that
gets asked first. It's the question one layer down — the one you
only notice when you stop accepting the official framing and start
asking who is doing the framing.

Once you do that, the outside view of {subject} starts to look more
interesting than the inside one.

## WHERE IT BECOMES FRAGILE

Now, here's where things get strange.

On paper, {subject} looks robust. The system around it is — but
only under the conditions it was originally built for. Push the
system sideways, and you start to see the seams.

Most of those seams aren't technical. They're human. Quiet
assumptions about how people will behave, what they'll tolerate,
what they'll bother to notice.

When those assumptions stop holding, the system doesn't break with
a bang. It bends.

## WHY IT MATTERS NOW

For a long time, this was a curiosity. Something specialists
thought about, and the rest of us politely ignored.

That window is closing. Several pressures are converging. The
conditions that made {subject} stable are quietly being replaced
by conditions that are not.

## CLOSING

The next time someone tells you the version of {subject} that fits
into a single sentence, you can smile.

It isn't quite that simple. The interesting truth about {subject}
is the one underneath the obvious one. It's quieter. It takes
longer to explain.

But once you see it, you can't unsee it. And you start to notice
similar shapes everywhere.
"""


GENERIC_SCRIPT_BODY = """\
## SETUP

Try this for a moment. Picture the version of {subject} you carry
around in your head. The rough shape of the system. The people
involved. The reasons it works the way it does.

Now hold that picture lightly. Because the moment you actually look
closely at {subject}, that picture starts to come apart in
interesting ways.

This isn't because the surface story is a lie. It's because the
surface story is incomplete in a very specific direction — a
direction that hides the part that's actually surprising.

## WHY IT EXISTS

At first, the idea behind {subject} sounds straightforward. There's
a need. There's a system that fills the need. End of story.

But systems don't show up because they're obvious. They show up
because, at some specific moment, a particular choice was made that
seemed less crazy than the alternatives at hand. Cost. Politics.
Convenience. Sometimes pure accident. That choice locks in. People
build on top of it. And decades later, the rest of us live inside
the consequences and treat them as fixed facts.

That's the part of {subject} most discussions skip. Not the way the
system looks today. Why it ever started to look like this in the
first place.

## WHAT MOST PEOPLE MISS

Here's the part that surprises people.

The interesting question about {subject} isn't usually the one that
gets asked first. It's the question that sits one layer down — the
one you only notice when you stop accepting the official framing and
start asking who is doing the framing, and why.

Once you do that, a few things become clearer.

The story we tell ourselves about {subject} is shaped, much more
than we'd like to admit, by the people who built it. That's not a
conspiracy. It's just gravity. If you spend ten years inside
something, your description of it will reflect what you can see from
the inside, not what it looks like from outside.

The outside view is almost always more interesting.

## WHERE IT BECOMES FRAGILE

Now, here's where things get strange.

On paper, the picture of {subject} looks robust. The system itself
is — but only under the conditions it was originally built for. Push
the system sideways, into territory it wasn't designed for, and you
start to see the seams.

Most of those seams aren't technical. They're human. They're the
quiet assumptions baked into the system about how people will
behave, what they'll tolerate, what they'll bother to notice.

When those assumptions stop holding, the system doesn't break with
a bang. It bends. And the bending is hard to see until it's already
happened.

That's the eerie part. By the time the failure is obvious, the
conditions that caused it have usually already moved on.

## WHY IT MATTERS NOW

For a long time, this would have been an interesting curiosity.
Something specialists thought about, and the rest of us politely
ignored.

That window is closing.

Several pressures are converging at once. The world is connected
differently than it was a decade ago. Information moves differently.
Trust works differently. The conditions that made {subject} stable
are slowly being replaced by conditions that are not.

None of this is panic-worthy on its own. But it is the kind of slow
shift that, if you're not paying attention, you only notice in
hindsight.

So this is the moment to actually pay attention.

## CLOSING

The next time someone tells you the version of {subject} that fits
neatly into a single sentence, you can smile.

It isn't quite that simple.

The interesting truth about {subject} is the one underneath the
obvious one. It's quieter. It takes longer to explain. It doesn't
fit on a poster.

But once you see it, you can't unsee it. And you start to notice
similar shapes everywhere.
"""


GENERIC_SCRIPT_DEEP_DIVE_BODY = """\
## SETUP

Try this for a moment. Picture the version of {subject} you carry
around in your head. The rough shape of the system. The people
involved. The reasons it works the way it does.

Now hold that picture lightly. Because the moment you actually look
closely at {subject}, that picture starts to come apart in
interesting ways.

This isn't because the surface story is a lie. It's because the
surface story is incomplete in a very specific direction — a
direction that hides the part that's actually surprising.

The version most of us inherited came from somewhere. It was
written by people with their own reasons for emphasizing the bits
they emphasized. That doesn't make the version wrong. It makes it
partial. And the partial bit is, almost always, the most
interesting bit.

## WHY IT EXISTS

At first, the idea behind {subject} sounds straightforward. There's
a need. There's a system that fills the need. End of story.

But systems don't show up because they're obvious. They show up
because, at some specific moment, a particular choice was made that
seemed less crazy than the alternatives at hand. Cost. Politics.
Convenience. Sometimes pure accident. That choice locks in. People
build on top of it. And decades later, the rest of us live inside
the consequences and treat them as fixed facts.

You can almost always trace {subject} back to a single decision
point. Sometimes a single person. Often, a single document. The
people involved didn't think they were making the world. They were
solving a specific, narrow problem in front of them. The world that
got built on top of that solution is downstream of decisions they
weren't really making.

That's the part of {subject} most discussions skip. Not the way the
system looks today. Why it ever started to look like this in the
first place.

## WHAT MOST PEOPLE MISS

Here's the part that surprises people.

The interesting question about {subject} isn't usually the one that
gets asked first. It's the question that sits one layer down — the
one you only notice when you stop accepting the official framing and
start asking who is doing the framing, and why.

Once you do that, a few things become clearer.

The story we tell ourselves about {subject} is shaped, much more
than we'd like to admit, by the people who built it. That's not a
conspiracy. It's just gravity. If you spend ten years inside
something, your description of it will reflect what you can see from
the inside, not what it looks like from outside.

The outside view is almost always more interesting.

There's a second layer underneath that. Most of what people argue
about when they argue about {subject} isn't really about {subject}.
It's about adjacent things — money, attention, status, control —
that are easier to talk about through the proxy of {subject} than
to talk about directly. Once you see the proxy, the arguments start
to make a different kind of sense.

## WHERE IT BECOMES FRAGILE

Now, here's where things get strange.

On paper, the picture of {subject} looks robust. The system itself
is — but only under the conditions it was originally built for. Push
the system sideways, into territory it wasn't designed for, and you
start to see the seams.

Most of those seams aren't technical. They're human. They're the
quiet assumptions baked into the system about how people will
behave, what they'll tolerate, what they'll bother to notice.

When those assumptions stop holding, the system doesn't break with
a bang. It bends. And the bending is hard to see until it's already
happened.

That's the eerie part. By the time the failure is obvious, the
conditions that caused it have usually already moved on.

There's another fragility most discussions never reach. The
expertise required to maintain {subject} sits in a small number of
people, almost all of them learning their craft in conditions that
no longer exist. Replacement is harder than it looks. Training is
slower than it looks. And the gap between what the system actually
needs and what the next generation is being prepared to provide is
growing in a direction most observers haven't fully priced in yet.

## WHY IT MATTERS NOW

For a long time, this would have been an interesting curiosity.
Something specialists thought about, and the rest of us politely
ignored.

That window is closing.

Several pressures are converging at once. The world is connected
differently than it was a decade ago. Information moves differently.
Trust works differently. The conditions that made {subject} stable
are slowly being replaced by conditions that are not.

None of this is panic-worthy on its own. But it is the kind of slow
shift that, if you're not paying attention, you only notice in
hindsight.

The interesting question is not whether {subject} will change. It
will. The interesting question is who will be paying attention while
it does. The change is not loud. It happens in small steps that
each, individually, look reasonable. The cumulative direction is
the part that's hard to see in the moment.

So this is the moment to actually pay attention.

## CLOSING

The next time someone tells you the version of {subject} that fits
neatly into a single sentence, you can smile.

It isn't quite that simple.

The interesting truth about {subject} is the one underneath the
obvious one. It's quieter. It takes longer to explain. It doesn't
fit on a poster.

But once you see it, you can't unsee it. And you start to notice
similar shapes everywhere — in the systems around you, in the
stories you've been told about them, in the gap between what you
were told to believe and what is actually happening.

That gap is where the interesting work always lives.
"""


GENERIC_UPLOAD_TEMPLATE = """\
# Upload Pack: {raw_topic}

## SEO description

*(Paste into the YouTube description box. Reads as a human, not a
keyword-stuffed bot. The first three lines are what shows above
the fold — write them like a teaser, not a summary.)*

Most of what we think we know about {subject} is the version that
fits into a sentence. The real story is more interesting, and
slightly more uncomfortable.

This is a 6–8 minute documentary on {subject}. It covers how it
actually works, where the surface story leaves things out, where
the system bends before it breaks, and why this is the moment to
actually pay attention.

Chapters:
00:00 — Hook
00:25 — Setup
01:10 — Why it exists
02:05 — What most people miss
03:00 — Where it becomes fragile
04:30 — Why it matters now
05:45 — Closing

If you found this useful, the rest of the channel covers adjacent
systems most people never look at directly.

—

🎙 Voice-over: human, slow.
🎬 Visuals: AI-generated and stock.
📚 Sources: linked in the pinned comment.

#{subject_hashtag} #documentary #explainer #howitworks #shortdoc

## 18 SEO tags

*(Paste these into the YouTube tags field, one per line or comma-
separated — YouTube accepts both.)*

{subject}
{subject} explained
{subject} documentary
how {subject} works
the truth about {subject}
hidden side of {subject}
{subject} mini documentary
{subject} short documentary
explainer video
faceless youtube
documentary style
behind the system
how it actually works
infrastructure documentary
short documentary
youtube documentary
systems thinking
why it matters

## Hashtags

*(First line of the description. YouTube indexes the first three;
the rest are decorative.)*

#{subject_hashtag} #documentary #explainer #howitworks #shortdoc
#systemsthinking #curiosity #faceless

## Suggested filename

`{subject_slug}_documentary_v1.mp4`

(Replace `v1` with the cut number if you re-export — useful when
you're juggling multiple versions in CapCut.)

## Suggested category

**People & Blogs** *(default)* — broadest recommendation surface
for evergreen explainer content.

Alternative: **Education** if your channel is positioned as
strictly educational. Avoid News & Politics — caps your
long-tail recommendation traffic.

## Posting time recommendation

For an English-speaking audience, post **Tuesday or Thursday at
3pm Eastern (US)**. That window catches:

- the Asia/Pacific evening tail
- the European late evening
- the US afternoon rebound after lunch

Avoid Monday morning (algorithm-cold start) and Friday evening
(weekend competition spike).
"""


GENERIC_CAPCUT_TEMPLATE = """\
# CapCut Edit Guide: {raw_topic}

*Paste this beside the timeline as you assemble the video.*

*Pacing for this length: **{cut_pacing}**.*

## Project setup (do this first)

- **Aspect ratio:** 16:9 (horizontal) — **not** 9:16. Shorts
  go in a separate CapCut project; see `shorts.md`.
- **Resolution:** 1920×1080 (1080p). 3840×2160 (4K) if your
  source clips are 4K.
- **Frame rate:** 24 fps for the cinematic look, or 30 fps if
  your AI-generated clips were rendered at 30.
- **Export preset:** YouTube 1080p, H.264, ~30 Mbps.

If CapCut opens with the Shorts/9:16 default, switch the
canvas to 16:9 before importing any clips.

## Timeline breakdown

The video runs in this order. Drop AI-generated clips into the
slots below, matching scene numbers from `storyboard.md` and
`ai_prompts.md`.

```
0:00–0:25   HOOK              (Scenes 1–3)
0:25–1:10   SETUP             (Scenes 4–5)
1:10–2:05   WHY IT EXISTS     (Scenes 6–7)
2:05–3:00   WHAT MOST MISS    (Scenes 8–10)
3:00–4:30   FRAGILITY         (Scenes 11–14)
4:30–5:45   WHY NOW           (Scenes 15–16)
5:45–6:45   CLOSING           (Scenes 17–19)
```

## Transitions per section

| Section          | Transition                     | Why |
| ---------------- | ------------------------------ | --- |
| HOOK             | Hard cut                       | Three contrasting images stacked tight. No smoothing. |
| SETUP reveal     | Dissolve                       | The expected diagram dissolves into real footage. |
| WHY IT EXISTS    | Cut                            | Documentary feel; resist any zoom transitions. |
| WHAT MOST MISS   | Diagram fade                   | Top layer fades to expose the deeper layer beneath. |
| FRAGILITY        | Slow cut + slight color shift  | Cool color grade kicks in here. |
| WHY NOW          | Cut                            | Modern footage; quick, but not frantic. |
| CLOSING          | Long held shot, no transition  | Just the closing line landing. |

**Avoid in CapCut:** glitch transitions, light leaks, fast zooms,
spinning wipes, anything that screams "TikTok edit". This is a
documentary.

## B-roll suggestions

CapCut → "Stock" tab covers most of these. Pexels and Pixabay
plug-ins inside CapCut handle the rest royalty-free.

- Atmospheric establishing shots tied to {subject}
- Modern interface footage (screens, monitors, dashboards)
- Archival photography for the origin section
- Quiet wide shots for breath beats
- Closeup textures of materials related to {subject}

## Subtitle style guidance

- Font: **white sans-serif, condensed, slight weight**
- Position: **bottom third**, no background bar
- Drop shadow: soft, 30% opacity, 2px offset (legibility on
  bright clips)
- Bold these phrases on screen — these are the rhythmic landing
  points the script is built around:
  - The hook's contradiction line
  - The single most surprising statistic
  - The "here's where things get strange" transition
  - The closing line itself

## SFX suggestions

| Moment                  | SFX                                       |
| ----------------------- | ----------------------------------------- |
| Hook open               | Low ambient drone, 0.5s pre-roll          |
| Section break           | Subtle whoosh OR a moment of silence — never both |
| Major statistic reveal  | One single ping at low volume             |
| Fragility beat          | Distant low rumble, almost subliminal     |
| Closing line            | Total silence — no music, no SFX          |

## Background music style

Reference: **slow Hans Zimmer, but quieter and less dramatic.**

- Genre: ambient cinematic, low-pulsing synth bass
- BPM: 60–80
- Key: minor (C minor / D minor / A minor work well)
- Energy: stays flat. No swells. No drops. No "epic moment."

CapCut "Music" library → search *"ambient cinematic"* or
*"documentary slow"*. Avoid anything tagged *"viral"*, *"epic"*,
or *"trailer"*.

**Drop the music entirely under the closing 30 seconds.** Silence
is the most powerful tool you have at the end.

## Voiceover pacing notes

- **Cadence:** ~140–150 words per minute
- **Breath beats:** hold 1 second of silence at every section break
- **Emphasis:** lower pitch + slight slowdown on key words. Never
  raised volume.
- **Avoid:** rising inflection at line ends, "podcast voice",
  forced energy

If you're using AI voice (ElevenLabs / Speechify), pick a slower
documentary preset and add a 0.5s pause manually at every section
break in the script.
"""


GENERIC_WORKFLOW_TEMPLATE = """\
# Workflow & Tools: {raw_topic}

This is the navigation file. It tells you exactly what to do
with each of the other files in this pack, in the order to do
it, and which external tool to use at each step. Bookmark this
file — it's your dashboard.

---

## EXECUTION WORKFLOW

### Step 1 — Read the concept *(5 min)*

Open `idea.md`. Read it once. Decide whether you're committing
to this video. If yes, continue.

**Tool:** none — judgement call.

### Step 2 — Pick the title *(5 min)*

Open `titles.md`. Pick the title that gives you the strongest
"I'd click that" reaction at thumbnail size, not at full size.

**Tool:** none — read both your gut and the categories.

### Step 3 — Design the thumbnail *(15 min)*

Open `thumbnail.md`. Copy the **AI Image Prompt** at the bottom
of the file.

**Tool:** Leonardo, Ideogram, or Bing Image Creator.

1. Paste the prompt. Generate 4 variants. Pick the strongest.
2. Add the **text overlay** (max 2–5 words from `thumbnail.md`)
   in CapCut or Canva.
3. Export as `thumbnail.jpg` at 1280×720.

### Step 4 — Record the voiceover *(15–25 min)*

Open `script.md`. Copy the entire script body (everything after
the title line).

**Tool:** ElevenLabs or PlayHT for AI voice. Or record your own
in CapCut.

1. Paste the full script.
2. Pick a slower documentary preset.
3. Add a 0.5s pause manually at every section break.
4. Export as a single audio file: `voiceover.mp3`.

### Step 5 — Generate scene visuals *(45–90 min)*

Open `ai_prompts.md`. Read the **Visual style anchor** at the
top — you'll append it to every image prompt.

**Format target: 16:9 horizontal at 1920×1080 minimum (4K
preferred).** This is for the long-form YouTube video, not
Shorts. Set your AI tool's aspect ratio to 16:9 before
generating — most tools default to square (1:1).

For every scene in the file:

1. Copy the **Image Prompt**.
2. Append the **Visual style anchor**.
3. Paste into Midjourney (`--ar 16:9`), Leonardo (16:9 preset),
   or Ideogram (16:9 preset). Generate 4 variants. Pick the
   strongest. Confirm the output is horizontal landscape.
4. Save the still as `scene_XX.png`.
5. Copy the **Video Prompt**.
6. Paste into Runway / Pika / Luma. Set the output aspect ratio
   to **16:9 horizontal**. Use **image-to-video** with the still
   you just generated (preferred), or text-to-video.
7. Save the clip as `scene_XX.mp4` matching the scene number.

Repeat for every scene.

**Tool:** Midjourney / Leonardo / Ideogram for image; Runway /
Pika / Luma for video. **Aspect ratio: 16:9 horizontal**.

### Step 6 — Cut the Shorts *(20 min)*

Open `shorts.md`. Each Short is a standalone vertical clip
(**9:16 1080×1920**, 15–45 seconds).

**Tool:** CapCut. *Open a separate project from the long-form —
do not mix 16:9 and 9:16 in one project.*

1. New CapCut project at **9:16 / 1080×1920**.
2. Pull the relevant 16:9 scene clips you generated in Step 5.
3. Re-frame for vertical: zoom in, reposition the subject to
   the center of the 9:16 canvas.
4. Burn in subtitles, bold the punch line.
5. Export each as `short_XX.mp4` at 1080×1920, H.264.

### Step 7 — Assemble the long-form video *(1–2 hours)*

Open `storyboard.md` (scene-by-scene narration alignment) and
`capcut.md` (transitions, B-roll, subtitle style, SFX, music).

**Tool:** CapCut.

1. New CapCut project at **16:9 / 1920×1080** (or 3840×2160 if
   your scene clips rendered at 4K). Frame rate: 24 fps.
2. Drop scene clips on the timeline in storyboard order. They
   should already be 16:9 horizontal from Step 5.
3. Layer the voiceover audio underneath.
4. Apply transitions per `capcut.md`.
5. Burn in subtitles. Bold the phrases listed in `capcut.md`.
6. Drop the music bed under the script (CapCut Music library).
7. **Drop the music entirely under the closing 30 seconds.**
8. Export at 1080p, H.264, ~30Mbps.

### Step 8 — Upload to YouTube *(10 min)*

Open `upload.md`.

**Tool:** YouTube Studio.

1. Upload the video file.
2. Copy the **SEO description** into the description box.
3. Copy the **18 SEO tags** into the tags field.
4. Set the **filename** as suggested.
5. Set the **category** (Education for evergreen explainer).
6. Set the thumbnail you exported in Step 3.
7. **Schedule** for the time recommended in `upload.md`.

### Step 9 — Optimize after upload *(ongoing)*

Once the video is live, monitor performance and iterate on
title/thumbnail if CTR is below 5% in the first 24 hours.

**Tool:** VidIQ or TubeBuddy.

1. Watch the first-24-hour CTR.
2. If under target, A/B test a different title from `titles.md`.
3. If under target, re-generate the thumbnail with a different
   prompt variation.
4. Use VidIQ tag suggestions to refine future uploads.

---

## TOOLS PANEL

*Production dashboard. Each link opens the canonical product
page. Sign in with your existing accounts.*

### 🧠 Script tools
*(For drafting, refining, or rewriting the script if you want
to vary it from the generated one.)*

- 🤖 [Claude](https://claude.ai) — best for long-form structured writing
- 💬 [ChatGPT](https://chatgpt.com) — broadest model coverage
- ✨ [Gemini](https://gemini.google.com) — Google ecosystem integration
- ⚡ [Grok](https://grok.com) — real-time content awareness

### 🎨 Image tools
*(For thumbnail and per-scene stills — Step 3 and Step 5.)*

- 🦁 [Leonardo](https://leonardo.ai) — fast, reliable, generous free tier
- 🟣 [Ideogram](https://ideogram.ai) — best for text inside images
- 🌐 [Bing Image Creator](https://www.bing.com/images/create) — DALL-E powered, free

### 🎬 Video tools
*(For motion clips per scene — Step 5.)*

- 🎞️ [Runway](https://runwayml.com) — Gen-3 quality, image-to-video
- 🎥 [Pika](https://pika.art) — fast turnaround, motion control
- 💡 [Luma](https://lumalabs.ai/dream-machine) — Dream Machine, photorealistic

### 🎙️ Voice tools
*(For voiceover — Step 4.)*

- 🗣️ [ElevenLabs](https://elevenlabs.io) — best AI voice quality
- 🎤 [PlayHT](https://play.ht) — large voice library, voice cloning

### ✂️ Editing tools
*(For assembly — Step 6 and Step 7.)*

- ✂️ [CapCut](https://www.capcut.com) — primary editor for this workflow
- 🎨 [Canva](https://www.canva.com) — thumbnail polish, text overlays

### 📺 YouTube tools
*(For upload, analytics, and optimization — Step 8 and Step 9.)*

- 📊 [YouTube Studio](https://studio.youtube.com) — upload, schedule, analytics
- 🔍 [VidIQ](https://vidiq.com) — SEO research, A/B testing
- 🚀 [TubeBuddy](https://tubebuddy.com) — keyword research, tag suggestions

---

## How to use this dashboard

- Bookmark this file. Pin the tab.
- Each step above has the tool listed inline. Click the link in
  the panel to open it. Sign in once per session.
- Don't skip Step 5's *Visual style anchor*. Without it, the 28
  separately-generated clips won't feel like the same world.
- Don't paste the script into ChatGPT to "improve" it. The
  script in `script.md` is already tuned for the editorial bar
  this channel is hitting. Improvement requests usually flatten
  the voice.
"""


# ---------------------------------------------------------------------------
# Seed library
# ---------------------------------------------------------------------------
#
# Every seed entry replaces the generic templates above for a specific
# topic. Provide the section bodies as fully-written markdown.

SEED_LIBRARY: dict[str, dict] = {
    "undersea_cables": {
        "match_keywords": [
            "undersea cable",
            "undersea cables",
            "submarine cable",
            "submarine cables",
            "ocean cable",
            "internet cable",
            "sea cable",
            "underwater cable",
        ],
        "subject": "undersea cables",
        "subject_short": "the cables",

        "idea_md": """\
# Refined Idea: Why undersea cables quietly control the internet

## The video concept

A 6–8 minute documentary that reveals the *physical* internet —
the four hundred fiber-optic cables lying on the ocean floor that
carry ninety-nine percent of all intercontinental data, with
almost nothing protecting them.

The promise to the audience: *by the end of this video, you will
never use the word "cloud" the same way again.*

## Hook angle

Open with the contradiction the audience has been carrying
without realising: the internet is somewhere in the air, in the
sky, in the cloud. The first 8 seconds break that picture by
revealing the actual location — a glass thread thinner than a
garden hose, lying in dark sediment on the ocean floor — and the
fact that almost nothing is protecting it.

The hook works because it weaponises a belief the audience
already holds. Most viewers think they know what the internet is.
The video starts by proving they don't.

## Emotional curiosity angle

The viewer should feel a slow, building unease as the scale of
the dependency becomes clear:

1. *Surprise* — wait, the internet is **where**?
2. *Recognition* — banking, hospitals, video calls, stock trades
   — all of that runs on this?
3. *Quiet alarm* — and there are only sixty repair ships in the
   entire world?
4. *Resignation, then resolve* — the closing beat reframes the
   feeling as awareness, not panic.

That arc — from comfortable picture, to unsettled, to clear-eyed
— is the feeling that makes the video get shared. Viewers don't
share information; they share the feeling of having seen the
seam in something other people are still treating as solid.

## Why this concept works

- **Curiosity gap.** Every viewer has a mental model of the
  internet. Almost every model is wrong in the same specific
  direction. The video rewires it in 7 minutes.
- **Stakes.** The connection between the topic and the viewer's
  life is direct: every video call, every payment, every
  cross-border message rides on these cables. No leap required.
- **Visual handle.** Underwater b-roll, animated maps, archival
  cable-ship footage, dramatic scale shots. The topic gives an
  editor more visual material than they can use.
- **Closing payoff.** "The most important infrastructure on
  Earth is sitting in the dark, under the sea, where almost no
  one is watching." That's the unit of word-of-mouth. Viewers
  will repeat it.
""",

        "titles_md": """\
# Titles: Why undersea cables quietly control the internet

## 12 CTR-Optimized Titles

### Curiosity gap
1. The Real Map of the Internet Looks Nothing Like You'd Expect
2. What Happens When You Send a Message Overseas (It's Stranger Than You Think)

### Hidden truth
3. The 400 Cables That Quietly Run the World
4. The Most Important Infrastructure Almost No One Sees

### Contradiction
5. There Is No Cloud — Just Cables, in the Sea, in the Dark
6. Why the Internet Is Wetter Than You Think

### Fear / risk
7. The Internet Is at the Bottom of the Ocean (And Almost Nothing Is Protecting It)
8. Why Cutting an Underwater Cable Could Stall the Global Economy

### What no one tells you
9. The Cables Big Tech Doesn't Want You Thinking About
10. The Aging Ships That Are Quietly Holding the Internet Together

### Simple explanation
11. How a Few Glass Threads on the Seafloor Power the Modern World
12. The 1850s Engineering That Quietly Runs the Modern Internet

## 5 Narration Hooks

1. Right now, while you're watching this, ninety-nine percent of
   all international internet traffic is moving through cables
   thinner than a garden hose, lying on the floor of the ocean.
   Almost nothing is protecting them.

2. The picture you have of the internet — clouds, satellites,
   signals in the air — is almost completely wrong. The actual
   internet is a wet, fragile, deeply physical thing.

3. There are around four hundred cables running across the seafloor.
   Together, they carry banking, streaming, hospital records, and a
   fifth of global stock trades. And only a few dozen ships in the
   world know how to fix them.

4. The next time someone says the internet is in the cloud, ask them
   where the cloud actually lives. The answer will surprise you.
   The internet is at the bottom of the sea.

5. There is a quiet shift happening in who actually owns the
   internet. It isn't the governments. It isn't the telecoms. It's
   the companies whose products you use every day — and they're
   laying cables across the ocean as fast as they can.
""",

        "script_md": """\
# Script: Why undersea cables quietly control the internet

*Estimated runtime: 6–7 minutes.*

## HOOK

Right now, while you're scrolling, almost every message you send
overseas is travelling through a cable thinner than a garden hose,
lying on the floor of the ocean.

Not a satellite. Not the cloud. A cable.

And almost nothing is protecting it.

## SETUP

The picture most of us have of the internet is somewhere up there —
satellites, clouds, signals bouncing through the air. That picture is
almost completely wrong.

The real internet is a wet, fragile, deeply physical thing. It runs
along the seabed. It crosses ocean trenches. It comes ashore in
unmarked buildings on quiet beaches you've probably driven past
without noticing.

There are about four hundred of these cables. Together they carry
around ninety-nine percent of all international data.

That's everything. Banking. Streaming. Video calls. Government
communications. The systems your hospital uses when a scan needs a
second opinion in another country.

All of it. Down there.

## WHY IT EXISTS

At first, this sounds like a strange engineering choice. Why not
satellites?

The answer is brutally simple. Light moving through glass fiber is
faster, cheaper, and a thousand times higher bandwidth than anything
you can beam from orbit. There is no contest. Satellites carry less
than one percent of intercontinental traffic, and that share has
been shrinking, not growing, for decades.

So when you open a video call with someone on another continent,
your face is almost certainly being squeezed into pulses of light,
sent down a glass thread the width of a human hair, travelling under
fishing boats and shipwrecks at two-thirds the speed of light.

It's a strange thing to picture. But that's what's happening.

## WHAT MOST PEOPLE MISS

Here's what surprises people the most.

Nobody really *owns* the internet. But somebody owns the cables.

For most of the twentieth century, governments and big telecom
companies laid them. Now? It's increasingly Google. Meta. Amazon.
Microsoft. The same companies whose products run on the cables are
buying and laying the cables themselves.

That changes the geography of the internet, quietly. A handful of
private companies, headquartered mostly in one country, are
stitching the world together according to where their data centers
happen to be.

Most people don't think about this at all. And the companies, for
the most part, would prefer it stayed that way.

## WHERE IT BECOMES FRAGILE

Now, here's where things get strange.

These cables are not really protected. There is no underwater
fence. There is no patrolling fleet. In international waters, there
is barely any law that would stop someone from cutting them.

Roughly a hundred and fifty cable faults happen every year. Most are
accidents — a fishing trawler dragging a net, a ship dropping anchor
in a bad spot. Sharks have, on occasion, bitten through them.
Engineers eventually added a Kevlar layer.

But the deliberate cuts are the ones people in the industry talk
about quietly.

In 2024, multiple cables in the Red Sea were severed within days of
each other. Roughly a quarter of all Asia-to-Europe internet traffic
ran through that corridor. The traffic re-routed. Latency spiked.
Some services slowed. Most users never noticed.

That's the eerie part. The system is fragile, but it bends before it
breaks. By the time you'd actually feel it, something would have to
go very wrong, in a very specific place, all at once.

There's another fragility most people never hear about. The ships
that repair these cables — the ones that go out into a storm in the
middle of the ocean and try to grab a frayed wire from two miles
down — there are only a few dozen of them in the world. Most are
aging. Some are decades old. The crews are highly specialized and
increasingly hard to replace.

We can lay cables fast. We cannot repair them fast.

## WHY IT MATTERS NOW

For a long time, this didn't really matter. The cables were boring.
They worked. Nobody thought about them.

That window is closing.

Tensions over Taiwan, the Baltic, the Red Sea, the Arctic — every
one of those regions is also a chokepoint for the cables that move
the world's data. Damaging one of them is becoming a tool of
pressure. Not war, exactly. Something quieter than war. Something
that lets a country degrade another country's internet without
firing a shot, and without quite getting caught.

Think about that for a moment. Most of what we call "the global
economy" runs on top of around four hundred glass threads. There is
no Plan B. There is no backup network sitting in orbit. There is no
other internet.

There is just this one. Stretched across the ocean floor. Held
together by maintenance ships from the 1990s and a handful of
engineers who know the routes by heart.

## CLOSING

The next time someone says the internet is in the cloud, you can
smile.

It isn't.

It's at the bottom of the ocean. And the more you learn about it,
the more you realize how much of the modern world is balanced on
something we almost never look at, almost never name, and almost
never protect.

That's the strange truth.

The most important infrastructure on Earth is sitting in the dark,
under the sea, where almost no one is watching.
""",

        "storyboard_md": """\
# Storyboard: Why undersea cables quietly control the internet

*Estimated total runtime: 6–7 minutes.*
*Each segment: 5–10 seconds unless noted.*

## Segment 1 — Hook open

- **Narration:** "Right now, while you're scrolling, almost every
  message you send overseas is travelling through a cable thinner
  than a garden hose, lying on the floor of the ocean."
- **Visual:** Slow push-in on dark ocean water from above; light
  penetrates to the seafloor; final frame settles on a single cable
  in fine sediment.
- **Duration:** 9s
- **Footage type:** Stock — underwater drone

## Segment 2 — Hook contrast

- **Narration:** "Not a satellite. Not the cloud. A cable."
- **Visual:** Three quick contrast cuts — satellite in space, a
  cloud icon, hard cut to a close-up of a cable cross-section.
- **Duration:** 5s
- **Footage type:** Stock + diagram overlay

## Segment 3 — Hook close

- **Narration:** "And almost nothing is protecting it."
- **Visual:** Wide aerial of empty open ocean. Long, quiet hold.
- **Duration:** 5s
- **Footage type:** Stock — aerial ocean

## Segment 4 — Setup A

- **Narration:** "The picture most of us have of the internet is
  somewhere up there — satellites, clouds, signals bouncing through
  the air."
- **Visual:** Stylized animation of stereotypical "internet"
  imagery: wifi waves, cloud icons, orbiting satellites.
- **Duration:** 7s
- **Footage type:** Animated diagram

## Segment 5 — Setup B (the reveal)

- **Narration:** "That picture is almost completely wrong."
- **Visual:** Hard cut. Diagram fades to black. World map fades in
  with submarine cable routes lighting up across all oceans.
- **Duration:** 6s
- **Footage type:** Animated map

## Segment 6 — On the seabed

- **Narration:** "The real internet is a wet, fragile, deeply
  physical thing. It runs along the seabed."
- **Visual:** Slow camera move along a cable on the ocean floor.
  Sediment, fish, faint light.
- **Duration:** 8s
- **Footage type:** Stock — underwater documentary

## Segment 7 — Landing stations

- **Narration:** "It comes ashore in unmarked buildings on quiet
  beaches you've probably driven past without noticing."
- **Visual:** Static of a low concrete building near a beach.
  Slow exterior pan.
- **Duration:** 7s
- **Footage type:** Stock — coastal architecture

## Segment 8 — Scale: 400 cables, 99%

- **Narration:** "There are about four hundred of these cables.
  Together they carry around ninety-nine percent of all
  international data."
- **Visual:** Animated map: cables draw themselves across oceans.
  Counter ticks up to 400. "99%" appears as a lower-third.
- **Duration:** 9s
- **Footage type:** Animated map + lower-third

## Segment 9 — What rides on them

- **Narration:** "That's everything. Banking. Streaming. Video
  calls. Government communications."
- **Visual:** Rapid montage — ATM screen, streaming load bar,
  video call window, government building exterior.
- **Duration:** 7s
- **Footage type:** Stock montage

## Segment 10 — Hospital example

- **Narration:** "The systems your hospital uses when a scan needs
  a second opinion in another country. All of it. Down there."
- **Visual:** Hospital workstation, then a slow dive shot returning
  to the seafloor.
- **Duration:** 8s
- **Footage type:** Stock — medical + underwater

## Segment 11 — Why fiber, not satellites

- **Narration:** "Light moving through glass fiber is faster,
  cheaper, and a thousand times higher bandwidth than anything you
  can beam from orbit."
- **Visual:** Split diagram comparing fiber vs satellite —
  bandwidth bars, latency markers.
- **Duration:** 10s
- **Footage type:** Diagram

## Segment 12 — The 1% factoid

- **Narration:** "Satellites carry less than one percent of
  intercontinental traffic, and that share has been shrinking, not
  growing, for decades."
- **Visual:** Pie chart with 1% slice highlighted; arrow pointing
  down on a small line graph.
- **Duration:** 8s
- **Footage type:** Diagram

## Segment 13 — The video-call image

- **Narration:** "Your face is almost certainly being squeezed into
  pulses of light, sent down a glass thread the width of a human
  hair, travelling under fishing boats and shipwrecks at two-thirds
  the speed of light."
- **Visual:** Custom animated journey — face captured, pixelated,
  transformed into pulses of light, traveling along a fiber under
  trawlers and wrecks, surfacing on the other side.
- **Duration:** 12s (a key emotional beat — let it run long)
- **Footage type:** Custom animation

## Segment 14 — Ownership shift

- **Narration:** "Nobody really owns the internet. But somebody
  owns the cables."
- **Visual:** Slow logo fade-ins on a dark background: Google,
  Meta, Amazon, Microsoft.
- **Duration:** 6s
- **Footage type:** Logo overlay

## Segment 15 — Government → hyperscaler timeline

- **Narration:** "For most of the twentieth century, governments
  and big telecom companies laid them. Now? It's increasingly
  Google. Meta. Amazon. Microsoft."
- **Visual:** Timeline animation. Pre-2000: government and telecom
  marks. Post-2010: hyperscaler logos overtake.
- **Duration:** 9s
- **Footage type:** Animated timeline

## Segment 16 — Geography of the data centers

- **Narration:** "A handful of private companies, headquartered
  mostly in one country, are stitching the world together according
  to where their data centers happen to be."
- **Visual:** World map with data center pins; cables route toward
  them.
- **Duration:** 9s
- **Footage type:** Animated map

## Segment 17 — No fence

- **Narration:** "These cables are not really protected. There is
  no underwater fence. There is no patrolling fleet."
- **Visual:** Empty ocean from above. A single anchor drops into
  water and sinks.
- **Duration:** 8s
- **Footage type:** Stock + symbolic shot

## Segment 18 — 150 faults a year

- **Narration:** "Roughly a hundred and fifty cable faults happen
  every year. Most are accidents — a fishing trawler dragging a
  net, a ship dropping anchor in a bad spot."
- **Visual:** Trawler stock, then anchor on seabed. Lower-third:
  "~150 faults / year".
- **Duration:** 9s
- **Footage type:** Stock + overlay

## Segment 19 — The shark

- **Narration:** "Sharks have, on occasion, bitten through them.
  Engineers eventually added a Kevlar layer."
- **Visual:** Archive footage of shark biting cable (real footage
  exists). Cut to cable cross-section diagram with Kevlar labeled.
- **Duration:** 8s
- **Footage type:** Archive + diagram

## Segment 20 — Red Sea, 2024

- **Narration:** "In 2024, multiple cables in the Red Sea were
  severed within days of each other. Roughly a quarter of all
  Asia-to-Europe internet traffic ran through that corridor."
- **Visual:** News still + animated map highlighting the Red Sea
  chokepoint with cables crossing it.
- **Duration:** 10s
- **Footage type:** Archive news + map

## Segment 21 — The bend, not break

- **Narration:** "The system is fragile, but it bends before it
  breaks. By the time you'd actually feel it, something would have
  to go very wrong, in a very specific place, all at once."
- **Visual:** Visualization of traffic re-routing — packets
  flowing along alternate cable paths.
- **Duration:** 10s
- **Footage type:** Animated diagram

## Segment 22 — Repair ships

- **Narration:** "There are only a few dozen ships in the world
  that can repair these cables. Most are aging. Some are decades
  old."
- **Visual:** Stock of a cable repair ship at sea. Engineers
  handling cable on deck.
- **Duration:** 9s
- **Footage type:** Stock — maritime industry

## Segment 23 — Lay fast, repair slow

- **Narration:** "We can lay cables fast. We cannot repair them
  fast."
- **Visual:** Split-screen: a fast laying operation on one side,
  a slow repair grappling on the other.
- **Duration:** 6s
- **Footage type:** Stock split-screen

## Segment 24 — Geopolitical chokepoints

- **Narration:** "Tensions over Taiwan, the Baltic, the Red Sea,
  the Arctic — every one of those regions is also a chokepoint for
  the cables that move the world's data."
- **Visual:** Map. Each region highlighted in sequence with cable
  routes superimposed.
- **Duration:** 10s
- **Footage type:** Animated map

## Segment 25 — Quieter than war

- **Narration:** "Damaging one of them is becoming a tool of
  pressure. Not war, exactly. Something quieter than war."
- **Visual:** Slow underwater shot of a single cable, moody color
  grade.
- **Duration:** 7s
- **Footage type:** Stock — underwater

## Segment 26 — No Plan B

- **Narration:** "Most of what we call 'the global economy' runs on
  top of around four hundred glass threads. There is no Plan B.
  There is no backup network sitting in orbit. There is no other
  internet."
- **Visual:** Wide world map. The 400 cables drawn in. Then a
  satellite icon ghost-fades and vanishes.
- **Duration:** 11s
- **Footage type:** Animated map

## Segment 27 — Closing image build

- **Narration:** "There is just this one. Stretched across the
  ocean floor. Held together by maintenance ships from the 1990s
  and a handful of engineers who know the routes by heart."
- **Visual:** Slow drone shot of an old cable ship sailing into
  the horizon at golden hour.
- **Duration:** 11s
- **Footage type:** Stock — drone

## Segment 28 — Closing line

- **Narration:** "The most important infrastructure on Earth is
  sitting in the dark, under the sea, where almost no one is
  watching."
- **Visual:** Long pull-back from a single cable on the seafloor
  up through the water column to the surface. Cut to black.
- **Duration:** 14s
- **Footage type:** Custom underwater + stock
""",

        "ai_prompts_md": """\
# AI Prompts: Why undersea cables quietly control the internet

*One image prompt + one video prompt per storyboard scene. Image
prompts target Midjourney / Leonardo / Ideogram. Video prompts
target Runway / Pika / Luma.*

## Format target — YouTube long-form

All output is for **16:9 horizontal long-form video**, not Shorts.

| Surface                | Aspect ratio | Resolution                       |
| ---------------------- | ------------ | -------------------------------- |
| Long-form video        | 16:9         | 1920×1080 (1080p) or 3840×2160   |
| Thumbnail              | 16:9         | 1280×720                         |
| Shorts (separate file) | 9:16         | 1080×1920 (re-framed in CapCut)  |

If your AI tool defaults to square (1:1), override to 16:9. The
visual style anchor below ends with `--ar 16:9` for Midjourney;
Leonardo / Ideogram have a 16:9 preset; Runway / Pika expose
aspect ratio in the clip generation panel.

## Visual style anchor

Append this phrase to every image prompt to keep the 28 scenes
feeling like the same world:

> `cinematic underwater documentary still, 16:9 horizontal
> cinematic frame at 4K (3840×2160), deep blue-black palette
> with subtle teal-cyan neon accents, faint godrays from above,
> single warm rim light, photorealistic, anamorphic 35mm lens,
> shallow depth of field, ultra-detailed, glowing fiber-optic
> data-flow accents, high contrast, mystery and investigation
> atmosphere, no text, no logos, no people unless stated
> --ar 16:9`

Each prompt below is already framed for horizontal output. If
your tool produces a square or vertical result, override the
aspect ratio in the panel before regenerating.

---

## Scene 1 — Hook open

**Image Prompt:** Slow overhead view of a dark ocean surface at
twilight, faint light penetrating into the water, a hint of a
single fiber-optic cable visible on the seafloor far below, fine
pale sediment catching the light.

**Video Prompt:** slow vertical descent from ocean surface down
through deep blue-black water, 9 seconds, faint godrays,
suspended particles drifting past, final frame settles on a
single cable in sediment.

## Scene 2 — Hook contrast

**Image Prompt:** Three small composited frames in sequence on a
dark background — a satellite floating in space, a stylized
cloud icon, then a sharp close-up of a fiber-optic cable cross-
section showing armor wrapping.

**Video Prompt:** three quick contrast cuts: satellite in space,
cloud icon, hard cut to a cable cross-section close-up, 5 seconds
total, each frame holds about 1.5 seconds.

## Scene 3 — Hook close

**Image Prompt:** Wide aerial of empty open ocean at golden
hour, no land in sight, no vessels, vast and quiet, slight haze
on the horizon.

**Video Prompt:** locked-off aerial wide shot of empty open
ocean, 5 seconds, almost no motion except subtle wave texture.

## Scene 4 — Setup A (the everyday picture)

**Image Prompt:** Stylized illustration aesthetic: cartoon wifi
waves, soft cloud icons, orbiting satellites around an idealized
Earth, friendly textbook palette, soft pastels.

**Video Prompt:** 2D animated illustration of the everyday
picture of the internet — wifi waves pulsing, cloud icons
drawing, a satellite tracing an orbit, 7 seconds, gentle motion.

## Scene 5 — Setup B (the reveal)

**Image Prompt:** A world map in deep navy with thin glowing
orange-yellow lines representing submarine cables tracing across
every ocean, lit from beneath, photographic depth.

**Video Prompt:** the soft animated diagram of Scene 4 fades to
black, then a world map fades in with submarine cable routes
lighting up across all oceans in sequence, 6 seconds.

## Scene 6 — On the seabed

**Image Prompt:** Slow camera-level view of a single fiber-
optic cable lying on a deep-ocean seabed, fine pale sediment,
faint particles drifting in the water, tiny fish glimpsed in the
distance.

**Video Prompt:** slow tracking shot moving alongside a cable on
the ocean floor, 8 seconds, low camera height, particles
drifting, faint light from above.

## Scene 7 — Landing stations

**Image Prompt:** A low, anonymous concrete building on a quiet
beach at dawn, no signage, scrubgrass and sand, the sea a few
meters away, photorealistic.

**Video Prompt:** static establishing shot of an unmarked
concrete cable landing station near a beach, slow exterior pan,
7 seconds.

## Scene 8 — Scale: 400 cables, 99%

**Image Prompt:** A world map in deep navy, all submarine cables
drawn as glowing thin lines, two large overlay numbers reading
"400" and "99%", clean infographic aesthetic.

**Video Prompt:** animated map: cables draw themselves from one
landfall to another across every ocean, a counter ticks up to
400, then a "99%" overlay fades in, 9 seconds.

## Scene 9 — What rides on them

**Image Prompt:** Composite still of four small frames — an ATM
screen mid-transaction, a streaming buffer indicator, a video-
call interface, a generic government building exterior — all in
modern cinematic color.

**Video Prompt:** rapid montage of contemporary screens — ATM, a
streaming load bar, a video call window, a government building
exterior, 7 seconds, modern cinematic color grade.

## Scene 10 — Hospital example

**Image Prompt:** A hospital workstation with a radiology
screen showing a cross-border consultation interface, clinical
lighting, professional but warm.

**Video Prompt:** static shot of a radiology workstation pulling
data, then a slow descending dive shot returning to a single
cable on the seafloor, 8 seconds, the descent is the visual link.

## Scene 11 — Why fiber, not satellites

**Image Prompt:** Split diagram on a dark background: left side
shows a fiber-optic cable with light pulses, right side shows a
satellite with radio waves, both labeled with bandwidth bars,
one clearly dwarfing the other.

**Video Prompt:** animated split diagram comparing fiber vs
satellite: bandwidth bars grow on both sides, fiber massively
overshooting satellite, 10 seconds, clean motion graphic.

## Scene 12 — The 1% factoid

**Image Prompt:** A clean dark-background pie chart with a
single tiny 1% slice highlighted in warm orange, the 99%
remainder in cool blue, minimalist data visualization aesthetic.

**Video Prompt:** pie chart animates in, 1% slice highlights,
then a small line graph below shows the 1% trending downward
over time, 8 seconds, clean infographic.

## Scene 13 — The video-call image

**Image Prompt:** A cinematic composite: a person's face being
captured by a webcam, then transformed into stylized pulses of
light traveling along a glass fiber on the ocean floor, with a
fishing trawler silhouette far above.

**Video Prompt:** custom animated journey: face captured by a
webcam, pixelated, transformed into pulses of light traveling
through a glass fiber under the ocean, past a fishing trawler
silhouette and a shipwreck, surfacing on a different continent,
12 seconds, photorealistic + animated hybrid, signature shot of
the episode.

## Scene 14 — Ownership shift

**Image Prompt:** Black background with four corporate logo
placements (placeholder boxes labeled BIG TECH 1–4), faintly
illuminated, monolithic and silent.

**Video Prompt:** four logo placeholders fade in slowly on a
dark background, one at a time, 6 seconds, each logo holds for
about one second after appearing.

## Scene 15 — Government → hyperscaler timeline

**Image Prompt:** A horizontal timeline graphic from 1990 to
2025: pre-2000 markers labeled "GOVERNMENT" and "TELECOM"; post-
2010 markers labeled "BIG TECH"; the post-2010 side is visibly
denser.

**Video Prompt:** animated horizontal timeline: pre-2000 markers
populate first in muted colors, post-2010 markers populate in
sharper saturation, the post-2010 side fills denser, 9 seconds.

## Scene 16 — Geography of the data centers

**Image Prompt:** World map with cluster pins in the United
States, Ireland, Singapore, and Northern Europe, with cable
routes converging toward those clusters, clean dark cartography.

**Video Prompt:** world map: data center pins drop into key
geographies, cable routes animate toward them in sequence,
9 seconds, clean cartographic motion.

## Scene 17 — No fence

**Image Prompt:** Aerial view of empty open ocean from above, a
single anchor falling through the water, slight wake on the
surface, vast emptiness around it.

**Video Prompt:** aerial of empty ocean, then a tight shot of
an anchor dropping from a vessel and sinking into deep water,
8 seconds, sense of solitude.

## Scene 18 — 150 faults a year

**Image Prompt:** A wide low-angle shot of a fishing trawler at
sea pulling nets, paired with a parallel shot of a heavy ship
anchor resting on the seabed, lower-third overlay reads "~150
faults / year".

**Video Prompt:** quick A/B between trawler pulling nets and
anchor on seabed, lower-third overlay "~150 faults / year"
animates in, 9 seconds.

## Scene 19 — The shark

**Image Prompt:** Archive-aesthetic underwater frame: a shark
silhouette near a fiber-optic cable, faint light, slight motion
blur, behind it a labeled cross-section diagram of the cable
showing the Kevlar layer.

**Video Prompt:** archive-style underwater clip of a shark
approaching a cable, cuts to a labeled cable cross-section
diagram with "Kevlar" highlighted, 8 seconds.

## Scene 20 — Red Sea, 2024

**Image Prompt:** A sharp regional map of the Red Sea with
submarine cable routes overlaid, several severance points
marked in warm color, news still composited subtly in the
corner.

**Video Prompt:** map of the Red Sea, cables overlay in,
severance points pulse warmly one by one, a news still ghost-
fades in and out, 10 seconds.

## Scene 21 — The bend, not break

**Image Prompt:** A network diagram showing data packets re-
routing along alternate cable paths, glowing thin lines on a
dark ocean map, sense of motion preserved in still form.

**Video Prompt:** animated network diagram: packets flow along a
primary cable, the cable severs, packets re-route along
alternative paths, latency briefly spikes then normalizes,
10 seconds, smooth schematic motion.

## Scene 22 — Repair ships

**Image Prompt:** Cinematic shot of a cable-repair ship at sea
in overcast light, deck-level view of crew handling thick cable
on a winch, weathered aesthetic.

**Video Prompt:** cinematic deck-level footage of a cable repair
ship: crew handling cable on a winch, ship rolling slightly in
swell, overcast light, 9 seconds.

## Scene 23 — Lay fast, repair slow

**Image Prompt:** Vertical split composition: left side shows a
cable-laying ship moving briskly, right side shows a repair ship
station-keeping with a grappling hook deployed, contrast in
tempo.

**Video Prompt:** split-screen: left side a cable-laying ship
moves quickly across the surface, right side a repair ship
station-keeps with a grappling hook deployed in slow motion,
6 seconds.

## Scene 24 — Geopolitical chokepoints

**Image Prompt:** A world map with four regions highlighted in
warm color — Taiwan Strait, Baltic Sea, Red Sea, Arctic — cable
routes superimposed across each, geopolitical-atlas aesthetic.

**Video Prompt:** map: four regions highlight in sequence —
Taiwan, Baltic, Red Sea, Arctic — cable routes pulse warmly
across each as they appear, 10 seconds.

## Scene 25 — Quieter than war

**Image Prompt:** A single underwater shot of a cable in dim
light, slight motion of suspended particles, mood of quiet
unease, no other elements.

**Video Prompt:** locked-off underwater shot of a single cable
in moody color grade, 7 seconds, only ambient particle drift, no
camera motion.

## Scene 26 — No Plan B

**Image Prompt:** A wide world map in deep navy with all 400
cables drawn as glowing thin lines, plus a small ghosted
satellite icon fading toward transparency in the corner.

**Video Prompt:** world map fully drawn with 400 cables glowing,
a satellite icon enters from the corner, ghost-fades and
disappears, 11 seconds, the map remains.

## Scene 27 — Closing image build

**Image Prompt:** An aging cable-repair ship sailing into the
horizon at golden hour, drone perspective from behind and above,
warm light catching the wake, lonely cinematic composition.

**Video Prompt:** drone shot of an aging cable ship sailing away
into golden-hour horizon, 11 seconds, slow forward camera
motion, warm light, lonely composition.

## Scene 28 — Closing line

**Image Prompt:** A single fiber-optic cable on the dark ocean
floor, the camera position low, water column rising into faint
light above, moody and final.

**Video Prompt:** slow continuous pull-back from a single cable
on the seafloor up through the entire water column to the
surface, fading toward black, 14 seconds, signature closing
shot of the episode.

---

## How to use these prompts

1. Open Midjourney / Leonardo / Ideogram. Paste the image prompt
   for Scene 1, append the **Visual style anchor** above,
   generate 4 variants, pick the strongest. **Confirm the output
   is 16:9 horizontal at 1920×1080 minimum** — if your tool
   defaulted to square, switch to 16:9 in the panel and
   regenerate.
2. Open Runway / Pika / Luma. Use **image-to-video** with the
   still you generated, plus the video prompt. Set the output
   aspect ratio to **16:9** (not 9:16, not 1:1). Image-to-video
   gives much better continuity across the 28 scenes than
   text-to-video.
3. Repeat for every scene. Save each clip as `scene_XX.mp4`
   matching the scene number. Drop them on the CapCut timeline.
4. **Set CapCut project resolution to 1920×1080 / 16:9** before
   importing. The pre-rolled CapCut Shorts/9:16 preset is the
   wrong one — switch to YouTube 16:9 long-form.
5. Don't drop the visual style anchor. It is the only thing that
   makes 28 separately-generated clips feel like the same world.

## A note on Shorts

The `shorts.md` file describes 6 vertical Shorts (9:16 1080×1920).
Those re-frame the long-form 16:9 footage you produced above —
they are not separately generated. In CapCut, open a second
project at 9:16, drop the relevant scene clips in, zoom and
reposition for vertical, burn in subtitles. See `shorts.md` for
the per-Short scene mapping.
""",

        "thumbnail_md": """\
# Thumbnail Strategy: Why undersea cables quietly control the internet

## Concept

A single fiber-optic cable lying on a dark ocean floor, faint
shafts of light filtering down from above, and one stark text
overlay. The image should immediately raise the question:
*"Wait — that's the internet?"*

## Emotional Trigger

**Mystery + scale.** The viewer should feel "everything depends
on this small thing" before they read a single word. The cable
must look almost too thin for the burden it's carrying.

## Visual Composition

- **Foreground (left third):** A single dark cable, slightly lit,
  lying in fine sediment. Sharp focus. Slight motion blur in the
  surrounding water for atmosphere.
- **Midground:** Soft seabed gradient, faint particles drifting
  in the water column.
- **Background:** Deep blue-black, fading to true black at the
  edges. Subtle godrays from upper-right.
- **Subject focus:** The cable. The eye must land on it within
  half a second. Test by viewing the thumbnail at 480px.

## Text Overlay

The thumbnail carries **two text elements**, both burned into
the image:

1. **Headline:** `THE INTERNET IS HERE`
   White, condensed sans-serif, slightly weathered. Position:
   upper-right, leaving negative space over the cable below.

2. **Runtime label:** `8 MIN`
   Smaller (~30% of headline size), bottom-right, white on dark,
   thin stroke. This is the standard YouTube documentary
   convention — sets a clear time commitment up front and
   improves CTR.

Avoid: a question mark, full sentences, more than two font
weights, yellow highlighter underline.

## Color Direction

Deep blue-black water as the dominant. **One** warm rim light on
the cable from above-right — a single highlight, not a wash.
High contrast. Avoid teal-and-orange grading; it reads as every
other YouTube thumbnail.

## AI Image Prompt

> **Recommended tool: Ideogram** (best at text rendering). If
> the text comes out mangled in the AI output, regenerate with
> `no text` in the prompt and add the text yourself in CapCut
> or Canva — that's the safer fallback.

cinematic close-up of a single fiber-optic submarine cable lying
on the dark ocean floor in fine sediment, **16:9 horizontal
YouTube thumbnail aspect ratio (1280×720 minimum)**, faint
godrays from above filtering through deep blue-black water,
slight motion blur of suspended particles, ultra-detailed cable
jacket with visible armor wrapping, cold blue tones with subtle
teal-cyan neon accents and a single warm rim highlight from
upper right, photorealistic, anamorphic 35mm lens, shallow depth
of field, dramatic underwater lighting, glowing fiber-optic
data-flow accents, high contrast, mystery and investigation
atmosphere, hyperdetailed 4K. **Text overlay burned into the
image: white condensed sans-serif headline reading "THE INTERNET
IS HERE" in the upper-right with slight weathered texture, plus
a smaller "8 MIN" runtime label in the bottom-right corner —
both white on dark, crisp legible kerning, sharp letterforms.**
No people, no logos, no other text. Eerie quiet atmosphere,
designed for YouTube thumbnail click-through. --ar 16:9
""",

        "shorts_md": """\
# Shorts Pack: Why undersea cables quietly control the internet

*Six standalone vertical clips, each 15–22 seconds. Each lands as
its own viral Short.*

## Format target — YouTube Shorts

| Surface | Aspect ratio | Resolution |
| ------- | ------------ | ---------- |
| Shorts  | **9:16**     | 1080×1920  |

Shorts are **vertical**, unlike the long-form 16:9 video. In
CapCut, open a **second project at 9:16 1080×1920**, pull the
relevant horizontal scene clips from the long-form export
(generated via `ai_prompts.md` at 16:9 1920×1080), zoom and
reposition each clip for vertical framing, burn in subtitles,
export each as `short_X_<title>.mp4`.

Do **not** regenerate clips at 9:16 — re-frame the horizontal
long-form clips. That keeps visual consistency across both
formats and avoids burning AI credits twice.

---

## Short 1 — "There is no cloud"

- **Hook (0–2s):** "There is no cloud. There never was."
- **Beat 1 (2–6s):** Stylized cloud icon dissolves into a world
  map.
- **Beat 2 (6–12s):** Cables draw themselves across every ocean.
  "Ninety-nine percent of the internet runs through these."
- **Beat 3 (12–18s):** Underwater shot of a real cable on the
  seafloor.
- **Punch (18–22s):** "The cloud is at the bottom of the ocean.
  Every video. Every message. Every bank transfer."

## Short 2 — "The shark that broke the internet"

- **Hook (0–2s):** "Sharks have, on occasion, broken the internet."
- **Beat 1 (2–7s):** Real archive footage of a shark biting a
  cable.
- **Beat 2 (7–14s):** Diagram zoom: cable cross-section, Kevlar
  layer highlighted.
- **Punch (14–20s):** "Engineers added a Kevlar layer. The sharks
  moved on. The cables stayed."

## Short 3 — "Four hundred glass threads"

- **Hook (0–2s):** "Everything you do online runs through about
  four hundred cables. That's it."
- **Beat 1 (2–8s):** Animated map: cables draw across oceans, a
  counter ticks to 400.
- **Beat 2 (8–14s):** Quick montage — banking, video calls,
  hospitals, stock exchanges.
- **Punch (14–20s):** "Four hundred glass threads. No Plan B."

## Short 4 — "Big Tech is buying the ocean"

- **Hook (0–2s):** "Big Tech is quietly buying the ocean floor.
  And almost no one is talking about it."
- **Beat 1 (2–8s):** Logo stack — Google, Meta, Amazon, Microsoft
  — fades in over a dark map.
- **Beat 2 (8–14s):** Timeline: pre-2000 government cables →
  post-2010 hyperscaler cables.
- **Punch (14–22s):** "The companies whose products you use every
  day are now stitching the internet together themselves."

## Short 5 — "The Red Sea moment"

- **Hook (0–2s):** "In 2024, someone cut a quarter of Asia's
  internet."
- **Beat 1 (2–8s):** Map: Red Sea chokepoint highlighted, cables
  crossing it.
- **Beat 2 (8–15s):** "Roughly twenty-five percent of Asia–Europe
  traffic ran through here. Several cables severed within days."
- **Punch (15–22s):** "Most users never noticed. That's the eerie
  part. The system bends before it breaks."

## Short 6 — "Ships from the 1990s"

- **Hook (0–2s):** "The internet is held together by ships from
  the 1990s."
- **Beat 1 (2–8s):** Stock of an aging cable repair ship at sea.
- **Beat 2 (8–14s):** "There are fewer than sixty of these ships
  in the entire world."
- **Punch (14–20s):** "We can lay cables fast. We cannot repair
  them fast. That's the part that should worry you."
""",

        "upload_md": """\
# Upload Pack: Why undersea cables quietly control the internet

## SEO description

*(Paste into the YouTube description box. The first three lines
are what shows above the fold — written as a teaser, not a
keyword summary.)*

The picture you have of the internet — clouds, satellites,
signals in the air — is almost completely wrong. The actual
internet is a wet, fragile, deeply physical thing. It runs along
the ocean floor.

This is a 7-minute documentary on the four hundred fiber-optic
cables that quietly carry ninety-nine percent of all
intercontinental data — and why almost nothing is protecting
them.

We cover:
- where the internet actually lives
- why satellites carry less than 1% of traffic
- who is quietly buying the ocean floor (it's not who you think)
- the 2024 Red Sea incident that affected a quarter of Asia–
  Europe traffic without most users noticing
- the aging fleet of repair ships that holds the whole thing
  together

Chapters:
00:00 — Hook
00:25 — Setup: the picture is wrong
01:10 — Why fiber, not satellites
02:05 — Who really owns the cables now
03:00 — Where it becomes fragile
04:30 — Why it matters now
05:45 — Closing

If you found this useful, the rest of the channel covers
adjacent systems — power grids, shipping lanes, financial rails
— that most people never look at directly.

—

🎙 Voice-over: human, slow.
🎬 Visuals: AI-generated and licensed stock.
📚 Sources: TeleGeography, ITU, public news archives. Linked in
the pinned comment.

#underseacables #internetinfrastructure #documentary #explainer

## 18 SEO tags

undersea cables
submarine cables
how the internet works
internet infrastructure
undersea cables explained
submarine cable map
underwater internet cables
who owns the internet
internet documentary
red sea cables 2024
big tech infrastructure
internet at the bottom of the ocean
fiber optic cables ocean
cable landing stations
youtube documentary
short documentary
faceless youtube
systems thinking

## Hashtags

*(First line of the description. YouTube indexes the first three;
the rest are decorative.)*

#underseacables #internetinfrastructure #documentary
#howitworks #shortdoc #faceless #systemsthinking #curiosity

## Suggested filename

`undersea-cables_documentary_v1.mp4`

(Replace `v1` with the cut number on re-export.)

## Suggested category

**Education** — this video sits more cleanly in Education than
in People & Blogs because the topic is genuinely informational
and triggers infrastructure-curious watch-history clusters on
YouTube.

Avoid News & Politics. The Red Sea segment is in the script, but
framing the whole video as news will cap your evergreen
recommendation surface.

## Posting time recommendation

Post **Tuesday at 3pm Eastern (US)**. That window catches:

- the Asia/Pacific evening tail
- the European late evening
- the US afternoon rebound after lunch

Tuesday specifically beats Thursday for evergreen explainer
content — the algorithm's recommendation cycle for educational
videos peaks 3–4 days after upload, and a Tuesday upload lands
its first peak weekend, which is when this kind of documentary
gets its strongest organic share.

Avoid Monday morning (algorithm cold-start) and Friday evening
(weekend competition spike).
""",

        "capcut_md": """\
# CapCut Edit Guide: Why undersea cables quietly control the internet

*Paste this beside the timeline as you assemble the video.*

## Project setup (do this first)

- **Aspect ratio:** 16:9 (horizontal) — long-form YouTube, not
  Shorts. The Shorts cuts go in a separate CapCut project (see
  `shorts.md`, 9:16 1080×1920).
- **Resolution:** 1920×1080 (1080p), or 3840×2160 (4K) if your
  AI-generated clips rendered at 4K.
- **Frame rate:** 24 fps for the cinematic documentary feel.
- **Export preset:** YouTube 1080p, H.264, ~30 Mbps.

If CapCut opens with the Shorts/9:16 default canvas, switch to
16:9 before importing the 28 scene clips.

## Timeline breakdown

The video runs in this order. Drop each AI-generated clip into
its slot, matching scene numbers from `storyboard.md` and
`ai_prompts.md`:

```
0:00–0:25   HOOK              (Scenes 1–3)
0:25–1:10   SETUP             (Scenes 4–10)
1:10–2:05   WHY IT EXISTS     (Scenes 11–13)
2:05–3:00   WHAT MOST MISS    (Scenes 14–16)
3:00–4:30   FRAGILITY         (Scenes 17–23)
4:30–5:45   WHY NOW           (Scenes 24–26)
5:45–6:45   CLOSING           (Scenes 27–28)
```

## Transitions per scene

| Scenes | Transition | Why |
| ------ | ---------- | --- |
| 1 → 2  | Hard cut | The contrast is the whole point of the hook. |
| 2 → 3  | Hard cut | Three short beats stacked tight. |
| 3 → 4  | Cut | Tonal handoff from real to stylized. |
| 4 → 5  | Dissolve | The clean diagram dissolves into the real cable map — this dissolve carries the thesis. |
| 5 → 6  | Cut | Map to underwater is a clean cut. |
| 6 → 7  | Cut | Continuity within the setup montage. |
| 8 → 9–10 | Cut, faster pace | Scale beat into "what runs on the cables" montage. |
| 11 → 12 | Cut | Diagram-to-diagram. |
| 13 (signature shot) | **Hold longer than feels comfortable** | This is the visual signature. Give it 12s. |
| 14 → 15 | Slow fade | The ownership reveal builds slowly. |
| 17 → 18 → 19 | Cut, cool grade kicks in | This is where the visual tone shifts. |
| 20 → 21 | Cut on map highlight | Red Sea reveal. |
| 27 → 28 | **No transition. Long held shot.** | The closing line lands in dry air. |

**Avoid in CapCut:** glitch transitions, light leaks, fast zooms,
spinning wipes, anything tagged "TikTok." This is a documentary.

## B-roll suggestions

When an AI-generated clip doesn't quite land, drop in:

- Atmospheric drone shots of open ocean (Pexels has dozens)
- Industrial port footage (cable ships, cranes)
- Underwater cable footage (Pexels and Pixabay both have stock)
- Modern interface footage for the "what runs on the cables"
  montage (ATM, video calls, hospital workstations)
- Archive footage of 19th-century telegraph cable laying for the
  origin context (search "transatlantic cable" archive)

## Subtitle style guidance

- Font: **white sans-serif, condensed, slight weight**. Inter
  Tight or DM Sans Condensed in CapCut.
- Position: **bottom third**, no background bar
- Drop shadow: soft, 30% opacity, 2px offset
- Bold these specific phrases on screen — they're the rhythmic
  landing points the script is built around:

  - *not a satellite, not the cloud, a cable*
  - *almost nothing is protecting it*
  - *ninety-nine percent*
  - *four hundred glass threads*
  - *no Plan B*
  - *something quieter than war*
  - *almost no one is watching*

These show up bold even on muted autoplay — that's how most of
the audience will see the video the first time.

## SFX suggestions

| Moment                          | SFX |
| ------------------------------- | --- |
| Hook open (Scene 1)             | Low ambient drone, 0.5s pre-roll |
| Each section break              | Subtle whoosh OR a moment of silence — never both |
| "Ninety-nine percent" reveal    | One single low-volume sonar ping |
| Red Sea segment (Scene 20)      | Distant low rumble, almost subliminal |
| Repair-fleet segment (Scenes 22–23) | Same low rumble, slightly higher |
| Closing line (Scene 28)         | **Total silence** — no music, no SFX |

Two pings maximum in the whole episode. They lose their meaning
fast.

## Background music style

Reference: **slow Hans Zimmer, but quieter.** Closer to *Time*
than *Inception trailer*.

- Genre: ambient cinematic, low-pulsing synth bass
- BPM: 60–80
- Key: minor (C minor / D minor work well)
- Energy: stays flat. No swells. No drops. No "epic moment".

CapCut "Music" library → search *"ambient cinematic"* or
*"documentary slow"*. Avoid anything tagged *"viral"*, *"epic"*,
or *"trailer"*.

**Drop the music entirely under the closing 30 seconds (Scenes
27 and 28).** The silence is the most powerful tool you have at
the end of this episode.

## Voiceover pacing notes

- **Cadence:** ~140–150 words per minute. Slower than a typical
  YouTube tutorial.
- **Breath beats:** hold 1 second of silence at every section
  break in the script. Don't cut these out — the script earns
  them.
- **Emphasis words:** *cable, ocean, fragile, four hundred,
  ninety-nine percent, no Plan B, ocean floor.* Slight slowdown
  and lower pitch on these, never raised volume.
- **Avoid:** rising intonation at line ends, "podcast voice",
  forced enthusiasm. The hype-voice is the AI tell.

If you're using AI voice (ElevenLabs / Speechify), pick a slower
documentary preset and add a 0.5s pause manually at every
section break in the script.
""",

        "workflow_md": """\
# Workflow & Tools: Why undersea cables quietly control the internet

This is the navigation file for the entire production. It tells
you exactly what to do with each of the other nine files in this
pack, in the order to do it, and which external tool to use at
each step. Bookmark this file — it's your dashboard.

---

## EXECUTION WORKFLOW

### Step 1 — Read the concept *(5 min)*

Open `idea.md`. Read it once. The promise to the audience is
*"by the end of this video, you will never use the word 'cloud'
the same way again"*. If you're committing to that promise,
continue.

**Tool:** none.

### Step 2 — Pick the title *(5 min)*

Open `titles.md`. The 12 titles are split across 6 categories.
For undersea cables, two work hardest:

- **Fear / risk:** *"The Internet Is at the Bottom of the Ocean
  (And Almost Nothing Is Protecting It)"*
- **Hidden truth:** *"The 400 Cables That Quietly Run the World"*

Pick the one that gives you the strongest "I'd click that"
reaction at thumbnail size.

**Tool:** none.

### Step 3 — Design the thumbnail *(15 min)*

Open `thumbnail.md`. Copy the **AI Image Prompt** at the bottom.

**Tool:** Leonardo, Ideogram, or Bing Image Creator.

1. Paste the prompt. The result should be a single fiber-optic
   cable on a dark ocean floor with faint godrays.
2. Generate 4 variants. Pick the one with the strongest
   silhouette at 480px (test by zooming out).
3. Add the text overlay **"THE INTERNET IS HERE"** in CapCut
   or Canva — white condensed sans-serif, upper-right, with
   negative space over the cable.
4. Export as `thumbnail.jpg` at 1280×720.

### Step 4 — Record the voiceover *(15–25 min)*

Open `script.md`. Copy the entire script body.

**Tool:** ElevenLabs (preferred) or PlayHT.

1. Paste the full script.
2. Pick a slower documentary preset. Recommended ElevenLabs
   voices: *Adam* (low, measured) or *Daniel* (warmer).
3. Add a 0.5s pause manually at every section break (HOOK →
   SETUP → WHY IT EXISTS → ...).
4. Slight slowdown on the emphasis words: *cable, ocean,
   fragile, four hundred, ninety-nine percent, no Plan B,
   ocean floor.*
5. Export as `voiceover.mp3`.

### Step 5 — Generate scene visuals *(60–90 min)*

Open `ai_prompts.md`. **There are 28 scenes.** Read the
**Visual style anchor** at the top — for this episode it's:

> *cinematic underwater documentary still, 16:9 horizontal
> cinematic frame at 4K (3840×2160), deep blue-black palette
> with subtle teal-cyan neon accents, faint godrays from above,
> single warm rim light, photorealistic, anamorphic 35mm lens,
> shallow depth of field, ultra-detailed, glowing fiber-optic
> data-flow accents, high contrast, mystery and investigation
> atmosphere, no text, no logos, no people unless stated
> --ar 16:9*

**Format target: 16:9 horizontal at 1920×1080 minimum (4K
preferred).** This is for the long-form YouTube video. Shorts
are re-framed in CapCut from these horizontal clips — see
Step 6.

For every one of the 28 scenes:

1. Copy the **Image Prompt**.
2. Append the **Visual style anchor**.
3. Paste into Midjourney (`--ar 16:9`), Leonardo (16:9 preset),
   or Ideogram (16:9 preset). Generate 4 variants. Pick the one
   that matches the underwater documentary tone — reject
   anything cartoonish, overlit, square, or vertical.
4. Save as `scene_XX.png`.
5. Copy the **Video Prompt**.
6. Paste into Runway / Pika / Luma. Set the output aspect ratio
   to **16:9 horizontal**. Use **image-to-video** with the still
   you just generated.
7. Save as `scene_XX.mp4`.

The signature scene is **Scene 13** (the video-call as light
pulses sequence). Spend extra time on it. Hold for 12 seconds
in the final cut.

The closing pull-back is **Scene 28**. 14 seconds. This is the
last image of the episode.

**Tool:** Midjourney / Leonardo / Ideogram for image; Runway /
Pika / Luma for video. **Aspect ratio: 16:9 horizontal**.

### Step 6 — Cut the 6 Shorts *(20 min)*

Open `shorts.md`. Six standalone vertical Shorts at **9:16 /
1080×1920**:

1. *"There is no cloud"* — uses Scenes 1, 5, 6 footage.
2. *"The shark that broke the internet"* — uses Scene 19.
3. *"Four hundred glass threads"* — uses Scene 8.
4. *"Big Tech is buying the ocean"* — uses Scenes 14, 15.
5. *"The Red Sea moment"* — uses Scenes 20, 21.
6. *"Ships from the 1990s"* — uses Scenes 22, 23.

**Tool:** CapCut. *Open a separate project from the long-form
— do not mix 16:9 and 9:16 in the same timeline.*

1. New CapCut project at **9:16 / 1080×1920**.
2. Pull the relevant 16:9 scene clips from Step 5.
3. Re-frame for vertical: zoom in, reposition the subject to
   the center of the 9:16 canvas.
4. Burn in subtitles, bold the punch line.
5. Export each as `short_X_<title>.mp4` at 1080×1920, H.264.

### Step 7 — Assemble the long-form video *(1.5–2 hours)*

Open `storyboard.md` (28 scenes, scene-by-scene narration
alignment) and `capcut.md` (transitions, B-roll, subtitle
style, SFX, music).

**Tool:** CapCut.

1. New CapCut project at **16:9 / 1920×1080** (or 3840×2160 if
   your scene clips rendered at 4K). Frame rate: 24 fps.
2. Drop scene clips on the timeline in storyboard order
   (Scenes 1 through 28). All 28 clips should already be 16:9
   horizontal from Step 5.
3. Layer `voiceover.mp3` underneath. Align scene cuts to the
   narration beats.
4. Apply transitions per `capcut.md`:
   - HOOK (Scenes 1–3): hard cuts
   - SETUP reveal (Scene 4 → 5): dissolve
   - Scene 13 (signature shot): hold 12 seconds, no cuts
   - FRAGILITY (Scenes 17–23): cool grade kicks in
   - Closing (Scene 28): no transition, long held shot
5. Burn in subtitles. Bold these phrases when they land:
   *not a satellite, not the cloud, a cable* / *almost nothing
   is protecting it* / *ninety-nine percent* / *four hundred
   glass threads* / *no Plan B* / *something quieter than war*
   / *almost no one is watching*.
6. Drop the music bed (CapCut Music library → search "ambient
   cinematic" or "documentary slow", BPM 60–80, minor key).
7. **Drop the music entirely under the closing 30 seconds.**
   Silence is the most powerful tool for the closing line.
8. Export at 1080p, H.264, ~30Mbps.

### Step 8 — Upload to YouTube *(10 min)*

Open `upload.md`.

**Tool:** YouTube Studio.

1. Upload the video file.
2. Copy the **SEO description** into the description box. The
   chapters are pre-formatted; YouTube will auto-detect them.
3. Copy the **18 SEO tags** into the tags field.
4. Set the **filename**:
   `undersea-cables_documentary_v1.mp4`
5. Set the **category**: **Education** (not News & Politics —
   keeps the evergreen recommendation surface intact).
6. Upload `thumbnail.jpg` from Step 3.
7. **Schedule for Tuesday 3pm Eastern.** This catches the
   Asia/Pacific evening tail, European late evening, and the US
   afternoon rebound — and lands its first algorithmic peak on
   the weekend, which is when documentary content shares most.

### Step 9 — Optimize after upload *(ongoing)*

Once live, monitor first-24-hour performance.

**Tool:** VidIQ or TubeBuddy.

1. **CTR target:** 5%+ in the first 24 hours.
2. If under target: A/B test the title — swap to one of the
   other 11 in `titles.md`.
3. If still under target: re-generate the thumbnail. Try the
   *"NO ONE IS WATCHING"* text overlay variant from
   `thumbnail.md`.
4. Use VidIQ to identify which related-video keywords drove
   external traffic — feed those into the next episode's
   `upload.md`.

---

## TOOLS PANEL

*Production dashboard. Each link opens the canonical product
page. Sign in with your existing accounts.*

### 🧠 Script tools
*(For drafting, refining, or rewriting if you want to vary
from the generated script.)*

- 🤖 [Claude](https://claude.ai) — best for long-form structured writing
- 💬 [ChatGPT](https://chatgpt.com) — broadest model coverage
- ✨ [Gemini](https://gemini.google.com) — Google ecosystem integration
- ⚡ [Grok](https://grok.com) — real-time content awareness

### 🎨 Image tools
*(For thumbnail and the 28 per-scene stills — Step 3 and Step 5.)*

- 🦁 [Leonardo](https://leonardo.ai) — fast, reliable, generous free tier
- 🟣 [Ideogram](https://ideogram.ai) — best for text inside images
- 🌐 [Bing Image Creator](https://www.bing.com/images/create) — DALL-E powered, free

### 🎬 Video tools
*(For motion clips per scene — Step 5.)*

- 🎞️ [Runway](https://runwayml.com) — Gen-3 quality, image-to-video
- 🎥 [Pika](https://pika.art) — fast turnaround, motion control
- 💡 [Luma](https://lumalabs.ai/dream-machine) — Dream Machine, photorealistic

### 🎙️ Voice tools
*(For voiceover — Step 4.)*

- 🗣️ [ElevenLabs](https://elevenlabs.io) — best AI voice quality (use *Adam* or *Daniel* for this episode)
- 🎤 [PlayHT](https://play.ht) — large voice library, voice cloning

### ✂️ Editing tools
*(For assembly — Step 6 and Step 7.)*

- ✂️ [CapCut](https://www.capcut.com) — primary editor for this workflow
- 🎨 [Canva](https://www.canva.com) — thumbnail polish, text overlays

### 📺 YouTube tools
*(For upload, analytics, optimization — Step 8 and Step 9.)*

- 📊 [YouTube Studio](https://studio.youtube.com) — upload, schedule, analytics
- 🔍 [VidIQ](https://vidiq.com) — SEO research, A/B testing
- 🚀 [TubeBuddy](https://tubebuddy.com) — keyword research, tag suggestions

---

## Episode-specific reminders

- **Visual style anchor goes on every image prompt.** Without
  it, the 28 generated clips won't feel like the same world.
- **Scene 13 is the visual signature.** The "video call as
  light pulses" sequence. Hold it 12 seconds in the final cut.
- **Scene 28 is the closing pull-back.** 14 seconds, cable on
  seafloor up to surface, cut to black. No music under it.
- **Don't paste the script into ChatGPT to "improve" it.** The
  script is already tuned for the editorial bar. Improvement
  requests usually flatten the voice.
""",
    },
}


def find_seed(topic: str) -> dict | None:
    """Return a seed entry whose keywords appear in the topic, else None."""
    if not topic:
        return None
    haystack = topic.lower()
    for seed in SEED_LIBRARY.values():
        for kw in seed.get("match_keywords", []):
            if kw in haystack:
                return seed
    return None


# ---------------------------------------------------------------------------
# Small helpers used by generic templates
# ---------------------------------------------------------------------------

def title_case_subject(subject: str) -> str:
    """Title-case a subject for use in titles. Keeps small words lowercase."""
    small = {"a", "an", "and", "the", "of", "in", "on", "for", "to", "with",
             "is", "are", "by", "at", "as", "or", "but"}
    words = subject.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i != 0 and lw in small:
            out.append(lw)
        else:
            out.append(lw[:1].upper() + lw[1:] if lw else lw)
    return " ".join(out)


def cap_first(text: str) -> str:
    """Capitalize only the first character; leave the rest alone."""
    if not text:
        return text
    return text[0].upper() + text[1:]


def _slug_compact(subject: str, sep: str = "-") -> str:
    """Lowercase + strip non-word + collapse whitespace into `sep`."""
    cleaned = re.sub(r"[^\w\s]", "", (subject or "").lower())
    return re.sub(r"\s+", sep, cleaned).strip(sep)


def template_context(card: dict) -> dict:
    """Build the substitution dict consumed by all generic templates."""
    subject = card.get("subject", "")
    length = length_or_default(card.get("video_length"))
    return {
        "raw_topic": card.get("raw_topic", ""),
        "subject": subject,
        "subject_short": card.get("subject_short", subject),
        "subject_cap": cap_first(subject),
        "subject_title": title_case_subject(subject),
        "subject_slug": _slug_compact(subject, sep="-"),
        "subject_hashtag": _slug_compact(subject, sep=""),
        "video_length": length,
        "runtime": LENGTH_RUNTIME[length],
        "word_target": LENGTH_WORD_TARGET[length],
        "scene_count": LENGTH_SCENE_COUNT[length],
        "cut_pacing": LENGTH_CUT_PACING[length],
        "thumbnail_hook": LENGTH_THUMBNAIL_HOOK[length],
        "thumbnail_runtime_label": LENGTH_THUMBNAIL_RUNTIME_LABEL[length],
    }


def pick_opener(tone: str, subject: str) -> str:
    """Deterministically select a tone-appropriate opening line.

    Selection is hashed off the subject so the same topic always picks
    the same opener — no randomness, but variation across topics.
    """
    bank = TONE_OPENERS.get(tone) or TONE_OPENERS["documentary"]
    idx = sum(ord(c) for c in subject) % len(bank)
    return bank[idx].format(subject=subject)


# ---------------------------------------------------------------------------
# Scene library — drives both storyboard.md and ai_prompts.md.
# ---------------------------------------------------------------------------
#
# Each scene declares a tier (1 = essential / always included, 2 = standard
# extra, 3 = deep-dive extra). Selection by length:
#
#   short      -> tier == 1                -> 13 scenes
#   standard   -> tier <= 2                -> 25 scenes
#   deep_dive  -> all                      -> 40 scenes
#
# duration_s is the base duration at standard length. Short shrinks it,
# deep_dive lengthens it — produces the requested cut pacing per length.

GENERIC_SCENES: list[dict] = [
    # ---- HOOK (5) ---------------------------------------------------------
    {"tier": 1, "section": "hook", "title": "Hook open",
     "narration": "*(opening line of the script)*",
     "visual": "Slow push-in on a single quiet image associated with {subject}. No motion graphics.",
     "footage": "Stock — single subject", "duration_s": 8,
     "image_prompt": "A single quiet image associated with {subject}, deep atmospheric mood, single subject focus, no clutter.",
     "video_prompt": "slow push-in toward the central subject of {subject}, 8 seconds, ambient particles, very gentle camera motion."},
    {"tier": 1, "section": "hook", "title": "Hook contrast",
     "narration": "*(second beat of the hook — the contradiction)*",
     "visual": "Hard cut to a contrasting image: the unexpected version of {subject}. Brief hold.",
     "footage": "Stock contrast", "duration_s": 5,
     "image_prompt": "A contrasting visual to the previous scene, the unexpected version of {subject}, hard tonal shift.",
     "video_prompt": "hard cut, 5 second hold, almost no camera motion."},
    {"tier": 2, "section": "hook", "title": "Hook close",
     "narration": "*(third beat — landing the contradiction)*",
     "visual": "Wide negative-space shot. Quiet hold.",
     "footage": "Stock — wide", "duration_s": 5,
     "image_prompt": "Wide negative-space shot of the environment around {subject}, emptiness and scale, no visible primary subject.",
     "video_prompt": "slow lateral drift across the frame, 6 seconds, no zoom."},
    {"tier": 3, "section": "hook", "title": "Hook deepening",
     "narration": "*(extending the hook with one more concrete image)*",
     "visual": "Tight cut to a specific telling detail tied to {subject}.",
     "footage": "Stock — close-up", "duration_s": 6,
     "image_prompt": "Tight macro close-up of a telling detail tied to {subject}, sharp focus, atmospheric.",
     "video_prompt": "slow rack focus over a close-up detail, 6 seconds, shallow depth of field."},
    {"tier": 3, "section": "hook", "title": "Hook landing",
     "narration": "*(letting the contradiction land — silence beat)*",
     "visual": "Long held shot. Almost no motion.",
     "footage": "Stock — held shot", "duration_s": 6,
     "image_prompt": "Held atmospheric shot suggesting the topic, almost no visible activity, contemplative.",
     "video_prompt": "locked-off held shot, 6 seconds, only ambient motion."},

    # ---- SETUP (5) --------------------------------------------------------
    {"tier": 1, "section": "setup", "title": "The everyday picture",
     "narration": "*(setting up the version the audience already holds)*",
     "visual": "Stylized illustration of how the average person mentally pictures {subject}. Soft palette.",
     "footage": "Animated diagram", "duration_s": 8,
     "image_prompt": "Stylized illustration of the everyday mental picture of {subject}, soft palette, friendly textbook diagram aesthetic.",
     "video_prompt": "2D animation drawing in the everyday picture of {subject}, 7 seconds, gentle motion."},
    {"tier": 1, "section": "setup", "title": "Picture breaks",
     "narration": "*(the moment the picture starts to come apart)*",
     "visual": "The diagram fragments. Cut to b-roll of the real version of {subject}.",
     "footage": "Stock + diagram transition", "duration_s": 7,
     "image_prompt": "The clean diagram of the previous scene fragmenting, revealing the real version of {subject} underneath.",
     "video_prompt": "diagram dissolves into real-world b-roll of {subject}, 6 seconds, palette shifts from soft to deep."},
    {"tier": 2, "section": "setup", "title": "Setup widens",
     "narration": "*(zooming out to show the wider system)*",
     "visual": "Pull-back from the detail to a wider view of {subject}.",
     "footage": "Stock — wide pull-back", "duration_s": 9,
     "image_prompt": "Wide pull-back composition revealing the scale around {subject}.",
     "video_prompt": "slow continuous pull-back, 9 seconds, sense of scale opening up."},
    {"tier": 3, "section": "setup", "title": "Setup detail",
     "narration": "*(one specific detail that anchors the topic)*",
     "visual": "Close-up of a single specific element of {subject}.",
     "footage": "Stock — close-up", "duration_s": 8,
     "image_prompt": "Close-up of one specific element associated with {subject}, sharp focus, photographic.",
     "video_prompt": "slow tracking shot across a single specific detail, 8 seconds, shallow focus."},
    {"tier": 3, "section": "setup", "title": "Setup transition",
     "narration": "*(transition into the why-it-exists section)*",
     "visual": "Tonal handoff: cooler color, slightly slower tempo.",
     "footage": "Stock", "duration_s": 5,
     "image_prompt": "Tonal-transition shot tied to {subject}, slightly cooler grade, moody.",
     "video_prompt": "very slow camera move with cooling color grade, 5 seconds."},

    # ---- WHY IT EXISTS (5) -----------------------------------------------
    {"tier": 1, "section": "why_exists", "title": "Origin opener",
     "narration": "*(opening of the WHY IT EXISTS section)*",
     "visual": "Period imagery / archival photography evoking the historical origin of {subject}.",
     "footage": "Archive", "duration_s": 9,
     "image_prompt": "Period imagery evoking the historical origin of {subject}, sepia or muted tones, sense of age.",
     "video_prompt": "slow Ken Burns pan across an archival-style photograph, 9 seconds."},
    {"tier": 1, "section": "why_exists", "title": "Lock-in",
     "narration": "*(showing how the choice locks in over time)*",
     "visual": "Time-lapse or layered animation showing accumulation around {subject}.",
     "footage": "Animated time-lapse", "duration_s": 8,
     "image_prompt": "Visual metaphor for accumulation and lock-in around {subject}, layered structure built up over time.",
     "video_prompt": "time-lapse build-up of layered structure, 8 seconds, increasing density."},
    {"tier": 2, "section": "why_exists", "title": "Origin detail",
     "narration": "*(zooming into one specific origin moment)*",
     "visual": "Tight on one decision-moment image — meeting, document, machinery.",
     "footage": "Archive close-up", "duration_s": 7,
     "image_prompt": "Tight close-up on a historical decision-moment artifact related to {subject}.",
     "video_prompt": "slow inward push on an archival object, 7 seconds, dramatic side lighting."},
    {"tier": 3, "section": "why_exists", "title": "Origin texture",
     "narration": "*(texture beat — material, place, era detail)*",
     "visual": "Texture-rich shot evoking the period when {subject} took its current shape.",
     "footage": "Archive texture", "duration_s": 6,
     "image_prompt": "Texture-rich period shot evoking the era when {subject} originated, fine grain.",
     "video_prompt": "static held texture shot, 6 seconds, faint film grain."},
    {"tier": 3, "section": "why_exists", "title": "Origin closing",
     "narration": "*(closing the origin section, transitioning forward)*",
     "visual": "Soft fade from period imagery to present day.",
     "footage": "Archive → modern transition", "duration_s": 7,
     "image_prompt": "Composite transitional image: period imagery fading toward modern view of {subject}.",
     "video_prompt": "slow cross-dissolve from archive to modern footage, 7 seconds."},

    # ---- WHAT MOST PEOPLE MISS (6) ---------------------------------------
    {"tier": 1, "section": "what_most_miss", "title": "One layer down",
     "narration": "*(\"the question that sits one layer down\")*",
     "visual": "Diagram with a top layer that fades to expose a deeper layer beneath.",
     "footage": "Diagram", "duration_s": 9,
     "image_prompt": "Diagram with a top layer fading to expose a deeper layer of {subject} beneath, schematic style.",
     "video_prompt": "top layer of diagram dissolves to reveal deeper structure, 7 seconds, slight inward push."},
    {"tier": 1, "section": "what_most_miss", "title": "Hidden actor",
     "narration": "*(reveal of the under-discussed players)*",
     "visual": "Quick reveal of the entities that quietly shape {subject}.",
     "footage": "Logo / actor reveal", "duration_s": 8,
     "image_prompt": "Composite revealing the under-discussed actors shaping {subject}, monolithic, dark background.",
     "video_prompt": "logos or actor placeholders fade in slowly on a dark background, 8 seconds."},
    {"tier": 2, "section": "what_most_miss", "title": "Insider vs outsider",
     "narration": "*(\"if you spend ten years inside something...\")*",
     "visual": "Split-screen: same scene from inside and outside.",
     "footage": "Stock split-screen", "duration_s": 8,
     "image_prompt": "Split composition: the same {subject} scene viewed from inside and outside simultaneously.",
     "video_prompt": "split-screen with two camera angles on the same subject, 8 seconds, both halves move slowly."},
    {"tier": 2, "section": "what_most_miss", "title": "Framing reveal",
     "narration": "*(\"the framing itself is shaping the answer\")*",
     "visual": "Visual metaphor for framing — a viewfinder, a frame within frame.",
     "footage": "Stylized animation", "duration_s": 7,
     "image_prompt": "Visual metaphor for framing: a frame within a frame around {subject}, conceptual.",
     "video_prompt": "camera reveals it was looking through a frame the whole time, 7 seconds."},
    {"tier": 3, "section": "what_most_miss", "title": "Detail beat",
     "narration": "*(one concrete example of the hidden mechanism)*",
     "visual": "Specific concrete example tied to {subject}.",
     "footage": "Stock — concrete example", "duration_s": 8,
     "image_prompt": "One concrete real-world example of the hidden mechanism behind {subject}.",
     "video_prompt": "static documentary-style shot of a real example, 8 seconds."},
    {"tier": 3, "section": "what_most_miss", "title": "Section close",
     "narration": "*(closing the what-most-miss section on a quiet note)*",
     "visual": "Quiet pull-back, palette cooling.",
     "footage": "Stock — quiet wide", "duration_s": 6,
     "image_prompt": "Quiet wide shot related to {subject}, palette cooling, contemplative tone.",
     "video_prompt": "slow pull-back, 6 seconds, palette desaturating subtly."},

    # ---- WHERE IT BECOMES FRAGILE (8) ------------------------------------
    {"tier": 1, "section": "fragility", "title": "Tonal shift",
     "narration": "*(\"now, here's where things get strange\")*",
     "visual": "Cooler color grade. Slower camera. Tonal handoff.",
     "footage": "Stock", "duration_s": 5,
     "image_prompt": "Cooler color grade, slower visual tempo, the same {subject} environment but with a sense of unease.",
     "video_prompt": "very slow camera move through a quiet environment, 5 seconds, cooler color tone."},
    {"tier": 1, "section": "fragility", "title": "Pressure points",
     "narration": "*(\"you start to see the seams\")*",
     "visual": "Diagram of {subject} with stress points highlighted in subtle warm color.",
     "footage": "Diagram", "duration_s": 9,
     "image_prompt": "Diagram of {subject} with stress points highlighted in subtle warm color, schematic overlay.",
     "video_prompt": "schematic overlay reveals stress markers one at a time, 9 seconds, locked-off."},
    {"tier": 2, "section": "fragility", "title": "Human assumptions",
     "narration": "*(\"most of those seams aren't technical, they're human\")*",
     "visual": "Faces, crowds, quotidian human behavior inside the system.",
     "footage": "Stock — human b-roll", "duration_s": 8,
     "image_prompt": "Faces or crowds — everyday human behavior inside the system around {subject}.",
     "video_prompt": "slow tracking shot through a crowd or workspace, 8 seconds, shallow focus."},
    {"tier": 2, "section": "fragility", "title": "First crack",
     "narration": "*(specific incident or pressure point)*",
     "visual": "News still / archival footage of a real failure tied to {subject}.",
     "footage": "Archive news", "duration_s": 9,
     "image_prompt": "News-still aesthetic showing a real failure or near-miss tied to {subject}.",
     "video_prompt": "static news-style footage, 9 seconds, slight zoom-in."},
    {"tier": 2, "section": "fragility", "title": "The bending",
     "narration": "*(\"it bends. and the bending is hard to see\")*",
     "visual": "Slow visual metaphor: structure under stress, holding shape but visibly deforming.",
     "footage": "Animation", "duration_s": 9,
     "image_prompt": "A structure under stress around {subject}, holding its shape but visibly deforming.",
     "video_prompt": "slow-motion deformation of a structure, 9 seconds, the bend barely visible."},
    {"tier": 3, "section": "fragility", "title": "Slow failure",
     "narration": "*(quiet, distributed failure mode)*",
     "visual": "Distributed visual metaphor: multiple small failures across a wide shot.",
     "footage": "Animation / split-grid", "duration_s": 8,
     "image_prompt": "Wide composition with multiple small distributed failure points tied to {subject}.",
     "video_prompt": "wide locked-off shot, 8 seconds, small failure points appear in sequence."},
    {"tier": 3, "section": "fragility", "title": "Failure detail",
     "narration": "*(one specific failure beat in detail)*",
     "visual": "Tight on a single failure point.",
     "footage": "Stock close-up", "duration_s": 7,
     "image_prompt": "Tight close-up on a single failure point related to {subject}.",
     "video_prompt": "slow inward zoom on a single failure detail, 7 seconds."},
    {"tier": 3, "section": "fragility", "title": "Fragility close",
     "narration": "*(landing the fragility section with one quiet held shot)*",
     "visual": "Held quiet shot. Tone cool, slightly tense.",
     "footage": "Stock — held shot", "duration_s": 7,
     "image_prompt": "Held cinematic shot evoking quiet unease around {subject}, cool grade.",
     "video_prompt": "locked-off shot, 7 seconds, almost no motion, cool color."},

    # ---- WHY IT MATTERS NOW (6) ------------------------------------------
    {"tier": 1, "section": "why_now", "title": "Modern shift",
     "narration": "*(opening of WHY IT MATTERS NOW)*",
     "visual": "Cut to present-day b-roll: news, screens, headlines tied to {subject}.",
     "footage": "Archive news", "duration_s": 7,
     "image_prompt": "Present-day b-roll: news screens, headlines, modern interfaces related to {subject}.",
     "video_prompt": "montage of contemporary screens and headlines, 7 seconds, quick but not frantic."},
    {"tier": 1, "section": "why_now", "title": "Convergence",
     "narration": "*(\"several pressures are converging at once\")*",
     "visual": "Animated diagram with multiple inputs converging on a single point.",
     "footage": "Diagram", "duration_s": 9,
     "image_prompt": "Animated diagram with multiple inputs converging on a single point representing {subject}.",
     "video_prompt": "arrows converging from different directions toward a central node, 9 seconds, smooth motion."},
    {"tier": 2, "section": "why_now", "title": "Specific case",
     "narration": "*(one specific contemporary case study tied to {subject})*",
     "visual": "Documentary-style coverage of a specific recent event tied to the topic.",
     "footage": "Archive / news", "duration_s": 9,
     "image_prompt": "Documentary-style coverage of a specific recent event tied to {subject}.",
     "video_prompt": "news-style footage, 9 seconds, slight zoom and reframe."},
    {"tier": 2, "section": "why_now", "title": "Stakes",
     "narration": "*(making the human stakes explicit)*",
     "visual": "Faces, hands, decisions — the human end of the system.",
     "footage": "Stock — human b-roll", "duration_s": 8,
     "image_prompt": "Human-stakes b-roll: hands, faces, decision-moment imagery tied to {subject}.",
     "video_prompt": "tight handheld documentary footage of human decisions, 8 seconds."},
    {"tier": 3, "section": "why_now", "title": "Why-now detail",
     "narration": "*(one concrete detail that grounds the urgency)*",
     "visual": "Modern interface or contemporary artifact tied to {subject}.",
     "footage": "Modern stock", "duration_s": 7,
     "image_prompt": "Modern interface or artifact tied to {subject}, contemporary cinematic look.",
     "video_prompt": "slow tracking shot across a modern interface, 7 seconds."},
    {"tier": 3, "section": "why_now", "title": "Why-now close",
     "narration": "*(closing the urgency section on a held quiet shot)*",
     "visual": "Long held shot. Quiet. Let the line land.",
     "footage": "Stock", "duration_s": 6,
     "image_prompt": "Quiet held wide shot tied to {subject}, contemplative.",
     "video_prompt": "locked-off held shot, 6 seconds, only ambient motion."},

    # ---- CLOSING (5) ------------------------------------------------------
    {"tier": 1, "section": "closing", "title": "Closing build",
     "narration": "*(opening line of the closing section)*",
     "visual": "Long quiet held shot of the central image of the episode.",
     "footage": "Stock — held", "duration_s": 6,
     "image_prompt": "Long quiet held shot of the central image of the episode about {subject}, atmospheric, lonely.",
     "video_prompt": "locked-off shot, 6 seconds, only ambient motion."},
    {"tier": 2, "section": "closing", "title": "Closing pull-back",
     "narration": "*(reveal: pull-back to the wider world)*",
     "visual": "Slow pull-back from a detail to the whole subject.",
     "footage": "Custom shot", "duration_s": 10,
     "image_prompt": "Pull-back composition revealing the wider world around {subject}, sense of scale and solitude.",
     "video_prompt": "slow continuous pull-back from detail to wide, 10 seconds, camera height rises slowly."},
    {"tier": 3, "section": "closing", "title": "Final image",
     "narration": "*(one strong memorable still)*",
     "visual": "One hero shot. Memorable. Held for the closing line.",
     "footage": "Hero still", "duration_s": 8,
     "image_prompt": "A final memorable hero still summarizing the episode's emotional weight on {subject}.",
     "video_prompt": "hold on a single still composition, 8 seconds, almost no motion."},
    {"tier": 2, "section": "closing", "title": "Final reflection",
     "narration": "*(closing reflection — one last beat)*",
     "visual": "Slow drift over a quiet final composition.",
     "footage": "Stock", "duration_s": 7,
     "image_prompt": "Quiet final composition tied to {subject}, atmospheric, reflective.",
     "video_prompt": "slow drift over a final composition, 7 seconds, sense of letting go."},
    {"tier": 3, "section": "closing", "title": "Sign-off",
     "narration": "*(closing line of the script — fade to black)*",
     "visual": "Final image. Hold. Cut to black.",
     "footage": "Hero still + black", "duration_s": 6,
     "image_prompt": "Black frame with the closing line of the script appearing as clean burned-in caption.",
     "video_prompt": "fade from black, final line appears, hold for 4 seconds, fade out, total 6 seconds."},
]


def _scene_duration_str(base_s: int, length: str) -> str:
    """Scale base duration by length to produce the cut pacing the spec asks for."""
    if length == "short":
        return f"{max(2, int(base_s * 0.5))}s"
    if length == "deep_dive":
        return f"{int(base_s * 1.4)}s"
    return f"{base_s}s"


def select_scenes(length: str) -> list[dict]:
    """Return the scene subset for the requested video length."""
    length = length_or_default(length)
    if length == "short":
        return [s for s in GENERIC_SCENES if s["tier"] == 1]
    if length == "deep_dive":
        return list(GENERIC_SCENES)
    return [s for s in GENERIC_SCENES if s["tier"] <= 2]


def render_storyboard_md(card: dict) -> str:
    """Render the storyboard.md body from the scene library."""
    ctx = template_context(card)
    length = ctx["video_length"]
    scenes = select_scenes(length)
    out: list[str] = []
    out.append(f"# Storyboard: {ctx['raw_topic']}\n")
    out.append(f"*Estimated total runtime: {ctx['runtime']} "
               f"(~{len(scenes)} scenes).*")
    out.append(f"*Pacing for this length: {ctx['cut_pacing']}.*\n")
    for i, scene in enumerate(scenes, start=1):
        duration = _scene_duration_str(scene["duration_s"], length)
        narration = scene["narration"].format(subject=ctx["subject"])
        visual = scene["visual"].format(subject=ctx["subject"])
        out.append(f"## Scene {i} — {scene['title']}\n")
        out.append(f"- **Narration:** {narration}")
        out.append(f"- **Visual:** {visual}")
        out.append(f"- **Duration:** {duration}")
        out.append(f"- **Footage type:** {scene['footage']}\n")
    return "\n".join(out)


_AI_PROMPTS_HEADER = """\
# AI Prompts: {raw_topic}

*One image prompt + one video prompt per storyboard scene.
Image prompts target Midjourney / Leonardo / Ideogram. Video
prompts target Runway / Pika / Luma.*

*Scene count for this length: **{scene_count} scenes**.*

## Format target — YouTube long-form

All output is for **16:9 horizontal long-form video**, not Shorts.
Every image and video prompt must produce a horizontal landscape
frame at 1920×1080 minimum (4K preferred).

| Surface                | Aspect ratio | Resolution                       |
| ---------------------- | ------------ | -------------------------------- |
| Long-form video        | 16:9         | 1920×1080 (1080p) or 3840×2160 (4K) |
| Thumbnail              | 16:9         | 1280×720                         |
| Shorts (separate file) | 9:16         | 1080×1920 (re-framed in CapCut)  |

If your AI tool defaults to square (1:1), override to 16:9
manually. The visual style anchor ends with `--ar 16:9` for
Midjourney; Leonardo / Ideogram have a 16:9 preset in the
generation panel; Runway / Pika expose aspect ratio in the
clip generation settings.

## Visual style anchor

Append this phrase to every image prompt to keep the scenes
feeling like the same world:

> `cinematic documentary still, 16:9 horizontal cinematic frame,
> 4K resolution (3840×2160), dark + neon palette with one warm
> rim light, photorealistic, anamorphic 35mm lens, shallow depth
> of field, ultra-detailed, glowing infrastructure / data-flow
> accents, high contrast, mystery and investigation atmosphere,
> no text, no logos --ar 16:9`

---

"""


_IMAGE_FRAME_SUFFIX = (
    "Horizontal 16:9 cinematic frame at 1920×1080 / 4K. --ar 16:9"
)
_VIDEO_FRAME_SUFFIX = (
    "Output: 16:9 horizontal landscape, 1920×1080, 24fps cinematic — "
    "for YouTube long-form, not Shorts."
)


def render_ai_prompts_md(card: dict) -> str:
    """Render the ai_prompts.md body from the scene library.

    Each image prompt is suffixed with an explicit 16:9 / 4K framing
    note so users who paste a single prompt without the visual style
    anchor still get horizontal output. Video prompts get an
    equivalent landscape suffix.
    """
    ctx = template_context(card)
    scenes = select_scenes(ctx["video_length"])
    parts: list[str] = [_AI_PROMPTS_HEADER.format(**ctx)]
    for i, scene in enumerate(scenes, start=1):
        image_prompt = scene["image_prompt"].format(subject=ctx["subject"])
        video_prompt = scene["video_prompt"].format(subject=ctx["subject"])
        parts.append(f"## Scene {i} — {scene['title']}\n")
        parts.append(
            f"**Image Prompt:** {image_prompt} {_IMAGE_FRAME_SUFFIX}\n"
        )
        parts.append(
            f"**Video Prompt:** {video_prompt} {_VIDEO_FRAME_SUFFIX}\n"
        )
    parts.append(
        "---\n\n"
        "## How to use these prompts\n\n"
        "1. Paste the image prompt for Scene 1 + the visual style anchor "
        "above into Midjourney / Leonardo / Ideogram. Confirm the output "
        "is 16:9 horizontal — if your tool defaults to square, switch "
        "to 16:9 in the panel. Generate 4 variants. Pick the strongest.\n"
        "2. Use image-to-video in Runway / Pika / Luma with the still "
        "you just generated, plus the video prompt. Confirm the output "
        "aspect ratio is 16:9 (1920×1080).\n"
        "3. Save each clip as `scene_XX.mp4` matching the scene number. "
        "Drop them on the CapCut timeline in order. Set the CapCut "
        "project to **1920×1080 / 16:9** before importing."
    )
    return "\n".join(parts)
