import sys, json
import swisseph as swe
import pytz
from datetime import datetime

# Lahiri ayanamsha
swe.set_sid_mode(swe.SIDM_LAHIRI)

ZODIAC = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

NAKSHATRAS = [
 "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
 "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
 "Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
 "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
 "Uttara Bhadrapada","Revati"
]

YOGAS = [
 "Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda",
 "Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva",
 "Vyaghata","Harshana","Vajra","Siddhi","Vyatipata","Variyana",
 "Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla",
 "Brahma","Indra","Vaidhriti"
]

TITHI_BASE = [
 "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami",
 "Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi",
 "Purnima"
]

PLANET_SHORT = {
    "SUN": "Su ",
    "MOON": "Mo ",
    "MARS": "Ma ",
    "MERCURY": "Me ",
    "JUPITER": "Ju ",
    "VENUS": "Ve ",
    "SATURN": "Sa ",
    "RAHU": "Ra ",
    "KETU": "Ke "
}

PLANETS_D1 = [
    ("SUN", swe.SUN),
    ("MOON", swe.MOON),
    ("MARS", swe.MARS),
    ("MERCURY", swe.MERCURY),
    ("JUPITER", swe.JUPITER),
    ("VENUS", swe.VENUS),
    ("SATURN", swe.SATURN),
    ("RAHU", swe.MEAN_NODE)  # KETU derived
]

# Planet short names + sign lords (same as your Node constants)
SIGN_LORD = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter"
}

PLANET_SHORT = {
    "Sun": "Su ",
    "Moon": "Mo ",
    "Mars": "Ma ",
    "Mercury": "Me ",
    "Jupiter": "Ju ",
    "Venus": "Ve ",
    "Saturn": "Sa ",
    "Rahu": "Ra ",
    "Ketu": "Ke ",
    "Ascendant": "As "
}

# Nakshatra lords in order for 27 nakshatras (cycle of 9 repeated 3 times)
NAK_LORDS_CYCLE = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

def nakshatra_lord_by_no(nak_no: int) -> str:
    # nak_no 1..27
    return NAK_LORDS_CYCLE[(nak_no - 1) % 9]

def sign_index_from_deg(deg):
    return int(normalize(deg) / 30)

def deg_in_sign(deg):
    return normalize(deg) % 30

def get_planet_awastha(norm_deg):
    # Standard Baladi Avastha by degrees in sign
    # 0-6 Bala, 6-12 Kumara, 12-18 Yuva, 18-24 Vridha, 24-30 Mrityu
    if norm_deg < 6: return "Bala"
    if norm_deg < 12: return "Kumara"
    if norm_deg < 18: return "Yuva"
    if norm_deg < 24: return "Vridha"
    return "Mrityu"

def house_from_asc_sign(asc_sign_index0, planet_sign_index0):
    # Whole sign house
    return ((planet_sign_index0 - asc_sign_index0) % 12) + 1

def sign_index_from_deg(deg):
    return int(normalize(deg) / 30)

def deg_in_sign(deg):
    return normalize(deg) % 30

def sign_name_from_index(i):
    return ZODIAC[i % 12]

def to_sign_number(sign_index_0):
    # Aries=0 -> 1, Pisces=11 -> 12
    return (sign_index_0 % 12) + 1

def normalize(x):
    x = x % 360
    return x + 360 if x < 0 else x

def julday(dt_utc):
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    )

def compute_nak_charan(moon_deg):
    nak_no = int(moon_deg / 13.3333333333) + 1
    nak_name = NAKSHATRAS[nak_no - 1]
    nak_offset = moon_deg % 13.3333333333
    charan = int(nak_offset / 3.3333333333) + 1
    return nak_no, nak_name, charan, nak_offset

def get_tithi_name(tithi_no: int) -> str:
    if tithi_no <= 15:
        return "Shukla-" + TITHI_BASE[tithi_no - 1]
    if tithi_no == 30:
        return "Krishna-Amavasya"
    return "Krishna-" + TITHI_BASE[tithi_no - 16]

def get_karana(tithi_no: int, half_tithi: int) -> str:
    # n = half-tithi index 1..60
    n = (tithi_no - 1) * 2 + half_tithi + 1
    if n == 1:
        return "Kimstughna"
    if n == 58:
        return "Shakuni"
    if n == 59:
        return "Chatushpada"
    if n == 60:
        return "Naga"
    cycle = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]
    return cycle[(n - 2) % 7]

def main():
    data = json.loads(sys.argv[1])

    tz = pytz.timezone(data.get("timezone", "Asia/Kolkata"))
    include_debug = bool(data.get("include_debug", False))
    include_offset_sweep = bool(data.get("include_offset_sweep", False))

    # Input datetime = local time
    dt_local = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S")
    dt_local = tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.utc)

    lat = float(data["lat"])
    lon = float(data["lon"])

    jd_birth = julday(dt_utc)

    #  Astrotalk knob (offset hours)
    offset_hours = float(data.get("avakhada_ref_offset_hours", 0))
    ref_jd = jd_birth + (offset_hours / 24.0)

    # --- sunrise/sunset for LOCAL date ---
    local_midnight = dt_local.replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_utc = local_midnight.astimezone(pytz.utc)
    jd0 = julday(midnight_utc)

    geopos = (lon, lat, 0)

    rsmi = swe.rise_trans(jd0, swe.SUN, swe.CALC_RISE, geopos, 0, 0, swe.FLG_SWIEPH)
    ssmi = swe.rise_trans(jd0, swe.SUN, swe.CALC_SET,  geopos, 0, 0, swe.FLG_SWIEPH)

    sunrise_jd = rsmi[1][0]
    sunset_jd  = ssmi[1][0]

    # --- Sidereal calculations (Lahiri) ---
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    #  IMPORTANT: Use ref_jd for panchang components
    sun = normalize(swe.calc_ut(ref_jd, swe.SUN, flags_sid)[0][0])
    moon = normalize(swe.calc_ut(ref_jd, swe.MOON, flags_sid)[0][0])

    moon_sign = ZODIAC[int(moon / 30)]

    # Ascendant (keep birth-time)
    cusps, ascmc = swe.houses(jd_birth, lat, lon)
    asc_trop = ascmc[0]
    ayan = swe.get_ayanamsa(jd_birth)
    asc = normalize(asc_trop - ayan)
    asc_sign = ZODIAC[int(asc / 30)]

    # tithi / yoga / nakshatra / charan / karana
    diff = normalize(moon - sun)
    tithi_no = int(diff / 12) + 1
    tithi_name = get_tithi_name(tithi_no)

    nak_no, nak_name, charan, nak_offset = compute_nak_charan(moon)

    yoga_no = int(normalize(sun + moon) / 13.3333333333) + 1
    yoga_name = YOGAS[yoga_no - 1]

    half_tithi = int((diff % 12) / 6)  # 0 or 1
    karana_name = get_karana(tithi_no, half_tithi)

    #  Requested: single flat object
    panchangObj = {
        "tithi_number": tithi_no,
        "tithi_name": tithi_name,

        "nak_number": nak_no,
        "nak_name": nak_name,
        "charan": charan,
        "nak_offset": nak_offset,

        "yog_number": yoga_no,
        "yog_name": yoga_name,

        "karan_name": karana_name,
        "half_tithi": half_tithi,

        "sunrise_jd": sunrise_jd,
        "sunset_jd": sunset_jd,
    }

    out = {
        "moon_sign": moon_sign,
        "ascendant_sign": asc_sign,
        "panchangObj": panchangObj
    }

    # -----------------------------
    # PLANETS DETAILED (D1)
    # -----------------------------
    # Use birth-time jd for chart positions
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    PLANETS_ORDER = [
        (0, "Sun", swe.SUN),
        (1, "Moon", swe.MOON),
        (2, "Mars", swe.MARS),
        (3, "Mercury", swe.MERCURY),
        (4, "Jupiter", swe.JUPITER),
        (5, "Venus", swe.VENUS),
        (6, "Saturn", swe.SATURN),
        (7, "Rahu", swe.MEAN_NODE)  # Ketu derived
    ]

    asc_sign_index0 = sign_index_from_deg(asc)

    planets_detailed = []
    rahu_data = None

    for pid, pname, pcode in PLANETS_ORDER:
        xx, flg = swe.calc_ut(jd_birth, pcode, flags_sid)
        full_deg = normalize(xx[0])
        speed = xx[3]
        norm_deg = deg_in_sign(full_deg)

        psign_index0 = sign_index_from_deg(full_deg)
        psign = ZODIAC[psign_index0]
        sign_lord = SIGN_LORD.get(psign)

        nak_no, nak_name, nak_pad, _nak_offset = compute_nak_charan(full_deg)
        nak_lord = nakshatra_lord_by_no(nak_no)

        is_retro = "true" if speed < 0 else "false"

        house = house_from_asc_sign(asc_sign_index0, psign_index0)

        row = {
            "id": pid,
            "name": pname,
            "fullDegree": float(full_deg),
            "normDegree": float(norm_deg),
            "speed": float(speed),
            "isRetro": is_retro,
            "sign": psign,
            "signLord": sign_lord,
            "nakshatra": nak_name,
            "nakshatraLord": nak_lord,
            "nakshatra_pad": int(nak_pad),
            "house": int(house),
            "is_planet_set": False,
            "planet_awastha": get_planet_awastha(norm_deg)
        }

        planets_detailed.append(row)

        if pname == "Rahu":
            rahu_data = row

    # Ketu = Rahu + 180 (same speed; always retro in most systems)
    if rahu_data:
        ketu_full = normalize(rahu_data["fullDegree"] + 180.0)
        ketu_norm = deg_in_sign(ketu_full)
        ketu_sign_index0 = sign_index_from_deg(ketu_full)
        ketu_sign = ZODIAC[ketu_sign_index0]
        ketu_sign_lord = SIGN_LORD.get(ketu_sign)

        knak_no, knak_name, knak_pad, _ = compute_nak_charan(ketu_full)
        knak_lord = nakshatra_lord_by_no(knak_no)
        ketu_house = house_from_asc_sign(asc_sign_index0, ketu_sign_index0)

        planets_detailed.append({
            "id": 8,
            "name": "Ketu",
            "fullDegree": float(ketu_full),
            "normDegree": float(ketu_norm),
            "speed": float(rahu_data["speed"]),
            "isRetro": "true",
            "sign": ketu_sign,
            "signLord": ketu_sign_lord,
            "nakshatra": knak_name,
            "nakshatraLord": knak_lord,
            "nakshatra_pad": int(knak_pad),
            "house": int(ketu_house),
            "is_planet_set": False,
            "planet_awastha": get_planet_awastha(ketu_norm)
        })

    # Ascendant as planet-like object (id 9)
    asc_full = normalize(asc)
    asc_norm = deg_in_sign(asc_full)
    an_no, an_name, an_pad, _ = compute_nak_charan(asc_full)
    an_lord = nakshatra_lord_by_no(an_no)

    planets_detailed.append({
        "id": 9,
        "name": "Ascendant",
        "fullDegree": float(asc_full),
        "normDegree": float(asc_norm),
        "speed": 0,
        "isRetro": "false",
        "sign": asc_sign,
        "signLord": SIGN_LORD.get(asc_sign),
        "nakshatra": an_name,
        "nakshatraLord": an_lord,
        "nakshatra_pad": int(an_pad),
        "house": 1,
        "is_planet_set": False,
        "planet_awastha": "--"
    })

    # attach to output
    out["planets_detailed"] = planets_detailed


    # -----------------------------
    # LAGNA CHART UI ARRAY (D1)
    # -----------------------------
    asc_sign_index0 = sign_index_from_deg(asc)

    # Planet positions at birth time (D1)
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    planet_pos = []  # {name, sign_index0, deg_in_sign}

    for pname, pcode in PLANETS_D1:
        xx, flg = swe.calc_ut(jd_birth, pcode, flags_sid)
        pdeg = normalize(xx[0])
        psign_index0 = sign_index_from_deg(pdeg)
        planet_pos.append({
            "name": pname,
            "sign_index0": psign_index0,
            "deg_in_sign": deg_in_sign(pdeg)
        })

    # KETU = RAHU + 180
    rahu_item = next((p for p in planet_pos if p["name"] == "RAHU"), None)
    if rahu_item:
        ketu_deg = normalize((rahu_item["sign_index0"] * 30) + rahu_item["deg_in_sign"] + 180)
        ketu_sign_index0 = sign_index_from_deg(ketu_deg)
        planet_pos.append({
            "name": "KETU",
            "sign_index0": ketu_sign_index0,
            "deg_in_sign": deg_in_sign(ketu_deg)
        })

    # Build 12-sign array starting from Ascendant sign (like your example)
    lagna_chart_ui = []
    for i in range(12):
        si0 = (asc_sign_index0 + i) % 12
        sname = sign_name_from_index(si0)
        snum = to_sign_number(si0)

        plist = [p for p in planet_pos if p["sign_index0"] == si0]
        planets = [p["name"] for p in plist]
        planet_small = [PLANET_SHORT.get(p["name"], (p["name"][:2].title() + " ")) for p in plist]
        planet_degree = [round(p["deg_in_sign"], 2) for p in plist]  # degrees within sign

        lagna_chart_ui.append({
            "sign": snum,
            "sign_name": sname,
            "planet": planets,
            "planet_small": planet_small,
            "planet_degree": planet_degree
        })

    # add to output
    out["lagna_chart_ui"] = lagna_chart_ui

    if include_debug:
        out["debug"] = {
            "birth_jd": jd_birth,
            "avakhada_ref_offset_hours": offset_hours,
            "ref_jd_used": ref_jd,
            "moon_sidereal_deg_at_ref": moon,
            "sun_sidereal_deg_at_ref": sun,
            "nakshatra_deg_offset": nak_offset,
            "charan_calc": charan,
            "asc_sidereal_deg": asc,
            "asc_sign": asc_sign
        }

    if include_offset_sweep:
        sweep_offsets = [-18, -16, -14, -12, -10, -8, 0]
        offset_sweep = {}
        for oh in sweep_offsets:
            test_ref = jd_birth + (oh / 24.0)
            test_moon = normalize(swe.calc_ut(test_ref, swe.MOON, flags_sid)[0][0])
            tnak_no, tnak_name, tcharan, toffset = compute_nak_charan(test_moon)
            offset_sweep[str(oh)] = {
                "moon_deg": test_moon,
                "nakshatra": tnak_name,
                "charan": tcharan,
                "nak_offset": toffset
            }
        out["offset_sweep"] = offset_sweep

    print(json.dumps(out))

if __name__ == "__main__":
    main()
