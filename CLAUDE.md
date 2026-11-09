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
- **Voices are locked (2026-11-07)** in `cast/<id>/profile.json` -> `voice`, with the approved
  clip in `cast/<id>/voice/sample.mp3`. ElevenLabs (free plan, built-in voices, model eleven_v3,
  needs `ELEVENLABS_API_KEY`): Foxley = Callum, Zara = Jessica, Faisal = Liam, Bunty = Will raised +4 semitones. Indic Parler-TTS
  (free, Apache-2.0, needs `HF_TOKEN`, runs in `.venv-parler`): Bilal, Nusrat, Raju, Ayesha
  (seed 1001), Rafiq, Jamil, Sher Khan and Seth Kareem (seed 7), each with a fixed description. Do not change a
  character's voice without the owner's approval. Pitch-lock each generated line to the
  character's median pitch so voices stay consistent. The owner will buy ElevenLabs Starter
  before monetizing (free plan is non-commercial).
- Voices are finalized BEFORE any video work; the owner wants to approve audio first.
- **Urdu only for now (2026-11-09).** Redos and new episodes are made in Urdu/Hindi only
  (`--lang ur`). Do not make English videos until the owner asks; keep the `en` text in episode
  JSON so English can be added later.
- **Cast names are Pakistani/Indian:** Constable Bilal (sidekick), Ustad Rafiq (cook), Begum
  Nusrat, Raju Mistri, Zara, Dr. Ayesha, Chacha Jamil, Faisal, Sher Khan (guard), Bunty (kid),
  Seth Kareem (shopkeeper). Folder ids: bilal, rafiq, nusrat, raju, zara, ayesha, jamil, faisal,
  sherkhan, bunty, kareem. Voices: `cast/<id>/profile.json` -> `voice`, `studio/voices.py`.

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
| `studio/render_lines.py` | Renders every episode line with the LOCKED voice (ElevenLabs / Indic Parler-TTS), pitch-locked to `cast/<id>/voice/sample.mp3`, cached in `work/voicecache/`; run with `.venv-parler` before `build_story.py` |
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
| `planning/riddle_tracker.xlsx` | The 30-episode plan (suspects, alibis, culprit, clue, sets, new art) and status tracker; built by `studio/make_riddle_plan.py` |
| `MOTION.md` | Animation rules (rossark-motion-skill method + this project's rig limits) |
| `.claude/skills/` | `video-director` (directing, timing, sound, QA) and `rossark-motion-skill` (making characters feel alive) |

## Commands

Story episodes (the main format):

```bash
.venv-parler/bin/python studio/render_lines.py episodes/s001_part1.json   # 1) voice lines (locked voices)
.venv/bin/python studio/build_story.py episodes/s001_part1.json            # 2) render to output/story_001_part1.mp4
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
1. Episode 1 re-rendered with the locked voices (2026-11-07): Part 1 44.5 s, Part 2 33.2 s,
   -14.1/-14.2 LUFS. The mix is written stereo (a mono mix measured ~3 dB louder once the
   player upmixed it). QA 'pops' warnings are intended pose changes, not glitches.
2. All 12 characters have puppets (`puppet/cast/`) and locked voices (2026-11-07).
3. Motion upgrades from MOTION.md: blinks for the cast, head tilt on a separate head layer,
   a moment of silence/music drop before the reveal (QA asks for it).
4. Puppet cut-outs cleaned (2026-11-07): `clear_enclosed_white` in make_cast_puppet.py removes
   background white trapped by the outline (arm/leg gaps, curls) and halos near the edge, keeping
   eyes, teeth and white clothing. Per-character `art.pose_margin` (Bunty, Rafiq) and
   `art.clip_at` (Rafiq) handle poses that overlap on the sheet. Rafiq's hat is whole now.
   Videos 1-5 were NOT re-rendered after this (owner said not to); they still show white gaps.
5. Episodes 2-5 done (2026-11-07) in BOTH languages: `episodes/s002-s005_part1/2.json` are bilingual
   (say = Devanagari, caption = Roman Urdu, en = English), written by `studio/write_episodes_2_5.py`.
   Build with `--lang ur|en` (render_lines.py takes `--lang ur,en`); outputs
   `output/story_00N_partK_{ur,en}.mp4`. Shot extras: `dark`, `rain`, cast `prop: kheer`, per-shot `signs`.
   English uses the SAME locked voices. Next: episodes 6+ from planning/riddle_tracker.xlsx.
6. New episode format (2026-11-09, owner approved on episode 2; apply to every episode from now on):
   - Part 1 ends with an extra shot in `foxley_study`: Foxley says "Raaz kal khulega! Follow karo,
     warna mujrim bach jayega!" under a big `banner` (RAAZ KAL KHULEGA! + pulsing FOLLOW @AskFoxley).
     On-screen calls to the audience use "karo" (casual), not "karein".
   - Part 2 checks EVERY alibi: one shot per innocent suspect (Foxley explains why the story holds,
     shot key `verdicts: [{"on": id, "ok": true, "line": 0}]` -> green "✓ SACH"), then the culprit
     last with `ok: false` -> red "✗ JHOOT", a beat of silence (`hold` ~1.1), then the MUJRIM stamp.
     Badge height above the head: `lift` (default 150). Badges and line-up numbers sit on a second
     world layer (`-w2`) above the night tint, so they stay bright.
   - `episodes/s002_part1/2.json` were edited by hand for this; do NOT re-run
     `write_episodes_2_5.py` for episode 2 (it would overwrite them). Episode 2 Urdu re-rendered
     with the cleaned puppets. Episodes 3-5 still use the old format.

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
