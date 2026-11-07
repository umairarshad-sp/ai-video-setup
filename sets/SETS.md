# Foxley Studio sets (backgrounds)

Each set is one empty vertical background that stories can reuse. Save each image as
`sets/<id>/background.png`. Foxley's study already exists (`source/background.png`).

## Rules every background follows

These keep characters looking right when they are placed into any scene:

1. **Vertical 9:16**, no characters, no animals, no text, letters or numbers anywhere
   (signs are left blank; the code writes on them, so any clue text is always spelled right).
2. **Same camera in every set:** eye level, looking straight at the back wall, like a stage.
3. **Same floor line:** the floor meets the back wall at about **60% of the way down** the
   image, and the **bottom third is open, empty floor** with nothing in front. That is where
   the characters stand, so they are the same size in every scene.
4. **Calm detail:** soft, even lighting, no strong shadows, no busy clutter in the middle. The
   top quarter can hold detail (shelves, windows, sky); title cards go there.
5. **Same art style as the characters:** attach `source/fullbody.png` (Foxley) as the style
   reference in every chat.

## Prompt template

Attach Foxley's image, then paste this with the set's description:

> In exactly the same art style as the attached character (thick dark outlines, flat colours
> with soft cel shading, warm cosy cartoon look), create a vertical 9:16 background of
> **[SET DESCRIPTION]**. Eye-level camera looking straight at the back wall, like a stage.
> The floor meets the back wall about 60% of the way down the image, and the bottom third is
> open, empty floor with nothing in front, where characters will stand. Soft even lighting,
> no strong shadows, the centre kept uncluttered. No people, no animals, no characters, no
> text, no letters or numbers anywhere; any signs are blank.

---

## Episode 1: "The Stolen Painting" (make these first)

| ID | Set | Used for |
|---|---|---|
| `mansion_living_room` | Penelope's living room | The crime scene, the suspect line-up, the reveal |
| `garden` | Penelope's rose garden | Penelope's alibi ("watering my roses") |
| `post_office_street` | A town street with the post office | Marco's alibi, and the clue (closed on Sundays) |
| `small_bedroom` | Rocky's little apartment bedroom | Rocky's alibi ("asleep after my night shift") |

**`mansion_living_room`**
> a grand, cosy mansion living room in daylight: a tall back wall with green damask
> wallpaper, a big ornate gold picture frame hanging in the centre of the wall that is
> completely EMPTY (only the bare wall shows inside it), a crystal chandelier, a marble
> fireplace on one side, a velvet purple armchair and a small side table with a vase of
> flowers at the far left and right edges, a polished wooden floor with a round rug

**`garden`**
> a sunny English rose garden at noon behind a mansion: rose bushes in red, pink and white
> along the back, a white wooden trellis arch with climbing roses, a stone birdbath, a
> green watering can resting by a flower bed at the side, blue sky with a few soft clouds,
> a light gravel path and short lawn as the open floor

**`post_office_street`**
> a charming small-town street on a quiet sunny day: the front of a little red-brick post
> office in the centre with a dark green door that is shut, closed window blinds, a red
> post box beside the door and one large BLANK white sign board hanging on the door; a
> bakery and a flower shop on either side with blank awnings, a lamp post, a wide
> pavement as the open floor

**`small_bedroom`**
> a small, messy but cosy apartment bedroom with the curtains closed and soft dim daylight
> coming through: an unmade single bed against the back wall with a rumpled blanket, a
> bedside table with an alarm clock (no numbers on its face), work boots and a toolbox on
> the floor by the wall, a poster frame with an abstract picture, a wooden floor

---

## More sets for future stories (make them when a story needs one)

| ID | Description to paste in |
|---|---|
| `kitchen` | a busy, warm restaurant kitchen: copper pots hanging from a rack, a big stove with a bubbling pot, a wooden counter with vegetables and a rolling pin, a tiled back wall, a fresh pie cooling on a windowsill, a tiled floor (Marco's place) |
| `museum_gallery` | a grand museum gallery hall: tall marble columns, framed paintings on the walls, a glass display case on a pedestal at one side, a velvet rope barrier, a shiny stone floor (Amara's museum) |
| `police_station` | a small, friendly town police station office: a wooden desk with a lamp and stacks of paper, a cork board with pinned photos and red string, a filing cabinet, a coat rack with a police cap, a tiled floor (Barnaby's desk) |
| `town_park` | a sunny town park: a winding path, green trees, a wooden bench, a small pond with a duck house, a bandstand far in the back, flower beds, a grass and path floor |
| `bakery_shop` | inside a cosy bakery: glass display counter with cakes and bread, shelves of loaves on the back wall, a chalkboard menu that is blank, a cash register with no numbers, a checked tile floor |
| `apartment_hallway` | an old apartment building hallway: a row of numbered-looking doors left blank, a patterned carpet runner, a wall lamp, a potted plant, a radiator, a window at the end (Wally's building) |
| `train_station` | a small old-fashioned train station platform: a waiting bench, a big round station clock with no numbers, a ticket window, luggage trolley, the platform edge as the open floor, a train track at the back |
| `night_street` | the same small-town street as `post_office_street` but at night: warm street lamps, dark blue sky with stars, glowing shop windows, a wet pavement with soft reflections |

## Adding a set later

Make a folder `sets/<id>/`, write a description like the ones above (place, time of day,
3-5 key objects, what sits in the centre of the back wall, what the floor is), and run the
template. If a story needs a clue in the picture, describe it clearly and leave any writing blank.
