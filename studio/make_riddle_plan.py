"""Build planning/riddle_tracker.xlsx: 30 Foxley mysteries + what art each one needs.

    .venv/bin/python studio/make_riddle_plan.py
"""
import os
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "planning", "riddle_tracker.xlsx")

EXISTING_SETS = {"mansion_living_room", "garden", "post_office_street", "small_bedroom", "foxley_study"}
NEW_CAST = {"Sher Khan", "Bunty", "Seth Kareem"}

# (title roman, title english, victim, what happened (hook),
#  [suspect: alibi] x3, culprit (lineup no.), clue type, the clue (shown in Part 1),
#  explanation (Part 2), difficulty 1-5, sets)
EP = [
 ("Painting Kis Ne Churayi?", "Who stole the painting?", "Begum Nusrat",
  "Nusrat's painting vanishes from her living room on Sunday at noon.",
  ["Ustad Rafiq: was at the post office posting a letter to his ammi",
   "Zara: was filming the roses in the garden all afternoon",
   "Raju Mistri: was asleep after his night shift"], 1, "Closed on that day",
  "The sign on the post office door: CLOSED ON SUNDAYS.",
  "It was Sunday (itwaar). The post office is closed on Sundays, so Rafiq was never there.", 1,
  ["mansion_living_room", "post_office_street", "garden", "small_bedroom"]),
 ("Andhere Ka Cricket", "Cricket in the dark", "Begum Nusrat",
  "Nusrat's pearl necklace disappears during two hours of load-shedding at night.",
  ["Raju Mistri: was outside trying to start the generator",
   "Zara: was on a phone call with her friend in the dark",
   "Chacha Jamil: was watching the cricket match on TV all evening"], 3, "Impossible during a power cut",
  "Foxley's opening line: the whole street has had no electricity for two hours.",
  "There was no electricity, so the TV could not have been on. Jamil was not watching cricket.", 1,
  ["mansion_living_room", "apartment_hallway", "small_bedroom"]),
 ("Kheer Kis Ne Khayi?", "Who ate the kheer?", "Ustad Rafiq",
  "Rafiq's big pot of Eid kheer is found empty in his kitchen.",
  ["Zara: was in the garden taking photos",
   "Faisal: just arrived with a parcel, never went near the kitchen",
   "Raju Mistri: was fixing the tap in the bathroom"], 2, "Physical trace",
  "A close-up shows white kheer and a raisin stuck in Faisal's moustache.",
  "Faisal says he never went near the kitchen, but there is fresh kheer on his moustache.", 1,
  ["kitchen", "garden"]),
 ("Barish Wali Raat", "The rainy night", "Dr. Ayesha",
  "A diamond goes missing from the museum during a night of heavy rain.",
  ["Dr. Ayesha: left the museum at 6 pm",
   "Raju Mistri: was inside fixing the gallery lights",
   "Sher Khan: stood guard at the open front gate all night"], 3, "Weather contradiction",
  "It rained heavily all night, yet Sher Khan's uniform, cap and shoes are completely dry.",
  "Anyone standing at an open gate all night in that rain would be soaked. Sher Khan was inside.", 2,
  ["museum_gallery", "night_street"]),
 ("Toota Sheesha", "The broken window", "Chacha Jamil",
  "A cricket ball smashes Jamil's window and the ball is missing.",
  ["Bunty: 'I didn't even see the window! And anyway, the ball must have rolled under the sofa.'",
   "Zara: was recording a dance video on the rooftop",
   "Faisal: was delivering parcels on the next street"], 1, "Guilty knowledge",
  "Bunty's own words: he knows the ball went under the sofa.",
  "Nobody had said where the ball landed. Only the person who hit it could know it rolled under the sofa.", 2,
  ["gali_street", "apartment_hallway"]),
 ("31 November", "The 31st of November", "Constable Bilal",
  "Bilal's wallet is stolen from his desk at the police station.",
  ["Faisal: was delivering parcels all day",
   "Raju Mistri: shows a bus ticket proving he was out of town on 31 November",
   "Zara: was at college; her friends saw her"], 2, "Impossible date",
  "A close-up of Raju's 'proof' ticket: dated 31 November.",
  "November has only 30 days. Raju's ticket is fake, so his alibi is fake.", 2,
  ["police_station"]),
 ("Pighalti Ice Cream", "The melting ice cream", "Dr. Ayesha",
  "Ayesha's bicycle is stolen from the park on a 40-degree afternoon.",
  ["Chacha Jamil: was reading the newspaper on the bench",
   "Zara: 'I've been sitting on this bench for an hour eating my ice cream'",
   "Faisal: was having lunch at the dhaba across the road"], 2, "Heat",
  "Zara's ice cream cone is still perfectly frozen, and the sky shows a blazing sun (40°C sign on a shop).",
  "In 40-degree heat an ice cream melts in minutes. Zara just bought it; she was not on the bench for an hour.", 2,
  ["town_park"]),
 ("Kichad Ke Nishaan", "Footprints in the mud", "Begum Nusrat",
  "Nusrat's rose-show trophy is taken from the garden after the rain.",
  ["Ustad Rafiq: was cooking lunch in the mansion kitchen",
   "Chacha Jamil: never left his chair on the veranda",
   "Raju Mistri: was painting the garden gate"], 2, "Footprints",
  "Muddy footprints lead to the trophy stand, with a small round dot beside every second step.",
  "The dots are from a walking stick. Only Jamil walks with a cane.", 2,
  ["garden", "mansion_living_room"]),
 ("Mobile Ki Gawahi", "The phone's witness", "Ustad Rafiq",
  "Cash disappears from Rafiq's restaurant kitchen at 2 pm.",
  ["Begum Nusrat: was at home in bed with fever all day, phone switched off",
   "Raju Mistri: was fixing a fridge at the bakery",
   "Faisal: was stuck in traffic on the highway"], 1, "Video evidence",
  "Zara's 2 pm food video shows, in the background, Nusrat walking past Rafiq's kitchen door.",
  "Zara's video proves Nusrat was at the restaurant at 2 pm, not at home in bed.", 3,
  ["kitchen", "bakery_shop"]),
 ("Naqli Sikka", "The fake coin", "Dr. Ayesha",
  "Three people sell 'ancient' items to Ayesha's museum. One is a fake.",
  ["Chacha Jamil: his grandfather's old pocket watch",
   "Faisal: a medal from his great-grandfather's army days",
   "Seth Kareem: a gold coin stamped '250 BC'"], 3, "Impossible inscription",
  "A close-up of the coin: '250 BC' is stamped on it.",
  "People living in 250 BC could not know they were 'before Christ'; that counting came centuries later. The coin is fake.", 3,
  ["museum_gallery", "kareem_shop"]),
 ("Mehndi Ka Nishaan", "The mehndi handprint", "Zara",
  "The envelope of wedding gifts (salami) vanishes at Zara's cousin's wedding.",
  ["Ustad Rafiq: was busy with the caterers all evening",
   "Raju Mistri: was fixing the stage lights",
   "Begum Nusrat: 'I arrived five minutes ago, straight from home'"], 3, "Physical trace",
  "An orange mehndi handprint on the gift box; the venue's mehndi stall is shown earlier. Nusrat's palm has fresh mehndi.",
  "Fresh mehndi comes from the stall at this wedding. Nusrat has been here much longer than five minutes.", 3,
  ["shaadi_hall"]),
 ("Sota Hua Musafir", "The sleeping passenger", "Begum Nusrat",
  "Nusrat's suitcase is swapped on the overnight train.",
  ["Raju Mistri: sat by the door all night, wide awake",
   "Faisal: was in the next carriage with his parcels",
   "Dr. Ayesha: 'I slept from the moment I boarded until we arrived. Lovely sunset over the river bridge, by the way.'"], 3,
  "Contradiction in own words",
  "Ayesha's own sentence: she slept the whole way, yet describes the sunset at the bridge.",
  "If she slept the whole journey, she could not have seen the sunset over the bridge.", 2,
  ["train_station"]),
 ("Chand Ki Gawahi", "The moon's witness", "Raju Mistri",
  "Raju's bicycle is stolen at night. Rafiq says he saw Faisal take it.",
  ["Ustad Rafiq: 'I saw Faisal clearly in the bright full moonlight!'",
   "Faisal: was asleep at home",
   "Zara: was studying for her exam"], 1, "Moon / calendar",
  "The wall calendar shows last night was amavas: a new moon, the darkest night of the month.",
  "On a new-moon night there is no moonlight. Rafiq could not have seen anyone 'clearly'; he is covering for himself.", 3,
  ["night_street", "small_bedroom"]),
 ("Haldi Wale Haath", "Turmeric hands", "Ustad Rafiq",
  "Someone pours salt into Rafiq's biryani before the cooking contest.",
  ["Zara: was filming the other contestants",
   "Seth Kareem: delivered spices in the morning and never came back",
   "Faisal: delivered the trophy and left"], 2, "Physical trace",
  "Yellow haldi fingerprints on the salt jar. Kareem sells haldi; his fingers are stained yellow.",
  "Only Kareem's hands are stained with haldi, and the fingerprints on the salt jar are haldi yellow.", 2,
  ["kitchen", "kareem_shop"]),
 ("Bell Kharab Hai", "The broken doorbell", "Chacha Jamil",
  "Jamil's parcel never arrives. Faisal says nobody answered the door.",
  ["Faisal: 'I rang the bell three times. Nobody answered, so I took the parcel back.'",
   "Raju Mistri: was fixing pipes on the roof",
   "Zara: was out at college"], 1, "Broken object",
  "A note on Jamil's door: 'Bell kharab hai, darwaza khatkhatayein' (the bell is broken, please knock).",
  "The bell has been broken for weeks. Faisal could not have 'rung it three times'; he never came to the door.", 1,
  ["apartment_hallway"]),
 ("Chhota Saya", "The short shadow", "Seth Kareem",
  "Kareem's shop is robbed at 5 pm.",
  ["Chacha Jamil: was asleep after lunch",
   "Ustad Rafiq: was cooking dinner for a party",
   "Raju Mistri: shows a selfie 'taken in the city at 5 pm'"], 3, "Shadows",
  "Raju's selfie: the sun is straight overhead and his shadow is tiny, right under his feet.",
  "A tiny shadow means midday, not 5 pm. The photo was taken at noon, so it proves nothing about 5 pm.", 4,
  ["kareem_shop", "gali_street"]),
 ("Ulta Akhbar", "The upside-down newspaper", "Begum Nusrat",
  "Nusrat's brooch disappears during her tea party.",
  ["Ustad Rafiq: 'I sat here reading the newspaper the whole time'",
   "Zara: was in the garden on her phone",
   "Dr. Ayesha: was looking at the paintings in the hall"], 1, "Visual giveaway",
  "Rafiq is holding the newspaper upside down.",
  "Nobody reads a newspaper upside down. Rafiq grabbed it just now to look busy.", 1,
  ["mansion_living_room", "garden"]),
 ("Mitti Ki Gullak", "The clay piggy bank", "Bunty",
  "Bunty's piggy bank (gullak) is smashed and empty.",
  ["Raju Mistri: was at the hardware shop",
   "Faisal: was delivering a parcel next door",
   "Zara: 'I don't know anything about a mango-shaped clay gullak!'"], 3, "Guilty knowledge",
  "Foxley only said 'gullak'. Nobody mentioned it was clay or shaped like a mango.",
  "Zara described the gullak exactly, so she had seen it. Only the thief had.", 3,
  ["gali_street", "apartment_hallway"]),
 ("Geela Rang", "Wet paint", "Dr. Ayesha",
  "A rare book disappears from the reading bench in the park.",
  ["Raju Mistri: was painting the park benches",
   "Seth Kareem: 'I never sat on that bench!'",
   "Chacha Jamil: was walking around the pond"], 2, "Physical trace",
  "The bench has a WET PAINT sign; Kareem's white trousers have green stripes across the back.",
  "Kareem says he never sat on the bench, but the fresh green paint on his trousers says he did.", 1,
  ["town_park"]),
 ("Khamosh Alarm", "The silent alarm", "Dr. Ayesha",
  "A painting is taken from the museum after closing time.",
  ["Faisal: 'I heard the alarm ringing loudly and ran in to help!'",
   "Sher Khan: was patrolling the back gate",
   "Raju Mistri: was fixing the air conditioning upstairs"], 1, "How things work",
  "Ayesha explains early on: the new alarm is silent. It only flashes a light in the police station.",
  "The alarm makes no sound. Faisal could not have heard it ringing; he was already inside.", 3,
  ["museum_gallery", "police_station"]),
 ("Barish Mein Match", "A match in the rain", "Chacha Jamil",
  "Jamil's gold watch disappears on the afternoon of the big match.",
  ["Bunty: 'I watched the whole match on TV. What a last over!'",
   "Begum Nusrat: was at a friend's house",
   "Faisal: was delivering in the next town"], 1, "News check",
  "Next morning's newspaper headline: 'Match cancelled due to rain, not a single ball bowled'.",
  "The match never happened, so there was no 'last over'. Bunty is lying about where he was.", 2,
  ["gali_street", "apartment_hallway"]),
 ("Ulte Haath Ki Siyahi", "Left-handed ink", "Ustad Rafiq",
  "A ransom-style note appears after Rafiq's secret recipe book goes missing.",
  ["Raju Mistri: was fixing the oven",
   "Dr. Ayesha: was writing notes at the next table",
   "Zara: was making a video in the dining room"], 2, "Left-handedness",
  "The note's ink is smudged left to right. Ayesha writes with her left hand, and her left palm edge is inky.",
  "Left-handed writers drag their hand through wet ink. The smudge and Ayesha's inky hand match.", 4,
  ["kitchen", "museum_gallery"]),
 ("Purani Wasiyat", "The old will", "Begum Nusrat",
  "A 'will' from 1995 turns up leaving Nusrat's house to someone else.",
  ["Chacha Jamil: found the will in an old trunk",
   "Seth Kareem: valued the trunk",
   "Raju Mistri: carried the trunk down from the attic"], 1, "Anachronism",
  "The will's envelope has a postage stamp printed in 2015.",
  "A letter from 1995 cannot carry a stamp printed in 2015. Jamil, who 'found' it, forged it.", 3,
  ["mansion_living_room"]),
 ("Unchi Almari", "The tall cupboard", "Ustad Rafiq",
  "Rafiq's saffron tin is taken from the very top shelf of his kitchen cupboard.",
  ["Zara: was helping serve tea",
   "Bunty: was playing cricket in the lane",
   "Raju Mistri: was fixing the window"], 3, "Height",
  "Rafiq mentions the stepladder has been locked in the store all day; the shelf is near the ceiling. Raju is by far the tallest.",
  "Without the ladder, Zara and Bunty cannot reach the top shelf. Only Raju is tall enough.", 3,
  ["kitchen"]),
 ("Thandi Istri", "The cold iron", "Begum Nusrat",
  "Nusrat's diamond earring goes missing from the laundry table.",
  ["Sher Khan: was guarding the gate",
   "Zara: was charging her phone in the hall",
   "Begum Nusrat: 'I've been ironing my sari for an hour'"], 3, "Temperature",
  "Foxley touches the iron: it is completely cold.",
  "An iron used for an hour would still be hot. Nusrat hid the earring herself (for the insurance).", 3,
  ["mansion_living_room"]),
 ("Lift Band Hai", "The lift is out of order", "Zara",
  "Zara's laptop disappears from the 10th floor of her building.",
  ["Sher Khan: 'I took the lift up to the 10th floor to check on things at 3 pm'",
   "Faisal: delivered to the ground floor",
   "Chacha Jamil: was at the barber getting a shave"], 1, "Closed / broken",
  "A sign on the lift: 'Under repair since morning'.",
  "The lift was not working all day. Sher Khan could not have taken it up; he is lying about where he was.", 2,
  ["apartment_lobby"]),
 ("Halka Suitcase", "The light suitcase", "Seth Kareem",
  "Kareem's antique vase is smuggled out of the station.",
  ["Dr. Ayesha: 'My suitcase is full of heavy books'",
   "Raju Mistri: carrying his toolbox",
   "Faisal: carrying parcels"], 1, "Physical giveaway",
  "Ayesha lifts her 'heavy' suitcase with one finger.",
  "A suitcase full of books would be very heavy. Hers is empty: the books were taken out to hide the vase elsewhere.", 2,
  ["train_station"]),
 ("Sheeshe Mein Aks", "Reflection in the glass", "Seth Kareem",
  "The mohalla cricket trophy vanishes from Kareem's shop window display.",
  ["Zara: was filming outside the shop",
   "Bunty: was at home doing homework",
   "Faisal: was delivering on another street"], 2, "Reflection",
  "Zara's video: in the shop window's reflection, a boy in a cricket cap reaches for the trophy.",
  "The reflection in Zara's video shows Bunty at the shop, not at home doing homework.", 4,
  ["kareem_shop", "gali_street"]),
 ("Chhote Joote", "Small shoes", "Ustad Rafiq",
  "Rafiq's prize mango basket is stolen from the garden.",
  ["Raju Mistri: was fixing the garden pipe",
   "Chacha Jamil: was resting indoors",
   "Zara: was out jogging"], 3, "Footprints",
  "Small sneaker prints by the basket, with a star pattern on the sole. Zara wears white sneakers.",
  "Raju wears big work boots and Jamil wears slippers. Only Zara's sneakers match the small star-soled prints.", 2,
  ["garden"]),
 ("Foxley Ka Imtihan", "Foxley's own case", "Foxley",
  "Season finale: Foxley's own magnifying glass is stolen from his study.",
  ["Begum Nusrat: was having tea at home",
   "Faisal: was delivering in the old city",
   "Seth Kareem: 'I was at the station meeting the 5 pm train from Lahore'"], 3, "Timetable",
  "The station board: the 5 pm train is cancelled on Sundays, and today is Sunday.",
  "There was no 5 pm train today, so Kareem was not at the station meeting it.", 4,
  ["foxley_study", "train_station"]),
]

NEEDS_CAST = [
 ("Sher Khan", "sherkhan", "Security guard / chowkidar at the museum and apartment building",
  "a tall, broad, serious security guard in his forties with a thick black moustache, a khaki guard uniform with a beret, a whistle on a cord and a wooden lathi stick",
  "standing at attention, saluting", "4, 20, 25, 26"),
 ("Bunty", "bunty", "Cricket-mad neighbourhood kid (about 10)",
  "a mischievous 10-year-old boy with spiky black hair and a gap in his front teeth, a cricket cap worn backwards, a green cricket jersey, shorts, sneakers, holding a cricket bat",
  "swinging the cricket bat with a big grin", "5, 18, 21, 28"),
 ("Seth Kareem", "kareem", "Shopkeeper: spices and antiques, sly and talkative",
  "a plump, sly middle-aged shopkeeper with a neat beard, neatly combed side-parted hair, a waistcoat over a kurta, a pen behind his ear and a small brass weighing scale",
  "rubbing his hands together with a sly smile", "10, 14, 16, 19, 23, 27, 30"),
]

NEEDS_SETS = [
 ("kitchen", "Planned in SETS.md", "3, 9, 14, 22, 24"),
 ("museum_gallery", "Planned in SETS.md", "4, 10, 20, 22"),
 ("police_station", "Planned in SETS.md", "6, 20"),
 ("town_park", "Planned in SETS.md", "7, 19"),
 ("bakery_shop", "Planned in SETS.md", "9"),
 ("apartment_hallway", "Planned in SETS.md", "2, 5, 15, 18, 21"),
 ("train_station", "Planned in SETS.md", "12, 27, 30"),
 ("night_street", "Planned in SETS.md", "4, 13"),
 ("gali_street", "NEW: a narrow desi mohalla lane with colourful houses, balconies, hanging wires, a small shop and an open area for gully cricket", "5, 16, 18, 21, 28"),
 ("shaadi_hall", "NEW: a decorated wedding hall with a flower-covered stage, fairy lights, round tables and a mehndi stall at the side", "11"),
 ("kareem_shop", "NEW: inside a cluttered spice-and-antique shop with jars of colourful spices, old clocks, brass items and a glass display window", "10, 14, 16, 28"),
 ("apartment_lobby", "NEW: an apartment building ground-floor lobby with a lift door that has a blank sign hanging on it, mailboxes and a guard's desk", "26"),
]

HEAD = ["#", "Title (Roman Urdu)", "Title (English)", "Victim", "The mystery (hook)",
        "Suspect 1 + alibi", "Suspect 2 + alibi", "Suspect 3 + alibi", "Culprit (line-up no.)", "Culprit",
        "Clue type", "The clue (shown in Part 1)", "Explanation (Part 2)", "Difficulty (1-5)",
        "Sets", "New art needed", "Status", "Script", "Voices", "Part 1 render", "Part 2 render",
        "Part 1 posted", "Part 2 posted", "Notes"]
WIDTH = [5, 24, 22, 15, 38, 40, 40, 40, 11, 15, 18, 45, 48, 10, 30, 24, 14, 9, 9, 10, 10, 13, 13, 30]
STATUS = ["Idea", "Script written", "Voices done", "Rendered", "Posted"]

F = "Arial"
thin = Side(style="thin", color="C9C9C9")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
HFILL = PatternFill("solid", fgColor="1F4E5F")
INPUT = PatternFill("solid", fgColor="FFF2CC")


def header(ws, row, cols):
    for c, h in enumerate(cols, 1):
        cell = ws.cell(row=row, column=c, value=h)
        cell.font = Font(name=F, bold=True, color="FFFFFF")
        cell.fill = HFILL
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = BORDER


def main():
    wb = Workbook()

    # ---------------- Episodes
    ws = wb.active
    ws.title = "Episodes"
    ws["A1"] = "Foxley Studio: 30 mysteries"
    ws["A1"].font = Font(name=F, bold=True, size=14, color="1F4E5F")
    ws["A2"] = ("Yellow columns are yours to fill in as you go (pick from the dropdowns or type a date). "
                "Every clue is shown or said in Part 1, so viewers can solve it fairly.")
    ws["A2"].font = Font(name=F, italic=True, color="555555")
    header(ws, 4, HEAD)
    for i, e in enumerate(EP, 1):
        t, te, victim, hook, sus, cn, ctype, clue, expl, diff, sets = e
        culprit = sus[cn - 1].split(":")[0]
        names = [s.split(":")[0] for s in sus]
        new = sorted({s for s in sets if s not in EXISTING_SETS} | {n for n in names if n in NEW_CAST})
        status = "Rendered" if i == 1 else "Idea"
        row = [i, t, te, victim, hook, *sus, cn, culprit, ctype, clue, expl, diff, ", ".join(sets),
               ", ".join(new) if new else "-", status, "Yes" if i == 1 else "No", "No",
               "Yes" if i == 1 else "No", "Yes" if i == 1 else "No", None, None,
               "Rendered with old voices; redo after voices are locked" if i == 1 else None]
        r = 4 + i
        for c, v in enumerate(row, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = Font(name=F, size=10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER
            if c >= 17:
                cell.fill = INPUT
        for c in (22, 23):
            ws.cell(row=r, column=c).number_format = "dd-mmm-yyyy"
    last = 4 + len(EP)
    for c, w in enumerate(WIDTH, 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.freeze_panes = "C5"
    ws.auto_filter.ref = f"A4:{get_column_letter(len(HEAD))}{last}"
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUS) + '"', allow_blank=True)
    yn = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    ws.add_data_validation(dv)
    ws.add_data_validation(yn)
    dv.add(f"Q5:Q{last}")
    yn.add(f"R5:U{last}")
    green = PatternFill("solid", fgColor="D9EAD3")
    ws.conditional_formatting.add(f"Q5:Q{last}", CellIsRule(operator="equal", formula=['"Posted"'], fill=green))
    ws["N4"].comment = Comment("1 = easy (spot it in one look), 5 = hard (needs careful listening).", "Foxley Studio")

    # ---------------- New art needed
    na = wb.create_sheet("New art needed")
    na["A1"] = "New characters"
    na["A1"].font = Font(name=F, bold=True, size=13, color="1F4E5F")
    header(na, 2, ["Character", "Folder id", "Role", "DESCRIPTION for the ChatGPT prompt (cast/CAST.md)",
                   "SIGNATURE POSE", "Episodes", "Art done?"])
    for i, row in enumerate(NEEDS_CAST, 3):
        for c, v in enumerate(list(row) + ["No"], 1):
            cell = na.cell(row=i, column=c, value=v)
            cell.font = Font(name=F, size=10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER
        na.cell(row=i, column=7).fill = INPUT
    r0 = 4 + len(NEEDS_CAST)
    na.cell(row=r0, column=1, value="Sets (backgrounds)").font = Font(name=F, bold=True, size=13, color="1F4E5F")
    header(na, r0 + 1, ["Set id", "Description / where it is described", "Episodes", "", "", "", "Art done?"])
    for i, (sid, desc, eps) in enumerate(NEEDS_SETS, r0 + 2):
        for c, v in {1: sid, 2: desc, 3: eps, 7: "No"}.items():
            cell = na.cell(row=i, column=c, value=v)
            cell.font = Font(name=F, size=10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER
        na.cell(row=i, column=7).fill = INPUT
    for c, w in enumerate([18, 70, 22, 70, 30, 22, 11], 1):
        na.column_dimensions[get_column_letter(c)].width = w
    yn2 = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    na.add_data_validation(yn2)
    yn2.add(f"G3:G{2 + len(NEEDS_CAST)}")
    yn2.add(f"G{r0 + 2}:G{r0 + 1 + len(NEEDS_SETS)}")

    # ---------------- Summary (formulas)
    sm = wb.create_sheet("Summary")
    sm["A1"] = "Progress"
    sm["A1"].font = Font(name=F, bold=True, size=13, color="1F4E5F")
    header(sm, 2, ["Status", "Episodes"])
    for i, s in enumerate(STATUS, 3):
        sm.cell(row=i, column=1, value=s).font = Font(name=F)
        sm.cell(row=i, column=2, value=f'=COUNTIF(Episodes!$Q$5:$Q${last},A{i})').font = Font(name=F)
    tr = 3 + len(STATUS)
    sm.cell(row=tr, column=1, value="Total").font = Font(name=F, bold=True)
    sm.cell(row=tr, column=2, value=f"=SUM(B3:B{tr-1})").font = Font(name=F, bold=True)
    sm.cell(row=tr + 1, column=1, value="Share posted").font = Font(name=F)
    c = sm.cell(row=tr + 1, column=2, value=f"=IFERROR(B{3+STATUS.index('Posted')}/B{tr},0)")
    c.font = Font(name=F)
    c.number_format = "0%"
    cr = tr + 3
    sm.cell(row=cr, column=1, value="Who is the culprit, how often (keeps it unpredictable)").font = Font(name=F, bold=True, size=13, color="1F4E5F")
    header(sm, cr + 1, ["Character", "Times culprit", "Times a suspect"])
    people = ["Ustad Rafiq", "Begum Nusrat", "Raju Mistri", "Zara", "Dr. Ayesha", "Chacha Jamil", "Faisal",
              "Sher Khan", "Bunty", "Seth Kareem"]
    for i, p in enumerate(people, cr + 2):
        sm.cell(row=i, column=1, value=p).font = Font(name=F)
        sm.cell(row=i, column=2, value=f'=COUNTIF(Episodes!$J$5:$J${last},A{i})').font = Font(name=F)
        sm.cell(row=i, column=3, value=(f'=COUNTIF(Episodes!$F$5:$F${last},A{i}&":*")+COUNTIF(Episodes!$G$5:$G${last},A{i}&":*")'
                                        f'+COUNTIF(Episodes!$H$5:$H${last},A{i}&":*")')).font = Font(name=F)
    sm.column_dimensions["A"].width = 30
    sm.column_dimensions["B"].width = 16
    sm.column_dimensions["C"].width = 16

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
