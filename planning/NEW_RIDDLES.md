# New riddles plan (2026-11-17)

These are single Reels in Urdu with English subtitles: the answer is in the same video and it loops
back to the start. The formats are the ones that tested best:
- **wit** (a clever trick, "17 Oont" style)
- **choice / logic** (pick 1, 2 or 3, "Teen Darwaze" style)
- **whodunit A** (fast "who's lying", episode 6 style)

Every riddle needs three things: real stakes, a clue everyone understands, and an "aha" answer.
Props are drawn in code (like the camels and doors). Backgrounds come from ChatGPT (prompts in
`sets/SETS.md`). Only existing cast is used, so no new voices need approval.

| # | Title | Format | Set | New art |
|---|---|---|---|---|
| 1 | Jaadui Lathi | wit + whodunit | `kareem_shop` (have it) | none (sticks in code) |
| 2 | Pighalti Ice Cream | whodunit A | `town_park` (have it) | none (ice cream, 40°C sign in code) |
| 3 | Halka Sikka | logic | `kareem_shop` (have it) | none (scale and coins in code) |
| 4 | Kichad Ke Nishaan | whodunit A | `garden` (have it) | none (footprints in code) |
| 5 | Ek Maachis | quick paheli (15 s) | `kitchen` + night tint (have it) | none (lantern, stove, candle, match in code) |
| 6 | Nadi Paar | logic (steps) | **`river_ghat` (new)** | goat, wolf, grass, boat in code |
| 7 | Do Matke | logic (steps) | `desert_village` (prompt ready) | pots with water levels in code |
| 8 | Sach aur Jhooth ke Pehredaar | choice / logic | **`qila_gate` (new)** | none (Sher Khan and Bilal as guards) |
| 9 | Kaunsi Balti Pehle Bharegi? | visual, no language | **`chhat_rooftop` (new)** | pipes, tank and buckets in code |
| 10 | 17 Oont / Teen Darwaze redo | (made) | `desert_village` / `qila_doors` | waiting for the two backgrounds |

## 1. Jaadui Lathi (the magic stick)
- **Hook:** "Chor khud pakra gaya... kaise?" (the thief caught himself... how?)
- **Story:** Seth Kareem's gold coins are stolen from his shop. Suspects: Raju (1), Faisal (2),
  Sher Khan (3). Chacha Jamil gives each of them a stick of the same length: "Chor ki lathi raat
  bhar mein ek inch lambi ho jayegi" (the thief's stick will grow an inch overnight). A night
  tint, then morning: the three sticks side by side, and one is shorter.
- **Question:** "Chor kaun? Comment karo 1, 2 ya 3!" with a 3-second countdown.
- **Answer:** 2, Faisal. The sticks are not magic; Faisal got scared and cut his stick by an inch
  so it wouldn't look longer. ✗ JHOOT and the MUJRIM stamp.
- **Why it works:** the clue is visible (one short stick) and the trick is a big "aha".

## 2. Pighalti Ice Cream (tracker episode 7)
- **Hook:** "40 degree garmi... aur ek jhoot!" (40-degree heat... and one lie)
- **Story:** Dr. Ayesha's bicycle is stolen from the park. Chacha Jamil: reading the newspaper.
  Faisal: having lunch at the dhaba across the road. Zara: "Main ek ghante se is bench pe baith
  ke ice cream kha rahi hoon" (I've been on this bench eating ice cream for an hour). Her cone is
  perfectly frozen, and a shop sign reads 40°C.
- **Answer:** 3, Zara. In 40-degree heat ice cream melts in minutes, so she just bought it.

## 3. Halka Sikka (the light coin)
- **Hook:** "9 sikke, 1 naqli. Sirf 2 baar taraazu!" (9 coins, 1 fake, only 2 weighings)
- **Story:** Seth Kareem has 9 gold coins; one fake is lighter. Using the scale only twice, find it.
- **Answer (animated):**
  1. Split the coins 3-3-3 and weigh two groups. If they balance, the fake is in the third group;
     if not, it's in the lighter one.
  2. From those 3, weigh 1 against 1 the same way.
- **Why it works:** a well-known logic puzzle in a desi setting; comments split between
  "4-4-1" and "3-3-3".

## 4. Kichad Ke Nishaan (tracker episode 8)
- **Hook:** "Kichad ne chor ka raaz khol diya!" (the mud gave the thief away)
- **Story:** Begum Nusrat's rose-show trophy is taken after the rain. Ustad Rafiq: cooking in the
  kitchen. Chacha Jamil: never left his chair on the veranda. Raju: painting the gate. Muddy
  footprints lead to the trophy stand, with a small round dot beside every second step.
- **Answer:** Chacha Jamil. The dots come from his walking stick.

## 5. Ek Maachis (one matchstick, 15 s)
- **Hook:** "90% log galat jawab dete hain!"
- **Story:** A dark kitchen, a power cut. There is one matchstick, a lantern, a chulha (stove) and
  a candle. "Sab se pehle kya jalaoge?" (what do you light first?)
- **Answer:** the matchstick 😄
- **Why it works:** cheap daily filler; funny answer.

## 6. Nadi Paar (river crossing)
- **Hook:** "Sirf ek kashti... aur teen musibatein!" (one boat... and three problems)
- **Story:** Raju must take a goat (bakri), a wolf (bhediya) and a bundle of grass (ghaas) across
  the river. The boat carries Raju plus one thing. Left alone, the wolf eats the goat, and the
  goat eats the grass.
- **Answer (animated boat trips):**
  1. Take the goat across.
  2. Go back and take the wolf.
  3. Bring the goat back.
  4. Take the grass across.
  5. Go back for the goat.
- **Art:** new `river_ghat` set; the animals and the boat are drawn in code.

## 7. Do Matke (two pots)
- **Hook:** "Thik 4 litre paani... sirf do matkon se!" (exactly 4 litres... with only two pots)
- **Story:** Ustad Rafiq needs exactly 4 litres for a recipe. He has a 5-litre and a 3-litre
  matka at the village well.
- **Answer (water levels animate):**
  1. Fill the 5.
  2. Pour it into the 3, which leaves 2 in the 5.
  3. Empty the 3.
  4. Pour the 2 into the 3.
  5. Fill the 5 again.
  6. Top up the 3; that uses 1, leaving 4 in the 5.
- **Art:** reuses `desert_village` (the well).

## 8. Sach aur Jhooth ke Pehredaar (the truthful and lying guards)
- **Hook:** "Ek sawaal... aur zindagi ka faisla!" (one question... and your life depends on it)
- **Story:** Two doors: one leads out, the other to the hungry lion. Two guards, Sher Khan and
  Constable Bilal: one always tells the truth, one always lies, and nobody knows which. You may
  ask one guard one question.
- **Answer:** ask either guard "Doosra pehredaar kaunsa darwaza batayega?" (which door would the
  other guard say?) and take the other door. A short animation shows both cases.
- **Art:** new `qila_gate` set (two doors). The lion from "Teen Darwaze" is reused.

## 9. Kaunsi Balti Pehle Bharegi? (which bucket fills first?)
- **Hook:** "Sirf 1% log pehli baar mein sahi bataate hain!" (only 1% get it right first time)
- **Story:** On a rooftop, a water tank feeds a web of pipes into buckets 1, 2 and 3. Some pipes
  are blocked; the blocked ends are shown clearly.
- **Answer:** water flows along the pipes in an animation and only one route is open. Bucket 2.
- **Why it works:** needs no language, so Urdu, Hindi and English viewers all get it, and people
  replay it to trace the pipes.
- **Art:** new `chhat_rooftop` set; the pipes are drawn in code.

## Build order
1. **Now, no new art:** 1 Jaadui Lathi, 2 Pighalti Ice Cream, 3 Halka Sikka.
2. **When the owner sends backgrounds:**
   - `desert_village`: 7 Do Matke, plus the 17 Oont redo.
   - `qila_doors`: Teen Darwaze redo.
   - `river_ghat`: 6 Nadi Paar.
   - `qila_gate`: 8 Pehredaar.
   - `chhat_rooftop`: 9 Balti.
3. Use 4 and 5 as fillers between bigger ones.
