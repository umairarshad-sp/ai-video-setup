# New riddles, batch 2 (2026-11-23)

Same approach as batch 1:
- single Reel, Urdu with English subtitles
- hook on the first frame, 3-second countdown, answer in the same video, loops back to the start
- existing cast with approved voices, props drawn in code

Only one new background is needed (`raat_pul`).

| # | Title | Type | Set | New art |
|---|---|---|---|---|
| 10 | Teen Bulb | logic | `apartment_lobby` + `apartment_hallway` (have) | none |
| 11 | Geela Rang | who's lying | `town_park` (have) | none (paint stripes and sign in code) |
| 12 | Umar Ki Paheli | quick maths trap (15-20 s) | `garden` (have) | none |
| 13 | Andhere Mein Moze | quick logic (20 s) | `small_bedroom` (have) | none (socks in code) |
| 14 | Raat Ka Pul | logic, step by step | **`raat_pul` (new)** | lantern in code |
| 15 | Kuen Ka Paani | wit story | `desert_village` (have) | none |
| 16 | Teen Shikari | wit / trick question | `river_ghat` (have) | fish in code |
| 17 | Chhe Glass | picture puzzle | `kitchen` (have) | glasses in code |

## 10. Teen Bulb (three bulbs)
- **Hook:** "Sirf ek baar upar ja sakte ho!" (you can only go upstairs once)
- **Story:** Raju is fixing the building wiring. Three switches in the lobby control three bulbs
  upstairs, but which switch runs which bulb? He can go upstairs only once.
- **Answer:**
  1. Turn switch 1 on for 5 minutes, then off.
  2. Turn switch 2 on and go upstairs.
  3. The lit bulb is switch 2, the warm one is switch 1, the cold one is switch 3.
- **Visual:** switches, bulbs with a glow, and heat lines on the warm bulb.

## 11. Geela Rang (wet paint)
- **Hook:** "Taaza rang ne chor pakarwa diya!" (fresh paint caught the thief)
- **Story:** Zara's phone is stolen from the park bench, which has just been painted green and has a
  "TAAZA RANG" (wet paint) sign.
  - Faisal: "I was at the dhaba."
  - Bunty: "I never even went near the bench!"
  - Raju: "I was painting the bench... over there."
- **Answer:** Bunty. There are green stripes on the back of his shorts.
- **Note:** Raju has paint on his hands, but that's expected for the painter. It's a decoy.

## 12. Umar Ki Paheli (the age trap)
- **Hook:** "90% log 30 bolte hain!" (90% of people say 30)
- **Story:** Chacha Jamil: "Jab main 6 saal ka tha, meri behan meri aadhi umar ki thi. Ab main 60
  ka hoon. Behan kitni saal ki hai?" (when I was 6 my sister was half my age; I'm 60 now; how old
  is she?)
- **Answer:** 57. She was 3, so she is 3 years younger, always.

## 13. Andhere Mein Moze (socks in the dark)
- **Hook:** "Bijli gayi... aur moze ka jora chahiye!" (the power's out... and you need a pair of socks)
- **Story:** Bunty's drawer has 10 black and 10 white socks, in the dark. "Kam se kam kitne nikaaloge
  ke ek jora pakka mil jaye?" (at least how many must you take to be sure of a pair?)
- **Answer:** 3. With only two colours, 3 socks always include a pair.

## 14. Raat Ka Pul (the night bridge)
- **Hook:** "17 minute... ek laltain... chaar log!" (17 minutes, one lantern, four people)
- **Story:** A rope bridge at night. Bunty crosses in 1 min, Zara 2, Raju 5, Chacha Jamil 10. At most
  2 on the bridge at once, they must carry the lantern, and a pair walks at the slower one's speed.
  Can everyone cross in 17 minutes?
- **Answer:**
  1. Bunty + Zara cross (2 min). Bunty returns (1).
  2. Raju + Jamil cross (10). Zara returns (2).
  3. Bunty + Zara cross (2).
  4. Total: 17.
- **Visual:** an animated crossing with a running minute counter.

## 15. Kuen Ka Paani (the well's water)
- **Hook:** "Kuan bik gaya... paani nahi!" (the well was sold... the water wasn't)
- **Story:** Seth Kareem sells Raju his well. Next day: "Kuan tumhara, paani mera! Paani ka kiraya do."
  (the well is yours, the water is mine, pay rent for it)
- **Question:** "Raju kya jawab de?" (what should Raju say?)
- **Answer:** Raju: "Theek hai Seth ji, apna paani mere kuen se nikaal lo... warna kuen mein rakhne
  ka kiraya do!" (fine, take your water out of my well, or pay rent for keeping it there!)
  KAMAAL stamp.

## 16. Teen Shikari (three fishermen)
- **Hook:** "Do baap, do bete... phir bhi teen machhliyan!" (two fathers, two sons, still three fish)
- **Story:** "Do baap aur do bete machhli pakarne gaye. Teen machhliyan pakri, aur sab ko ek-ek
  mili. Kaise?" (two fathers and two sons went fishing, caught three fish, and each got one; how?)
- **Answer:** Only three people: Chacha Jamil (grandfather), Raju (his son), Bunty (Raju's son).
  Jamil and Raju are the two fathers; Raju and Bunty are the two sons.

## 17. Chhe Glass (six glasses)
- **Hook:** "Sirf EK glass chhoo sakte ho!" (you may touch only ONE glass)
- **Story:** Six glasses in a row: the first three full of lassi, the last three empty. Make them
  alternate full-empty-full-empty by touching only one glass.
- **Answer:** Pick up glass 2, pour it into glass 5, and put it back.

## Build order
1. **Quick ones first, no new art:** 12 Umar, 13 Moze, 17 Glass.
2. **Then:** 10 Bulb, 11 Geela Rang, 15 Kuan, 16 Shikari.
3. **When the `raat_pul` background is ready:** 14 Raat Ka Pul.
