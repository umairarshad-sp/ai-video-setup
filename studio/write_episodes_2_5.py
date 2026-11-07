"""Write the bilingual story scripts for episodes 2-5 (Part 1 and Part 2 each).

    python3 studio/write_episodes_2_5.py

Every line has three texts: "say" (Devanagari, spoken in the Urdu/Hindi version), "caption"
(Roman Urdu/Hindi, shown in that version) and "en" (spoken and shown in the English version).
On-screen texts are {"ur": ..., "en": ...}.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ln(who, en, roman, deva, **kw):
    return {"who": who, "en": en, "caption": roman, "say": deva, **kw}


def fox_bilal(set_id, lines, dark=0):
    sh = {"set": set_id, "cast": [{"id": "foxley", "x": 0.3, "face": "right"}, {"id": "bilal", "x": 0.74}],
          "camera": {"from": {"focus": "group", "zoom": 1.25}, "to": {"focus": "group", "zoom": 1.32}},
          "sfx": [["pop", 0.05]], "transition": "whoosh", "lines": lines}
    if dark:
        sh["dark"] = dark
    return sh


def alibi(set_id, who, line, x=0.5, dark=0, rain=False, prop=None, zoom_to=1.2, caption_y=None):
    c = {"id": who, "x": x}
    if prop:
        c["prop"] = prop
    sh = {"set": set_id, "transition": "whoosh", "cast": [c],
          "camera": {"from": {"focus": [0.5, 0.6], "zoom": 1.0}, "to": {"focus": who, "zoom": zoom_to}},
          "lines": [line], "hold": 0.3}
    if dark:
        sh["dark"] = dark
    if rain:
        sh["rain"] = True
    if caption_y:
        sh["caption_y"] = caption_y
    return sh


def lineup(set_id, ids, line, dark=0, props=None, title=None, part=1):
    xs = [0.2, 0.5, 0.8]
    sh = {"set": set_id, "transition": "whoosh",
          "cast": [dict({"id": i, "x": x}, **({"prop": props[i]} if props and i in props else {})) for i, x in zip(ids, xs)],
          "lineup": ids, "lines": [line]}
    if part == 1:
        sh.update({"camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.06}},
                   "sfx": [["riser", 0.0]], "timer": 5, "cta": {"after_timer": True, "y": 430}, "hold": 2.2})
    else:
        sh.pop("transition")
        sh.update({"camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.12}, "to": {"focus": [0.5, 0.62], "zoom": 1.0}},
                   "title": title, "sfx": [["sting", 0.0]], "hold": 0.3})
    if dark:
        sh["dark"] = dark
    return sh


LETS_CHECK = ln("foxley", "Let's check the alibis, detectives.", "Chalo jasooso, sab ki kahani jaanchte hain.",
                "चलो जासूसो, सब की कहानी जाँचते हैं।")


def reveal(set_id, culprit, l1, l2, answer, dark=0, prop=None, caption_y=None):
    c = {"id": culprit, "x": 0.62, "pose": "nervous"}
    if prop:
        c["prop"] = prop
    sh = {"set": set_id, "transition": "whoosh",
          "cast": [{"id": "foxley", "x": 0.25, "face": "right", "pose": "thinking"}, c],
          "camera": {"from": {"focus": "group", "zoom": 1.2}, "to": {"focus": culprit, "zoom": 1.6}, "ease": "power2.inOut"},
          "answer": {"text": answer, "at": 3.0, "y": 210}, "lines": [dict(l1, pose="thinking"), dict(l2, sfx_before="reveal", pose="examine")],
          "caption_y": caption_y or 1500, "hold": 0.4}
    if dark:
        sh["dark"] = dark
    return sh


def guilty(set_id, culprit, fox_line, culprit_line, dark=0, prop=None):
    c = {"id": culprit, "x": 0.72, "pose": "nervous"}
    if prop:
        c["prop"] = prop
    sh = {"set": set_id, "transition": "whoosh", "cast": [{"id": "foxley", "x": 0.28, "face": "right", "pose": "point"}, c],
          "camera": {"from": {"focus": "group", "zoom": 1.22}, "to": {"focus": "group", "zoom": 1.3}},
          "stamp": {"text": {"ur": "MUJRIM!", "en": "GUILTY!"}, "on": culprit, "line": 1},
          "lines": [dict(fox_line, pose="point"), dict(culprit_line, pose="guilty")], "hold": 0.6}
    if dark:
        sh["dark"] = dark
    return sh


def ending(set_id):
    return [
        {"set": set_id, "cast": [{"id": "foxley", "x": 0.3, "face": "right"}, {"id": "bilal", "x": 0.74}],
         "camera": {"from": {"focus": "group", "zoom": 1.25}, "to": {"focus": "group", "zoom": 1.3}},
         "stamp": {"text": "CASE CLOSED!", "on": "foxley", "line": 1},
         "lines": [ln("bilal", "I knew it! I always knew it!", "Mujhe pata tha! Mujhe hamesha se pata tha!",
                      "मुझे पता था! मुझे हमेशा से पता था!", pose="signature_point", sfx_after="boing"),
                   ln("foxley", "Case closed!", "Case closed!", "केस क्लोज़्ड!", pose="signature_thumbs_wink")],
         "hold": 0.5},
        {"set": set_id, "cast": [{"id": "foxley", "x": 0.5, "face": "right"}],
         "camera": {"from": {"focus": [0.5, 0.66], "zoom": 1.12}, "to": {"focus": [0.5, 0.66], "zoom": 1.18}},
         "cta": {"at": 0.2, "y": 560}, "caption_y": 230,
         "lines": [ln("foxley", "Follow for tomorrow's case. Stay sharp, detectives!",
                      "Kal ke naye case ke liye follow karein. Hoshiyar rahiye, jasooso!",
                      "कल के नए केस के लिए फ़ॉलो करें। होशियार रहिए, जासूसो!", after="signature_thumbs_wink")],
         "hold": 1.5},
    ]


def episode(n, part, title, shots, note=None):
    e = {"number": n, "part": part, "title": title, "handle": "@AskFoxley",
         "language": "bilingual: say = Devanagari (ur version voice), caption = Roman Urdu (ur captions), en = English",
         "music": {"bpm": 92, "gain": 0.5}, "shots": shots}
    if note:
        e["answer_note"] = note
    json.dump(e, open(os.path.join(ROOT, "episodes", f"s{n:03d}_part{part}.json"), "w"), indent=2, ensure_ascii=False)


# ============================================================ Episode 2: Andhere Ka Cricket
T2 = {"ur": "HAAR KIS NE CHURAYA?", "en": "WHO TOOK THE NECKLACE?"}
S2 = ["raju", "zara", "jamil"]
episode(2, 1, T2, [
    {"set": "mansion_living_room", "dark": 0.7, "cast": [{"id": "nusrat", "x": 0.5, "pose": "shocked"}],
     "camera": {"from": {"focus": [0.5, 0.4], "zoom": 1.6}, "to": {"focus": [0.5, 0.62], "zoom": 1.12}, "dur": 1.8, "ease": "power2.out"},
     "title": T2, "title_dur": 3.2, "sfx": [["sting", 0.0]],
     "lines": [ln("nusrat", "My pearl necklace! Someone took it in the dark!", "Mera motiyon ka haar! Andhere mein kisi ne utha liya!",
                  "मेरा मोतियों का हार! अंधेरे में किसी ने उठा लिया!", pose="shocked", after="signature_faint")], "hold": 0.6},
    fox_bilal("mansion_living_room", [
        ln("foxley", "Two hours of load-shedding, no electricity on the whole street. Someone used the dark.",
           "Do ghante ki load-shedding, poori gali mein bijli nahi thi. Kisi ne andhere ka faida uthaya.",
           "दो घंटे की लोड शेडिंग, पूरी गली में बिजली नहीं थी। किसी ने अंधेरे का फ़ायदा उठाया।"),
        ln("bilal", "Then it was the generator! Generators are always suspicious!",
           "Phir to generator ne kiya! Generator hamesha mashkook hota hai!",
           "फिर तो जनरेटर ने किया! जनरेटर हमेशा मशकूक होता है!", pose="signature_point", sfx_after="boing"),
        ln("foxley", "Generators don't steal, Bilal.", "Generator chori nahi karte, Bilal.", "जनरेटर चोरी नहीं करते, बिलाल।", after="thinking"),
    ], dark=0.62),
    alibi("night_street", "raju", ln("raju", "I was outside the whole time, trying to start the generator!",
          "Main poora waqt bahar generator chalane ki koshish kar raha tha!",
          "मैं पूरा वक़्त बाहर जनरेटर चलाने की कोशिश कर रहा था!", after="signature_wrench"), x=0.35, dark=0.45),
    alibi("apartment_hallway", "zara", ln("zara", "I was sitting in the dark, talking to my friend on the phone.",
          "Main andhere mein baith ke apni dost se phone pe baat kar rahi thi.",
          "मैं अंधेरे में बैठ के अपनी दोस्त से फ़ोन पे बात कर रही थी।", after="signature_filming"), dark=0.68),
    alibi("small_bedroom", "jamil", ln("jamil", "I watched the cricket match on TV all evening. What a last over!",
          "Main saari shaam TV pe cricket match dekh raha tha. Kya aakhri over tha!",
          "मैं सारी शाम टीवी पे क्रिकेट मैच देख रहा था। क्या आख़िरी ओवर था!", after="signature_cane_shake"), dark=0.68),
    lineup("mansion_living_room", S2, ln("foxley", "One of them is lying. Who took the necklace?",
           "Inn mein se ek jhoot bol raha hai. Haar kis ne churaya?", "इनमें से एक झूठ बोल रहा है। हार किस ने चुराया?"), dark=0.5),
], note="Chacha Jamil (3) is lying: there was no electricity during the load-shedding, so his TV could not have been on.")
episode(2, 2, T2, [
    lineup("mansion_living_room", S2, LETS_CHECK, dark=0.35, title=T2, part=2),
    reveal("small_bedroom", "jamil",
           ln("foxley", "Chacha Jamil says he watched cricket on TV all evening.",
              "Chacha Jamil kehte hain woh saari shaam TV pe cricket dekh rahe the.",
              "चाचा जमील कहते हैं वो सारी शाम टीवी पे क्रिकेट देख रहे थे।"),
           ln("foxley", "But there was no electricity! The TV could not have been on.",
              "Lekin bijli thi hi nahi! TV chal hi nahi sakta tha.", "लेकिन बिजली थी ही नहीं! टीवी चल ही नहीं सकता था।"),
           {"ur": "Bijli nahi thi, to TV kaise chala?", "en": "No power, so no TV!"}, dark=0.62),
    guilty("mansion_living_room", "jamil",
           ln("foxley", "You were never watching cricket, Chacha!", "Aap cricket dekh hi nahi rahe the, Chacha!",
              "आप क्रिकेट देख ही नहीं रहे थे, चाचा!"),
           ln("jamil", "Arey... I only wanted to check if the pearls were real!",
              "Arey... main to bas dekhna chahta tha ke moti asli hain ya nahi!",
              "अरे... मैं तो बस देखना चाहता था के मोती असली हैं या नहीं!"), dark=0.2),
    *ending("mansion_living_room"),
])

# ============================================================ Episode 3: Kheer Kis Ne Khayi?
T3 = {"ur": "KHEER KIS NE KHAYI?", "en": "WHO ATE THE KHEER?"}
S3 = ["zara", "faisal", "raju"]
episode(3, 1, T3, [
    {"set": "kitchen", "cast": [{"id": "rafiq", "x": 0.55, "pose": "shocked"}],
     "camera": {"from": {"focus": [0.2, 0.4], "zoom": 1.6}, "to": {"focus": [0.5, 0.62], "zoom": 1.12}, "dur": 1.8, "ease": "power2.out"},
     "title": T3, "title_dur": 3.2, "sfx": [["sting", 0.0]],
     "lines": [ln("rafiq", "My Eid kheer! The whole pot is empty!", "Meri Eid ki kheer! Poori degchi khaali hai!",
                  "मेरी ईद की खीर! पूरी देगची ख़ाली है!", pose="shocked")], "hold": 0.6},
    fox_bilal("kitchen", [
        ln("foxley", "A whole pot of kheer, gone in ten minutes. Someone has a sweet tooth.",
           "Dus minute mein poori kheer gayab. Kisi ko meetha bohot pasand hai.",
           "दस मिनट में पूरी खीर ग़ायब। किसी को मीठा बहुत पसंद है।"),
        ln("bilal", "Arrest the ants! Ants love sweets!", "Cheentiyon ko giraftaar karo! Cheentiyan meetha khaati hain!",
           "चींटियों को गिरफ़्तार करो! चींटियाँ मीठा खाती हैं!", pose="signature_point", sfx_after="boing"),
        ln("foxley", "Ants don't eat a whole pot, Bilal.", "Cheentiyan poori degchi nahi khaati, Bilal.",
           "चींटियाँ पूरी देगची नहीं खातीं, बिलाल।", after="thinking"),
    ]),
    alibi("garden", "zara", ln("zara", "I was in the garden taking photos. I didn't even go inside.",
          "Main baagh mein photos le rahi thi. Andar gayi hi nahi.", "मैं बाग़ में फ़ोटोज़ ले रही थी। अंदर गई ही नहीं।",
          after="signature_filming")),
    alibi("gali_street", "faisal", ln("faisal", "I just arrived with a parcel. I never went near the kitchen!",
          "Main to abhi parcel le ke aaya hoon. Kitchen ke paas bhi nahi gaya!",
          "मैं तो अभी पार्सल ले के आया हूँ। किचन के पास भी नहीं गया!"), prop="kheer", zoom_to=1.5),
    alibi("apartment_hallway", "raju", ln("raju", "I was upstairs, fixing the tap in the bathroom.",
          "Main upar bathroom mein nal theek kar raha tha.", "मैं ऊपर बाथरूम में नल ठीक कर रहा था।", after="signature_wrench")),
    lineup("kitchen", S3, ln("foxley", "Look closely. Who ate the kheer?", "Ghaur se dekhiye. Kheer kis ne khayi?",
           "ग़ौर से देखिए। खीर किस ने खाई?"), props={"faisal": "kheer"}),
], note="Faisal (2) is lying: he says he never went near the kitchen, but there is fresh kheer on his moustache.")
episode(3, 2, T3, [
    lineup("kitchen", S3, LETS_CHECK, props={"faisal": "kheer"}, title=T3, part=2),
    reveal("gali_street", "faisal",
           ln("foxley", "Faisal says he never went near the kitchen.", "Faisal kehta hai woh kitchen ke paas bhi nahi gaya.",
              "फ़ैसल कहता है वो किचन के पास भी नहीं गया।"),
           ln("foxley", "Then why is there fresh kheer on his moustache?", "To phir uski moonchh pe taaza kheer kyun lagi hai?",
              "तो फिर उसकी मूँछ पे ताज़ा खीर क्यों लगी है?"),
           {"ur": "Moonchh pe taaza kheer!", "en": "Fresh kheer on his moustache!"}, prop="kheer"),
    guilty("kitchen", "faisal",
           ln("foxley", "You ate it, Faisal!", "Kheer tumne khayi, Faisal!", "खीर तुमने खाई, फ़ैसल!"),
           ln("faisal", "It smelled so good... just one spoon. Okay, fifty spoons.",
              "Itni achhi khushboo thi... bas ek chammach. Achha, pachaas chammach.",
              "इतनी अच्छी ख़ुशबू थी... बस एक चम्मच। अच्छा, पचास चम्मच।"), prop="kheer"),
    *ending("kitchen"),
])

# ============================================================ Episode 4: Barish Wali Raat
T4 = {"ur": "HEERA KIS NE CHURAYA?", "en": "WHO STOLE THE DIAMOND?"}
S4 = ["ayesha", "raju", "sherkhan"]
episode(4, 1, T4, [
    {"set": "museum_gallery", "cast": [{"id": "ayesha", "x": 0.55, "pose": "shocked"}],
     "camera": {"from": {"focus": [0.12, 0.43], "zoom": 1.8}, "to": {"focus": [0.5, 0.62], "zoom": 1.12}, "dur": 1.8, "ease": "power2.out"},
     "title": T4, "title_dur": 3.2, "sfx": [["sting", 0.0]],
     "lines": [ln("ayesha", "The museum's diamond is gone! The display case is empty!",
                  "Museum ka heera gayab hai! Display case khaali hai!", "म्यूज़ियम का हीरा ग़ायब है! डिस्प्ले केस ख़ाली है!",
                  pose="shocked")], "hold": 0.6},
    dict(fox_bilal("night_street", [
        ln("foxley", "Last night it poured, all night long. Not one dry inch on this street.",
           "Kal saari raat moosladhaar barish hui. Is gali mein ek inch bhi sookha nahi bacha.",
           "कल सारी रात मूसलाधार बारिश हुई। इस गली में एक इंच भी सूखा नहीं बचा।"),
        ln("bilal", "Maybe the rain took it! Rain gets in everywhere!", "Shayad barish ne churaya! Barish har jagah ghus jaati hai!",
           "शायद बारिश ने चुराया! बारिश हर जगह घुस जाती है!", pose="signature_point", sfx_after="boing"),
        ln("foxley", "Rain doesn't steal diamonds, Bilal.", "Barish heere nahi churati, Bilal.", "बारिश हीरे नहीं चुराती, बिलाल।",
           after="thinking"),
    ]), rain=True),
    alibi("museum_gallery", "ayesha", ln("ayesha", "I locked my office and left at six o'clock.",
          "Main ne apna daftar band kiya aur chhe baje chali gayi.", "मैंने अपना दफ़्तर बंद किया और छह बजे चली गई।",
          after="signature_glasses_push")),
    alibi("museum_gallery", "raju", ln("raju", "I was inside, fixing the gallery lights till midnight.",
          "Main aadhi raat tak andar gallery ki lights theek kar raha tha.", "मैं आधी रात तक अंदर गैलरी की लाइट्स ठीक कर रहा था।",
          after="signature_wrench"), x=0.4),
    alibi("museum_gallery", "sherkhan", ln("sherkhan", "I stood at the open front gate all night. Not even a bird got past me!",
          "Main saari raat khule gate pe khara raha. Ek parinda bhi nahi guzra!", "मैं सारी रात खुले गेट पे खड़ा रहा। एक परिंदा भी नहीं गुज़रा!",
          after="signature_salute"), zoom_to=1.35),
    lineup("museum_gallery", S4, ln("foxley", "One of them is lying. Who stole the diamond?",
           "Inn mein se ek jhoot bol raha hai. Heera kis ne churaya?", "इनमें से एक झूठ बोल रहा है। हीरा किस ने चुराया?")),
], note="Sher Khan (3) is lying: it rained heavily all night, yet his uniform, cap and boots are completely dry.")
episode(4, 2, T4, [
    lineup("museum_gallery", S4, LETS_CHECK, title=T4, part=2),
    reveal("museum_gallery", "sherkhan",
           ln("foxley", "Sher Khan stood at an open gate all night, in pouring rain.",
              "Sher Khan saari raat khule gate pe khara raha, moosladhaar barish mein.",
              "शेर ख़ान सारी रात खुले गेट पे खड़ा रहा, मूसलाधार बारिश में।"),
           ln("foxley", "But his uniform, his cap and his boots are completely dry!",
              "Lekin uski wardi, topi aur joote bilkul sookhe hain!", "लेकिन उसकी वर्दी, टोपी और जूते बिल्कुल सूखे हैं!"),
           {"ur": "Barish ke baad bhi bilkul sookha?", "en": "Bone dry after a night of rain?"}),
    guilty("museum_gallery", "sherkhan",
           ln("foxley", "You were inside all night, Sher Khan!", "Aap saari raat andar the, Sher Khan!", "आप सारी रात अंदर थे, शेर ख़ान!"),
           ln("sherkhan", "It was raining... I only went in to stay dry. And the diamond was so shiny.",
              "Barish ho rahi thi... main bas sookhne andar gaya. Aur heera itna chamak raha tha.",
              "बारिश हो रही थी... मैं बस सूखने अंदर गया। और हीरा इतना चमक रहा था।")),
    *ending("museum_gallery"),
])

# ============================================================ Episode 5: Toota Sheesha
T5 = {"ur": "SHEESHA KIS NE TODA?", "en": "WHO BROKE THE WINDOW?"}
S5 = ["bunty", "zara", "faisal"]
episode(5, 1, T5, [
    {"set": "apartment_hallway", "cast": [{"id": "jamil", "x": 0.5, "pose": "shocked"}],
     "camera": {"from": {"focus": [0.5, 0.25], "zoom": 1.7}, "to": {"focus": [0.5, 0.62], "zoom": 1.12}, "dur": 1.8, "ease": "power2.out"},
     "title": T5, "title_dur": 3.2, "sfx": [["sting", 0.0]],
     "lines": [ln("jamil", "Someone smashed my window with a cricket ball! And the ball is gone!",
                  "Kisi ne cricket ball se meri khirki tor di! Aur ball bhi gayab hai!",
                  "किसी ने क्रिकेट बॉल से मेरी खिड़की तोड़ दी! और बॉल भी ग़ायब है!", pose="shocked", after="signature_cane_shake")],
     "hold": 0.6},
    fox_bilal("gali_street", [
        ln("foxley", "A broken window, and nobody knows where the ball went.",
           "Toota sheesha, aur kisi ko nahi pata ball kahan gayi.", "टूटा शीशा, और किसी को नहीं पता बॉल कहाँ गई।"),
        ln("bilal", "Simple! The window was old, it broke by itself!", "Seedhi baat! Khirki purani thi, khud hi toot gayi!",
           "सीधी बात! खिड़की पुरानी थी, ख़ुद ही टूट गई!", pose="signature_point", sfx_after="boing"),
        ln("foxley", "Windows don't throw cricket balls, Bilal.", "Khirkiyan cricket ball nahi phainkti, Bilal.",
           "खिड़कियाँ क्रिकेट बॉल नहीं फेंकतीं, बिलाल।", after="thinking"),
    ]),
    alibi("gali_street", "bunty", ln("bunty", "I didn't even see the window! And anyway, the ball must have rolled under the sofa.",
          "Main ne to khirki dekhi bhi nahi! Aur waise bhi, ball sofa ke neeche gayi hogi.",
          "मैंने तो खिड़की देखी भी नहीं! और वैसे भी, बॉल सोफ़े के नीचे गई होगी।")),
    alibi("gali_street", "zara", ln("zara", "I was on the rooftop, recording a dance video.",
          "Main chhat pe dance video bana rahi thi.", "मैं छत पे डांस वीडियो बना रही थी।", after="signature_filming"), x=0.55),
    alibi("gali_street", "faisal", ln("faisal", "I was delivering parcels on the next street.",
          "Main agli gali mein parcel de raha tha.", "मैं अगली गली में पार्सल दे रहा था।", after="signature_running"), x=0.4),
    lineup("gali_street", S5, ln("foxley", "One of them just gave it away. Who broke the window?",
           "Inn mein se ek ne khud hi raaz khol diya. Sheesha kis ne toda?", "इनमें से एक ने ख़ुद ही राज़ खोल दिया। शीशा किस ने तोड़ा?")),
], note="Bunty (1) gave himself away: nobody had said where the ball landed, yet he knew it rolled under the sofa.")
episode(5, 2, T5, [
    lineup("gali_street", S5, LETS_CHECK, title=T5, part=2),
    reveal("gali_street", "bunty",
           ln("foxley", "Nobody told Bunty where the ball landed.", "Kisi ne Bunty ko nahi bataya tha ke ball kahan giri.",
              "किसी ने बंटी को नहीं बताया था के बॉल कहाँ गिरी।"),
           ln("foxley", "So how did he know it rolled under the sofa?", "To use kaise pata ke ball sofa ke neeche gayi?",
              "तो उसे कैसे पता के बॉल सोफ़े के नीचे गई?"),
           {"ur": "Ball kahan gayi, sirf use pata tha!", "en": "Only the batter knew where the ball went!"}),
    guilty("gali_street", "bunty",
           ln("foxley", "You hit that six, Bunty!", "Woh chakka tumne maara tha, Bunty!", "वो छक्का तुमने मारा था, बंटी!"),
           ln("bunty", "It was the best shot of my life! ...Sorry, Chacha.", "Meri zindagi ka sabse behtareen shot tha! ...Sorry, Chacha.",
              "मेरी ज़िंदगी का सबसे बेहतरीन शॉट था! ...सॉरी, चाचा।")),
    *ending("gali_street"),
])

print("wrote episodes s002-s005, parts 1 and 2")
