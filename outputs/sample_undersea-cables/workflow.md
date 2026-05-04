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
