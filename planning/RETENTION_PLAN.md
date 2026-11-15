# Keeping viewers watching: review and new formats (2026-11-15)

Problem (owner): viewers skip the riddle Reels. This file reviews why, using our own videos and
outside research, and proposes formats to test. Nothing here is built yet.

## 1. Why the current videos get skipped

What the platforms reward (research, see Sources):
- The first 1-3 seconds decide most of the result. Average Reels watch time is about 8.5 s
  (Metricool, ~24M posts); average Shorts watch time is about 16 s.
- Instagram ranks Reels mainly on watch time, sends (DM shares) per reach and likes per reach.
  Replays and completion help.
- YouTube Shorts: aim for about 70% "viewed" (not swiped away) and under 25% swipe-away in the
  first 3 s. Targets for average view duration: over 60% for Shorts under 15 s, over 50% for
  15-30 s, over 40% for 30-60 s.
- Viral riddles are short (often under 15-20 s). They open with a bold challenge ("only 3% get
  this"), leave the answer to the end, and split viewers into two camps, which drives comments.
- Seamless loops raised retention in an Emplifi study (+9% at 3 s, +21% at 30 s), but only when
  viewers reach the loop point.

Our videos against that:

| What we do now | Why it loses viewers |
|---|---|
| Part 1 is 45-53 s; the question ("who is lying?") arrives at ~35 s | Most viewers have left after ~8 s; they never see the puzzle |
| Opening: title card plus a slow zoom on a dark room (0.7 night tint) | No challenge or stakes in the first second; dark frames look dull in a bright feed |
| Banter (Bilal's joke, Foxley's reply) before the alibis | Filler; it delays the puzzle |
| The clue is spoken; reveal is the next day | Muted viewers miss the clue. Non-followers (most of the reach) never see the answer, so the video gives no reward |
| Part 2 is 51-54 s of explanation | Low value for anyone who didn't see Part 1 yesterday |
| Puppet pose swaps, slow camera | Little motion per second compared with feed content |

The core of the idea is good: a desi cast, a "who is lying" puzzle and a clean reveal. The
problem is pacing and structure, not the concept.

## 2. New formats to test (each is a single, self-contained Reel)

### A. "30-second Jhooth Pakro" (rebuild of our detective format)
- **0.0-1.5 s, hook:** all three suspects on screen from frame 1. Big text and voice:
  "Sirf 5% log jhoota pakar paate hain. Tum?" (only 5% catch the liar).
- **1.5-15 s, alibis:** each suspect gets about 4 s and one line, with a big speech bubble on
  screen so it works muted. No banter.
- **15-19 s, question:** "Kaun jhoota? Comment karo!" with a 3-2-1 countdown and a ticking sound.
- **19-26 s, reveal in the same video:** zoom on the clue, ✗ JHOOT, MUJRIM stamp.
- **Last frame = first frame:** the video loops seamlessly, so viewers rewatch to check the clue.
- Bright scenes, a cut every 1.5-2 s, and the clue visible in the picture, not only spoken.
- Optional variant (A/B): hold the reveal back with "Jawab pinned comment mein" (answer in the
  pinned comment) so viewers comment and open the comments.

### B. "Pause karo aur dhoondo" (visual clue, the fastest to make)
- One detailed scene with a hidden clue, for example the calendar says Sunday, a wet umbrella,
  footprints, or a clock showing the wrong time.
- 5 s: "Is tasveer mein jhoot chhupa hai. 3 second!" (a lie is hidden in this picture), then a
  freeze with a countdown, then a circle and zoom on the clue.
- 10-15 s in total. People pause and rewatch, which counts as watch time, and it needs almost
  no voice.

### C. "Kya tum bach paoge?" (choice riddles)
- "Teen darwaze: aag, sher jo 3 saal se bhooka hai, paani se bhara kamra. Kaunsa?" (three doors:
  fire, a lion that hasn't eaten in 3 years, a flooded room; which one?)
- Pick 1, 2 or 3 and watch the answer. This style is proven on Bright Side-type pages, gets two
  camps arguing in the comments, and works without a detective.

### D. Desi paheli speed round (15 s)
- A classic Urdu/Hindi paheli with a twist, kinetic text, 3 s to think, then the answer.
- "90% log galat jawab dete hain" (90% of people get this wrong).
- A cheap daily filler between bigger episodes.

### E. Logic and visual puzzles with no language barrier
- Matchsticks, "which glass fills first", odd-one-out among emojis or letters.
- Works for Urdu, Hindi and English viewers at once, so it reaches more people.

**About Foxley:** keep him as the brand (a 1-second logo sting, the thumbnail badge, an
occasional "Foxley ka case" episode), not the narrator of every video. Formats B-E don't need
him; the human cast can carry A.

## 3. Production rules for every new video
1. A hook in the first second: on-screen text plus voice, and the puzzle visible straight away.
2. 15-30 s maximum. Cut anything that is not puzzle, clue or reveal.
3. Works muted: big text for every key fact; the clue can be seen, not only heard.
4. A visual change every 1.5-2 s (cut, zoom, pop-in); bright frames, no heavy night tint.
5. The answer is in the same video (or in the pinned comment for the comment-bait variant).
   Two-day splits only for special "big case" stories.
6. The end loops back to the start.
7. Comment prompts that split opinions ("Team 2 ya Team 3?").

## 4. Tools we can reuse from the poem pipeline ("Kids Poem Videos: Tools, Skills and Scripts" doc)

| Tool | Use for riddles |
|---|---|
| Whisper word timings (`align_lines.py`) | Captions that land exactly on each word instead of our estimated timing; snappier kinetic text |
| `make_set_layers.py` (back/mid/front layers) | Parallax camera moves, so static scenes feel alive |
| `make_blink.py`, `engine.js` PoseActor, contact shadows, creeping holds | More life in the puppets (blinks are already on our MOTION.md list) |
| Beat grid (`fit_grid.py`, `music_kids.py`) | Cut on the beat; rhythm keeps people watching |
| `check_timeline.py` | Pre-render rules: hook text by 1.0 s, no shot longer than 2.5 s, total 30 s or less |
| Somio AI | A 2-3 s sonic logo / jingle for @AskFoxley, so the channel is recognisable by sound |
| `make_thumbnail.py` | Already matched by our `make_thumbnails.js` |

New:
- **Social Media Skills plugin** (in the directory, not installed). Useful parts: hook-writer,
  viral-reverse-engineering, experimentation-and-ab-testing, youtube-shorts, tiktok-script,
  reels-script.
- **Instagram Trial Reels** (shown to non-followers first) and TikTok/YouTube analytics, to test
  hooks without hurting the main feed.

## 5. Two-week test plan
- **Week 1:** 1 Reel a day, rotating formats A, B, C, D (Urdu, English subtitles), all under
  30 s.
- **Measure per video:**
  - YouTube Studio: "viewed vs swiped away", average % viewed.
  - Instagram: 3-second hold rate, average watch time, sends.
  - TikTok: average watch time, % watched in full.
- **Week 2:** double down on the best two formats and test only the first 2 seconds (hook text
  and wording).
- Keep a simple sheet (or a dashboard artifact) with these numbers per video.

## Sources
- Metricool data via [later.com](https://later.com/blog/instagram-reels-algorithm/) and
  [metricool.com](https://metricool.com/youtube-shorts-algorithm/)
- Instagram signals: [dataslayer.ai](https://www.dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers), [reeldrop.io](https://www.reeldrop.io/blog/instagram-reels-algorithm/), [creatorflow.so](https://creatorflow.so/blog/instagram-algorithm/)
- Shorts benchmarks: [retensis.com](https://retensis.com/blog/youtube-shorts-analytics-metrics-explained), [1of10.com](https://1of10.com/blog/youtube-shorts-analytics/), [joyspace.ai](https://joyspace.ai/youtube-shorts-analytics-metrics-growth)
- Hooks: [go-viral.app](https://www.go-viral.app/blog/hook-first-3-seconds/), [cut.pro](https://cut.pro/en/blog/hooks-first-3-seconds-2026), [greenfroglabs.com](https://greenfroglabs.com/blog/anatomy-of-viral-hook)
- Riddle formats: [riddlespuzzle.com](https://riddlespuzzle.com/viral-tiktok-riddles-everyone-is-trying-to-solve/), [mindyourlogic.com (Detective Mehul)](https://www.mindyourlogic.com/detective-riddles)
- Loops: [emplifi.io](https://emplifi.io/?p=23678), [faceless.so](https://faceless.so/blog/how-to-make-a-looping-video-the-complete-guide)
