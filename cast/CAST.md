# Foxley Studio cast

> **Language and voices (2026-11-07):** the channel is in Hindustani (Urdu/Hindi). Names are
> Pakistani/Indian. Each character's voice recipe (Kokoro Hindi voice, blend, speed, pitch) is in
> `cast/<id>/profile.json` -> `voice`; audition them all with `.venv/bin/python studio/voices.py`.
> The voice column in the table below is out of date; profile.json is the source of truth.

Professor Foxley is the detective in every story. Everyone else is a human cartoon
character who can come back in any riddle as a suspect, witness or victim. Each one has a
folder here: `profile.json` (look, personality, voice, height) and `art/` (their sheets).

| ID | Character | Role | What they look like | Voice | Height* |
|---|---|---|---|---|---|
| `bilal` | **Constable Bilal** | Foxley's sidekick | Tall, skinny, ginger, freckles, oversized police cap over his eyes | am_eric | 1.10 |
| `rafiq` | **Ustad Rafiq** | Suspect | Short and round, giant curly moustache, very tall chef hat, checked apron | am_onyx | 0.85 |
| `nusrat` | **Begum Nusrat** | Suspect / victim | Elderly rich lady, silver bun, purple dress, pearls, feather boa | bf_emma | 0.95 |
| `raju` | **Raju Mistri** | Suspect (red herring) | Stocky handyman, backwards red cap, blue overalls, toolbelt | am_adam | 1.00 |
| `zara` | **Zara** | Suspect / witness | Teen girl, black ponytail, mint hoodie, headphones, phone | af_nova | 0.80 |
| `ayesha` | **Dr. Ayesha** | Suspect / expert | Museum curator, afro puff, lab coat, orange turtleneck, round glasses | af_heart | 0.95 |
| `jamil` | **Chacha Jamil** | Suspect / witness | Grumpy old man, bald, huge white eyebrows and moustache, cardigan, cane | bm_george | 0.85 |
| `faisal` | **Faisal** | Suspect | Cheerful delivery man, bright yellow uniform, green bike helmet, parcel | am_liam | 0.95 |

\*Height relative to Foxley, so line-ups look right. Voices are first picks; we will audition them.

Every character has their own signature colour and silhouette (the hat, the moustache, the
headphones...) so viewers recognise them in a split second on a phone screen.

---

## The art each character needs (two images)

**Image 1, turnaround sheet:** front, three-quarter, side and back. This locks in the design so
every later image of the character matches it.

**Image 2, acting sheet:** the poses the animation actually uses. Poses 1 and 2 must be the
same pose with only the mouth different. That pair is how the character lip-syncs.

The characters only need to face **left** in the acting sheet. Facing right is made by
mirroring the image, which is why there must be **no text, logos or numbers on clothing**.

### How to generate them in ChatGPT

1. Start a chat, **attach `source/fullbody.png` (Foxley)** as the style reference.
2. Paste **Prompt 1** with the character's description. Regenerate until the design is right.
3. In the same chat, **attach the turnaround you chose** and paste **Prompt 2**.
4. Save both as PNGs into `cast/<id>/art/` as `turnaround.png` and `acting.png`.

**Prompt 1: turnaround sheet**

> In exactly the same art style as the attached fox character (thick dark outlines, flat
> colours with soft cel shading, cute chibi proportions about 3 heads tall, big expressive
> eyes), create a character turnaround sheet of a HUMAN cartoon character: **[DESCRIPTION]**.
> Show the same character 4 times in a row, full body, standing neutral, evenly spaced and the
> same size: front view, three-quarter view, side view, back view. Plain white background, no
> shadows on the floor, no text, no labels, no logos or writing on the clothes.

**Prompt 2: acting sheet** (attach the turnaround)

> Using the attached turnaround as the exact character design (same face, hair, outfit,
> colours and proportions) and the same art style, create an acting sheet of this character.
> 6 poses in one row, full body, all in three-quarter view facing LEFT, evenly spaced, the
> same size and the same height, feet on the same baseline: (1) standing neutral, mouth
> closed; (2) the EXACT same pose as pose 1, only the mouth open as if talking; (3) nervous,
> sweating, eyes looking away; (4) shocked, mouth wide open, hands up; (5) caught and guilty,
> sheepish smile, shoulders shrugged; (6) **[SIGNATURE POSE]**. Plain white background, no
> floor shadows, no text, no labels, no speech bubbles or effects.

### Descriptions and signature poses to paste in

**Constable Bilal**
- DESCRIPTION: a tall, skinny young police officer with a long neck, a big nose, freckles and
  messy ginger hair; an oversized navy police cap that slips over his eyes, a navy uniform a
  size too big, a shiny badge, a small notepad and pencil
- SIGNATURE POSE: pointing forward proudly with total (wrong) confidence

**Ustad Rafiq**
- DESCRIPTION: a short, round, jolly chef with rosy cheeks, a huge curly black moustache and
  thick eyebrows; a very tall white chef hat, a white double-breasted chef jacket, a red
  neckerchief and a red-and-white checked apron, holding a wooden spoon
- SIGNATURE POSE: proudly holding up a steaming pie on a tray

**Begum Nusrat**
- DESCRIPTION: an elegant, wealthy elderly lady with a tall silver-grey hair bun, cat-eye
  glasses on a chain and a proud raised chin; a long purple dress, a white feather boa, a big
  pearl necklace and a small purple handbag
- SIGNATURE POSE: dramatically fainting with the back of her hand on her forehead

**Raju Mistri**
- DESCRIPTION: a stocky, friendly handyman with tan skin, short black stubble, a cheeky
  gap-toothed grin and a backwards red cap; faded blue overalls over a yellow T-shirt, a brown
  toolbelt with a hammer and wrench, scuffed work boots
- SIGNATURE POSE: holding a big wrench over his shoulder, giving a thumbs up

**Zara**
- DESCRIPTION: a clever teenage girl with a high black ponytail, round face and confident
  smirk; an oversized mint-green hoodie, big white headphones around her neck, black leggings,
  chunky white sneakers, always holding her phone
- SIGNATURE POSE: holding her phone up, filming, with a smug look

**Dr. Ayesha**
- DESCRIPTION: a brilliant museum curator and scientist with dark brown skin, a big round afro
  puff and gold hoop earrings; a white lab coat over an orange turtleneck, round tortoiseshell
  glasses, holding a clipboard
- SIGNATURE POSE: pushing her glasses up with one finger, clipboard under her arm

**Chacha Jamil**
- DESCRIPTION: a grumpy old man with a bald head, huge bushy white eyebrows and a white walrus
  moustache, slightly hunched; a brown knitted cardigan with leather elbow patches, beige
  trousers, slippers, leaning on a wooden cane
- SIGNATURE POSE: shaking his cane angrily in the air

**Faisal**
- DESCRIPTION: a cheerful, energetic young delivery man with brown skin, a big smile, short
  wavy black hair and a thin moustache; a bright yellow delivery uniform with a cap, a green
  bike helmet hanging from his arm and a big cardboard parcel
- SIGNATURE POSE: running in a hurry, holding the parcel under one arm

---

## Foxley still needs one more sheet

The talking head and expression sheets already work. For story scenes he also needs a
full-body acting sheet. Attach `source/fullbody.png` and paste:

> Using the attached fox detective as the exact character design and art style, create an
> acting sheet of him: 6 poses in one row, full body, all in three-quarter view facing RIGHT,
> evenly spaced, the same size, feet on the same baseline: (1) standing neutral, mouth closed;
> (2) the EXACT same pose as pose 1, only the mouth open as if talking; (3) pointing
> accusingly forward; (4) bending forward examining something with his magnifying glass;
> (5) thinking with a hand on his chin; (6) confident thumbs up with a wink. Plain white
> background, no floor shadows, no text, no labels, no effects.

Foxley faces RIGHT and the suspects face LEFT, so in a two-shot they face each other without
mirroring anyone.

## Adding a new character later

Copy any folder, edit `profile.json`, write a DESCRIPTION in the same style as above (body
shape, face, hair, 3-4 clothing items, one prop, one signature colour), and run both prompts.
