# Foxley Studio

Daily riddle and mystery videos hosted by **Professor Foxley**, a fox detective, made entirely
in code and rendered to vertical 1080x1920 MP4 for Instagram Reels, TikTok and YouTube Shorts.

Every riddle has two videos: **Part 1** sets up the mystery and asks viewers to comment their
guess, and **Part 2** (the next day) explains it and reveals the answer.

## Quick start

```bash
bash setup.sh
```

```bash
.venv/bin/python studio/build_episode.py episodes/001_part1.json
```

The video appears in `output/`.

## How it works

1. **Script:** an episode is a JSON file in `episodes/` listing what each character says, their
   expression, and what appears on screen.
2. **Voice:** each line is spoken by [Kokoro](https://github.com/thewh1teagle/kokoro-onnx), a
   free text-to-speech model that runs locally.
3. **Lip sync:** the voice is analysed frame by frame to pick a mouth shape.
4. **Animation:** the characters are built from ChatGPT drawings cut into layers, and animated
   with [HyperFrames](https://hyperframes.heygen.com) and GSAP.
5. **Render:** HyperFrames renders the composition frame by frame to MP4.

## What's in here

| Folder | Contents |
|---|---|
| `studio/` | The pipeline code |
| `source/` | Foxley's original artwork |
| `puppet/` | Foxley cut into animation layers |
| `cast/` | The recurring characters and the prompts to draw them (`cast/CAST.md`) |
| `episodes/` | Episode scripts |
| `.claude/skills/` | Two Claude Code skills used for directing and animation |
| `MOTION.md` | Animation rules for this project |
| `CLAUDE.md` | Project notes for Claude Code sessions |

## Credits

- `.claude/skills/video-director` by [win4r](https://github.com/win4r/video-director), MIT licence.
- `.claude/skills/rossark-motion-skill` by [rossark0](https://github.com/rossark0/rossark-motion-skill), MIT licence.
