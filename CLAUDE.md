# Foxley Studio: riddle videos for Instagram, TikTok and YouTube Shorts

A side project: a daily riddle/mystery channel hosted by **Professor Foxley**, a fox
detective. Each riddle is posted as two vertical videos: **Part 1** poses the mystery and asks
viewers to comment their guess; **Part 2** (posted the next day) explains and reveals the
answer. Videos are made entirely in code in this repo and rendered to 1080x1920 MP4.

## First thing in a new session

```bash
bash setup.sh
```

This installs the Node tools, the Python env and the Kokoro voice model (they are not in git).
Then read `MOTION.md` (animation rules) and `cast/CAST.md` (the characters).

## The owner's rules (they override defaults)

- **Story format, not a talking head.** Each Part 1 is a short mystery with several scenes
  and cuts, several characters, and Foxley as the detective who solves it. A single static
  frame with one character was rejected (2026-11-07).
- **Background music in every video**, ducked under voices, plus sound effects.
- **Supporting characters are human cartoon characters, not animals.** They are a recurring,
  reusable cast in `cast/`; add new ones there when a story needs them.
- Engagement: Part 1 ends with a numbered line-up ("comment 1, 2 or 3") and a countdown.
- Everything is saved in this repo so any session can continue the work.

## Layout

| Path | What it is |
|---|---|
| `studio/build_episode.py` | Episode script (JSON) -> Kokoro voice -> lip sync -> HyperFrames HTML -> MP4 in `output/` |
| `studio/lipsync.py` | Audio-only lip sync: loudness + brightness -> mouth shape per frame (A-G, None) |
| `studio/make_foxley_puppet.py` | Cuts the ChatGPT Foxley sheets in `source/` into `puppet/foxley/` |
| `studio/make_placeholder.py` | A code-drawn stand-in fox (`puppet/placeholder/`), for tests |
| `source/` | Foxley's original ChatGPT art: full body, turnaround, mouth sheet, expression sheet, study background |
| `puppet/foxley/` | Foxley talk/react puppet: `talk.png` + mouth patches + blink lids + 8 `pose_*.png`, `rig.json` |
| `cast/<id>/` | Each character: `profile.json` (look, voice, height) and `art/` (turnaround + acting sheets) |
| `cast/CAST.md` | Cast list, descriptions and the ChatGPT prompts to generate each character's art |
| `episodes/NNN_partK.json` | Episode scripts |
| `sets/<id>/background.png` | Reusable scene backgrounds; descriptions and the ChatGPT prompt in `sets/SETS.md` |
| `MOTION.md` | Animation rules (rossark-motion-skill method + this project's rig limits) |
| `.claude/skills/` | `video-director` (directing, timing, sound, QA) and `rossark-motion-skill` (making characters feel alive) |

## Commands

```bash
.venv/bin/python studio/build_episode.py episodes/001_part1.json            # render to output/
.venv/bin/python studio/build_episode.py episodes/001_part1.json --no-render # just build/<name>/index.html
.venv/bin/python studio/make_foxley_puppet.py                                # rebuild Foxley's puppet from source/
```

Checking a build (from `build/<name>/`):

```bash
PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium npx hyperframes lint
```

```bash
PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium npx hyperframes snapshot --at 1,5,10
```

Checking a render:

```bash
.venv/bin/python .claude/skills/video-director/scripts/qa_video.py output/foxley_001_part1.mp4 --out work/qa/
```

## Episode script format (current talk/react builder)

```json
{"number": 1, "part": 1, "difficulty": 2, "voice": "am_puck", "handle": "@AskFoxley",
 "riddle": "…", "answer": "…", "explanation": "…",
 "segments": [
   {"pause": 0.8, "expression": "smug"},
   {"say": "Let's see how sharp you really are.", "show": "riddle"},
   {"timer": 5, "expression": "thinking"},
   {"say": "Drop your answer in the comments!", "show": "cta"}
 ]}
```

`say` lines lip-sync on the front-facing head; `pause`/`timer` segments cut to the reaction
pose for `expression` (smug, proud, thinking, shocked, laugh, point, excited, facepalm, wink).
`show` triggers on-screen graphics: riddle, cta, answer, explain, stamp.

## Status and next steps (keep this section current)

Done:
- Pipeline works end to end: Kokoro voice, lip sync, Foxley talk/react puppet from the owner's
  art, study background, riddle card, timer, answer reveal, "Case closed!" stamp, CTA.
- Riddle #001 ("The more you take, the more you leave behind" / Footsteps) renders in both parts.
- Cast of 8 human characters designed (`cast/`), with ChatGPT prompts, and **all 8 have their
  turnaround + acting sheets** in `cast/<id>/art/`, imported and checked with
  `studio/check_cast_art.py` (pose split, mouth-closed vs mouth-open alignment; see each
  `profile.json` -> `art.mouth` for how that character lip-syncs). Puppets not built yet.
- Open question for the owner: Mia's mint hoodie + messy dark ponytail resembles Vanellope
  (Wreck-It Ralph); suggested regenerating with a different hoodie colour/hairstyle.

Next:
1. Owner generates art (Foxley's full-body acting sheet is in `cast/foxley/art/`):
   the 4 episode-1 sets in `sets/SETS.md` (mansion_living_room, garden, post_office_street,
   small_bedroom). Signs are generated blank; clue text is drawn in code.
2. Build the story/scene engine: multiple shots and backgrounds, camera moves, several
   characters per shot, per-character voices, word-by-word captions, numbered line-up.
3. Music and SFX: an original mystery score synthesized from the timeline (see
   video-director `references/sound.md`), ducking, tick, reveal hit, stamp. Loudness -14 LUFS.
4. First story episode: "The Stolen Painting" (Sunday noon; Marco says he was at the post
   office, which is closed on Sundays).
5. Audition and lock voices for Foxley and each cast member.

## Environment notes (cloud sessions)

- Chrome in the renderer cannot reach CDNs: compositions load GSAP from a local
  `vendor/gsap.min.js` (the builder copies it from `node_modules`). Never reference a CDN.
- Render with `PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium` (the builder sets it).
- freesound.org refuses requests from cloud servers (403 even with a valid
  `FREESOUND_API_KEY`). Don't try to work around it; use synthesized audio or tracks the
  owner uploads (Pixabay Music / YouTube Audio Library, CC0 preferred).
- The PyPI package `freesound-python` is a name-squat; `requirements.txt` pins the real client
  from GitHub.
- Downloading prebuilt binaries (e.g. Rhubarb lip sync) is blocked; lip sync is our own code.
