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

- **Language: Hindustani (Urdu/Hindi)** for all voices (2026-11-07). Write each line twice in the
  episode JSON: `say` in Devanagari (what Kokoro speaks, lang hi; it pronounces Devanagari best)
  and `caption` in Roman Urdu/Hindi (what viewers read). On-screen text is Roman Urdu/Hindi.
- **Cast names are Pakistani/Indian:** Constable Bilal (sidekick), Ustad Rafiq (cook), Begum
  Nusrat, Raju Mistri, Zara, Dr. Ayesha, Chacha Jamil, Faisal. Folder ids: bilal, rafiq, nusrat,
  raju, zara, ayesha, jamil, faisal. Voices: `cast/<id>/profile.json` -> `voice`, `studio/voices.py`.

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
| `studio/build_story.py` | Story episodes: shots on sets, cast puppets, per-character Kokoro voices, lip sync, word-by-word captions, camera moves, line-up, timer, stamps, music + SFX mix |
| `studio/make_cast_puppet.py` | Cuts `cast/<id>/art/acting.png` into `puppet/cast/<id>/` (poses on one canvas, feet on the bottom edge, talking mouths) |
| `studio/voices.py` | Kokoro voices per character: Hindi base voice + blend + speed + pitch (rubberband); `python studio/voices.py` writes an audition to `work/voices/` |
| `studio/audio.py` | Original music (D-minor detective loop) and SFX synthesized in code; ducking; loudnorm to -14 LUFS |
| `studio/lipsync.py` | Audio-only lip sync: loudness + brightness -> mouth shape per frame (A-G, None) |
| `studio/make_foxley_puppet.py` | Cuts the ChatGPT Foxley sheets in `source/` into `puppet/foxley/` |
| `studio/make_placeholder.py` | A code-drawn stand-in fox (`puppet/placeholder/`), for tests |
| `source/` | Foxley's original ChatGPT art: full body, turnaround, mouth sheet, expression sheet, study background |
| `puppet/foxley/` | Foxley talk/react puppet: `talk.png` + mouth patches + blink lids + 8 `pose_*.png`, `rig.json` |
| `cast/<id>/` | Each character: `profile.json` (look, voice, height) and `art/` (turnaround + acting sheets) |
| `cast/CAST.md` | Cast list, descriptions and the ChatGPT prompts to generate each character's art |
| `episodes/NNN_partK.json` | Episode scripts |
| `sets/<id>/background.png` | Reusable scene backgrounds; descriptions and the ChatGPT prompt in `sets/SETS.md` |
| `branding/avatar_*.png` | @AskFoxley profile pictures (1080x1080, circle-safe), made by `studio/make_avatar.py`; teal is the recommended one |
| `MOTION.md` | Animation rules (rossark-motion-skill method + this project's rig limits) |
| `.claude/skills/` | `video-director` (directing, timing, sound, QA) and `rossark-motion-skill` (making characters feel alive) |

## Commands

Story episodes (the main format):

```bash
.venv/bin/python studio/build_story.py episodes/s001_part1.json            # render to output/story_001_part1.mp4
.venv/bin/python studio/make_cast_puppet.py all                           # rebuild cast puppets from cast/<id>/art
```

Older talk/react format (Foxley talking head only):

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
- Story pipeline works end to end (`studio/build_story.py`): Episode 1 "The Stolen Painting"
  renders in both parts (`episodes/s001_part1.json` 34 s, `s001_part2.json` 24 s), passes
  video-director QA (no flashes, -13.5 LUFS). Rafiq is the culprit (post office closed on Sundays / itwaar).
- All 8 cast members + Foxley full body have art; puppets built for foxley, bilal, nusrat,
  rafiq, raju, zara (`puppet/cast/`). Mouth positions are hand-set in each profile.json
  (`art.mouth.center/radius`, acting-sheet pixels); the automatic finder is unreliable.
- 4 episode-1 sets + Foxley's study in `sets/`, with floor lines and sign boxes in set.json.
- The earlier talk/react format (Riddle #001, `episodes/001_part*.json`) still builds.

Next:
1. Owner review of the Hindustani Episode 1 and the voice audition; lock voices.
2. Build puppets for ayesha, jamil, faisal (set their mouth centre in profile.json first).
3. Motion upgrades from MOTION.md: blinks for the cast, head tilt on a separate head layer,
   a moment of silence/music drop before the reveal (QA asks for it).
4. Known nit: Rafiq's shocked pose loses a sliver of his hat (poses touch on his sheet).
5. More episodes: write new `episodes/sNNN_part1/2.json` using the cast and sets.

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
