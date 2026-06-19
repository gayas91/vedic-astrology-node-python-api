from astro_constants import NAKSHATRAS, ZODIAC

# ----------------- Rajju -----------------
RAJJU_MAP = {
    "Ashwini": "Pada",
    "Bharani": "Kati",
    "Krittika": "Nabhi",
    "Rohini": "Kantha",
    "Mrigashira": "Pada",
    "Ardra": "Kati",
    "Punarvasu": "Nabhi",
    "Pushya": "Kantha",
    "Ashlesha": "Pada",
    "Magha": "Kati",
    "Purva Phalguni": "Nabhi",
    "Uttara Phalguni": "Kantha",
    "Hasta": "Pada",
    "Chitra": "Kati",
    "Swati": "Nabhi",
    "Vishakha": "Kantha",
    "Anuradha": "Pada",
    "Jyeshtha": "Kati",
    "Mula": "Nabhi",
    "Purva Ashadha": "Kantha",
    "Uttara Ashadha": "Pada",
    "Shravana": "Kati",
    "Dhanishta": "Nabhi",
    "Shatabhisha": "Kantha",
    "Purva Bhadrapada": "Pada",
    "Uttara Bhadrapada": "Kati",
    "Revati": "Nabhi"
}

def rajju_dosha(m_nak, f_nak):
    m = RAJJU_MAP.get(m_nak, "")
    f = RAJJU_MAP.get(f_nak, "")
    return "Yes" if (m and m == f) else "No"

# ----------------- Vedha -----------------
VEDHA_PAIRS = {
    ("Ashwini", "Jyeshtha"),
    ("Bharani", "Anuradha"),
    ("Krittika", "Vishakha"),
    ("Rohini", "Swati"),
    ("Mrigashira", "Chitra"),
    ("Ardra", "Hasta"),
    ("Punarvasu", "Magha"),
    ("Pushya", "Purva Phalguni"),
    ("Ashlesha", "Uttara Phalguni"),
    ("Mula", "Revati"),
    ("Purva Ashadha", "Uttara Bhadrapada"),
    ("Uttara Ashadha", "Purva Bhadrapada"),
}

def vedha_dosha(m_nak, f_nak):
    pair = (m_nak, f_nak)
    reverse = (f_nak, m_nak)
    return "Yes" if (pair in VEDHA_PAIRS or reverse in VEDHA_PAIRS) else "No"

# ----------------- helpers -----------------
def canon(s: str) -> str:
    return "".join(ch.lower() for ch in str(s or "") if ch.isalnum())

def sign_index(sign_name: str) -> int:
    c = canon(sign_name)
    for i, s in enumerate(ZODIAC):
        if canon(s) == c:
            return i
    return -1

def nak_index(nak_name: str) -> int:
    c = canon(nak_name)
    for i, n in enumerate(NAKSHATRAS):
        if canon(n) == c:
            return i
    return -1

# def row(title, description, m_attr, f_attr, total, got):
#     return {
#         "description": description,
#         "male_koot_attribute": m_attr,
#         "female_koot_attribute": f_attr,
#         "total_points": total,
#         "received_points": got,
#         "title": title
#     }

def row(title, description, m_attr, f_attr, total, got):
    detail_map = {
        "varna": "Varna reflects the mental compatibility between two individuals and plays a relatively minor role in overall marriage compatibility.",
        "vashya": "Vashya represents the degree of mutual influence and dominance between the bride and groom in a marriage.",
        "tara": "Tara indicates the compatibility of the birth stars of the bride and groom and also reflects the couple’s fortune.",
        "yoni": "Yoni represents the sexual and physical compatibility between the bride and groom.",
        "maitri": "Maitri evaluates the mental compatibility and emotional bond shared between the partners in a marriage.",
        "gan": "Gan reflects the behavior, nature, and temperament of the prospective bride and groom toward each other.",
        "bhakut": "Bhakut relates to the couple’s shared joys and challenges and evaluates their prosperity and well-being after marriage.",
        "nadi": "Nadi reflects the health compatibility between the couple and also plays an important role in matters related to childbirth and progeny."
    }

    return {
        "description": description,
        "detail_description": detail_map.get(title, ""),
        "male_koot_attribute": m_attr,
        "female_koot_attribute": f_attr,
        "total_points": total,
        "received_points": got,
        "title": title
    }

# ----------------- RULESET -----------------
# You can tune these to match the “other app”.

# 1) Varna
VARNA_MAP = {
    "Aries": "Kshatriya", "Leo": "Kshatriya", "Sagittarius": "Kshatriya",
    "Taurus": "Vaishya", "Virgo": "Vaishya", "Capricorn": "Vaishya",
    "Gemini": "Shudra", "Libra": "Shudra", "Aquarius": "Shudra",
    "Cancer": "Brahmin", "Scorpio": "Brahmin", "Pisces": "Brahmin",
}
VARNA_RANK = {"Shudra": 1, "Vaishya": 2, "Kshatriya": 3, "Brahmin": 4}

# 2) Vashya
VASHYA_MAP = {
    "Aries": "Chatuspad", "Taurus": "Chatuspad", "Capricorn": "Chatuspad",
    "Gemini": "Manav", "Virgo": "Manav", "Libra": "Manav", "Aquarius": "Manav",
    "Cancer": "Jalachar", "Pisces": "Jalachar",
    "Leo": "Vanachara", "Sagittarius": "Vanachara",
    "Scorpio": "Keet",
}

# Fractional scoring to allow 0.5 like your other app
# same => 2
# strong-compatible => 1
# weak-compatible => 0.5
VASHYA_STRONG = {
    ("Chatuspad", "Manav"), ("Manav", "Chatuspad"),
    ("Manav", "Vanachara"), ("Vanachara", "Manav"),
}
VASHYA_WEAK = {
    ("Jalachar", "Keet"), ("Keet", "Jalachar"),
}

# 3) Tara (0 / 1.5 / 3)
# Many apps give 1.5 for “madhyam” tara. We include it.
TARA_GOOD = {1, 3, 5, 7}
TARA_MED  = {2, 4, 6, 8}
# 0 when remainder==0 (9th)

# 4) Yoni mapping + enemy list (you can tune)
_YONI = {
    "Ashwini": "Horse",
    "Bharani": "Elephant",
    "Krittika": "Sheep",
    "Rohini": "Serpent",
    "Mrigashirsha": "Serpent",
    "Ardra": "Dog",
    "Punarvasu": "Cat",
    "Pushya": "Sheep",
    "Ashlesha": "Cat",
    "Magha": "Rat",
    "PurvaPhalguni": "Rat",
    "UttaraPhalguni": "Cow",
    "Hasta": "Buffalo",
    "Chitra": "Tiger",
    "Swati": "Buffalo",
    "Vishakha": "Tiger",
    "Anuradha": "Deer",
    "Jyeshtha": "Deer",
    "Mula": "Dog",
    "PurvaAshadha": "Monkey",
    "UttaraAshadha": "Mongoose",
    "Shravana": "Monkey",
    "Dhanishta": "Lion",
    "Shatabhisha": "Horse",
    "PurvaBhadrapada": "Lion",
    "UttaraBhadrapada": "Cow",
    "Revati": "Elephant",
}
NAK_YONI = {canon(k): v for k, v in _YONI.items()}

YONI_ENEMY = {
    ("Elephant", "Lion"), ("Lion", "Elephant"),
    ("Horse", "Buffalo"), ("Buffalo", "Horse"),
    ("Dog", "Deer"), ("Deer", "Dog"),
    ("Cat", "Rat"), ("Rat", "Cat"),
    ("Monkey", "Mongoose"), ("Mongoose", "Monkey"),
    ("Cow", "Tiger"), ("Tiger", "Cow"),
    ("Sheep", "Serpent"), ("Serpent", "Sheep"),
}

# 5) Sign lords + Maitri (0/1/3/4/5)
SIGN_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
ENEMIES = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Venus", "Mercury"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon"},
}

# 6) Gana
_GANA = {
    "Ashwini": "Deva",
    "Bharani": "Manushya",
    "Krittika": "Rakshasa",
    "Rohini": "Manushya",
    "Mrigashirsha": "Deva",
    "Ardra": "Manushya",
    "Punarvasu": "Deva",
    "Pushya": "Deva",
    "Ashlesha": "Rakshasa",
    "Magha": "Rakshasa",
    "PurvaPhalguni": "Manushya",
    "UttaraPhalguni": "Manushya",
    "Hasta": "Deva",
    "Chitra": "Rakshasa",
    "Swati": "Deva",
    "Vishakha": "Rakshasa",
    "Anuradha": "Deva",
    "Jyeshtha": "Rakshasa",
    "Mula": "Rakshasa",
    "PurvaAshadha": "Manushya",
    "UttaraAshadha": "Manushya",
    "Shravana": "Deva",
    "Dhanishta": "Rakshasa",
    "Shatabhisha": "Rakshasa",
    "PurvaBhadrapada": "Manushya",
    "UttaraBhadrapada": "Manushya",
    "Revati": "Deva",
}
NAK_GANA = {canon(k): v for k, v in _GANA.items()}

# 8) Nadi
_NADI = {
    "Ashwini": "Aadi", "Ardra": "Aadi", "Punarvasu": "Aadi", "UttaraPhalguni": "Aadi",
    "Hasta": "Aadi", "Jyeshtha": "Aadi", "Mula": "Aadi", "Shatabhisha": "Aadi", "PurvaBhadrapada": "Aadi",
    "Bharani": "Madhya", "Mrigashirsha": "Madhya", "Pushya": "Madhya", "PurvaPhalguni": "Madhya",
    "Chitra": "Madhya", "Anuradha": "Madhya", "PurvaAshadha": "Madhya", "Dhanishta": "Madhya", "UttaraBhadrapada": "Madhya",
    "Krittika": "Antya", "Rohini": "Antya", "Ashlesha": "Antya", "Magha": "Antya",
    "Swati": "Antya", "Vishakha": "Antya", "UttaraAshadha": "Antya", "Shravana": "Antya", "Revati": "Antya",
}
NAK_NADI = {canon(k): v for k, v in _NADI.items()}

# ----------------- getters -----------------
def varna_of_sign(sign):
    c = canon(sign)
    for k, v in VARNA_MAP.items():
        if canon(k) == c:
            return v
    return "Unknown"

def vashya_of_sign(sign):
    c = canon(sign)
    for k, v in VASHYA_MAP.items():
        if canon(k) == c:
            return v
    return "Unknown"

def yoni_of_nak(nak):
    return NAK_YONI.get(canon(nak), "Unknown")

def gana_of_nak(nak):
    return NAK_GANA.get(canon(nak), "Unknown")

def nadi_of_nak(nak):
    return NAK_NADI.get(canon(nak), "Unknown")

def sign_lord(sign):
    c = canon(sign)
    for k, v in SIGN_LORD.items():
        if canon(k) == c:
            return v
    return "Unknown"

# ----------------- scoring -----------------
def vashya_points(a, b):
    if a == "Unknown" or b == "Unknown":
        return 0
    if a == b:
        return 2
    if (a, b) in VASHYA_STRONG:
        return 1
    if (a, b) in VASHYA_WEAK:
        return 0.5
    return 0

def tara_points(m_nak, f_nak):
    mi = nak_index(m_nak)
    fi = nak_index(f_nak)
    if mi < 0 or fi < 0:
        return 0

    count = (fi - mi) % 27 + 1
    rem = count % 9
    if rem in TARA_GOOD:
        return 3
    if rem in TARA_MED:
        return 1.5
    return 0

def yoni_points(a, b):
    if a == "Unknown" or b == "Unknown":
        return 0
    if a == b:
        return 4
    if (a, b) in YONI_ENEMY:
        return 0
    # many apps use 2 for neutral
    return 2

def planet_relation(a, b):
    if a == "Unknown" or b == "Unknown":
        return "unknown"
    if b in FRIENDS.get(a, set()):
        return "friend"
    if b in ENEMIES.get(a, set()):
        return "enemy"
    return "neutral"

def maitri_points(a, b):
    ra = planet_relation(a, b)
    rb = planet_relation(b, a)

    if ra == "friend" and rb == "friend":
        return 5
    if ra == "enemy" and rb == "enemy":
        return 0
    if ("enemy" in (ra, rb)) and ("friend" in (ra, rb)):
        # some apps give 1 here (not 0)
        return 1
    if ra == "neutral" and rb == "neutral":
        return 3
    # friend+neutral
    return 4

def gana_points(a, b):
    if a == "Unknown" or b == "Unknown":
        return 0
    if a == b:
        return 6
    pair = {a, b}
    if pair == {"Deva", "Manushya"}:
        return 5
    if pair == {"Manushya", "Rakshasa"}:
        return 1
    if pair == {"Deva", "Rakshasa"}:
        # some apps give 1 instead of 0; adjust if needed
        return 0
    return 3

def bhakut_points(m_sign, f_sign):
    mi = sign_index(m_sign)
    fi = sign_index(f_sign)
    if mi < 0 or fi < 0:
        return 0

    dist = (fi - mi) % 12 + 1
    # classic dosha distances
    if dist in (2, 12, 5, 9, 6, 8):
        return 0
    return 7

def varna_points(m_varna, f_varna):
    vm = VARNA_RANK.get(m_varna, 0)
    vf = VARNA_RANK.get(f_varna, 0)
    return 1 if (vm >= vf and vm > 0 and vf > 0) else 0

def nadi_points(m_nadi, f_nadi):
    if m_nadi == "Unknown" or f_nadi == "Unknown":
        return 0
    return 0 if m_nadi == f_nadi else 8

# ----------------- main -----------------
def compute_ashtakoot(m, f, lang="en", include_debug=False):
    m_sign = m["moon_sign"]
    f_sign = f["moon_sign"]
    m_nak = m["nak_name"]
    f_nak = f["nak_name"]

    rajju = rajju_dosha(m_nak, f_nak)
    vedha = vedha_dosha(m_nak, f_nak)

    debug = {}

    # attributes
    varna_m = varna_of_sign(m_sign)
    varna_f = varna_of_sign(f_sign)

    vashya_m = vashya_of_sign(m_sign)
    vashya_f = vashya_of_sign(f_sign)

    yoni_m = yoni_of_nak(m_nak)
    yoni_f = yoni_of_nak(f_nak)

    maitri_m = sign_lord(m_sign)
    maitri_f = sign_lord(f_sign)

    gana_m = gana_of_nak(m_nak)
    gana_f = gana_of_nak(f_nak)

    nadi_m = nadi_of_nak(m_nak)
    nadi_f = nadi_of_nak(f_nak)

    # points
    p_varna = varna_points(varna_m, varna_f)
    p_vashya = vashya_points(vashya_m, vashya_f)
    p_tara = tara_points(m_nak, f_nak)
    p_yoni = yoni_points(yoni_m, yoni_f)
    p_maitri = maitri_points(maitri_m, maitri_f)
    p_gana = gana_points(gana_m, gana_f)
    p_bhakut = bhakut_points(m_sign, f_sign)
    p_nadi = nadi_points(nadi_m, nadi_f)

    points = [
        row("varna", "Natural Refinement  / Work", varna_m, varna_f, 1, p_varna),
        row("vashya", "Innate Giving / Attraction  towards each other", vashya_m, vashya_f, 2, p_vashya),
        row("tara", "Comfort - Prosperity - Health", m_nak, f_nak, 3, p_tara),
        row("yoni", "Intimate Physical", yoni_m, yoni_f, 4, p_yoni),
        row("maitri", "Friendship", maitri_m, maitri_f, 5, p_maitri),
        row("gan", "Temperament", gana_m, gana_f, 6, p_gana),
        row("bhakut", "Constructive Ability / Constructivism / Society and Couple", m_sign, f_sign, 7, p_bhakut),
        row("nadi", "Progeny / Excess", nadi_m, nadi_f, 8, p_nadi),
    ]

    total_received = sum(x["received_points"] for x in points)
    total_points = 36
    minimum_required = 18

    points.append({
        "total_points": total_points,
        "received_points": total_received,
        "minimum_required": minimum_required,
        "title": "total"
    })

    status = total_received >= minimum_required
    report = (
        f"The match has scored {total_received} points outs of {total_points} points. "
        + ("This is a reasonably good score. Hence, this is a favourable Ashtakoota match."
           if status else
           "This score is below recommended minimum. Hence, this is not a favourable Ashtakoota match.")
    )

    points.append({"status": status, "report": report, "title": "conclusion"})

    if include_debug:
        mi = sign_index(m_sign)
        fi = sign_index(f_sign)
        dist = (fi - mi) % 12 + 1 if mi >= 0 and fi >= 0 else None
        debug = {
            "male_moon_sign": m_sign,
            "female_moon_sign": f_sign,
            "male_nak": m_nak,
            "female_nak": f_nak,
            "bhakut_distance": dist,
            "varna": (varna_m, varna_f),
            "vashya": (vashya_m, vashya_f),
            "yoni": (yoni_m, yoni_f),
            "maitri": (maitri_m, maitri_f),
            "gana": (gana_m, gana_f),
            "nadi": (nadi_m, nadi_f),
        }
    return {
        "points": points,
        "rajju_dosha": rajju,
        "vedha_dosha": vedha
    }, debug
    
    # return points, debug
