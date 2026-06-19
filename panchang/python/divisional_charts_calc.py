import math
import swisseph as swe

from astro_constants import ZODIAC, PLANETS_D1, PLANET_SMALL_UI
from astro_utils import (
    normalize, deg_in_sign, sign_index_from_deg,
    sign_name_from_index, to_sign_number
)

# -------------- helpers to build UI chart --------------

def build_ui_chart(start_sign_index0: int, planet_sign_index0_list: list):
    """
    planet_sign_index0_list: list of tuples (planet_code, sign_index0)
    start_sign_index0: chart ordering starts from this sign
    """
    chart = []
    for i in range(12):
        si0 = (start_sign_index0 + i) % 12
        sname = sign_name_from_index(si0)
        snum = to_sign_number(si0)

        plist = [p for (p, sidx) in planet_sign_index0_list if sidx == si0]
        planet_small = [PLANET_SMALL_UI.get(p, (p[:2].title() + " ")) for p in plist]

        chart.append({
            "sign": snum,
            "sign_name": sname,
            "planet": plist,
            "planet_small": planet_small,
            "planet_degree": []  # keep empty like your example
        })
    return chart


def get_planet_longitudes_sidereal(jd_birth: float):
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    out = []
    for pname, pcode in PLANETS_D1:
        xx, _ = swe.calc_ut(jd_birth, pcode, flags_sid)
        deg = normalize(xx[0])
        out.append((pname, deg))

    # Ketu = Rahu + 180
    rahu_deg = None
    for pname, deg in out:
        if pname == "RAHU":
            rahu_deg = deg
            break
    if rahu_deg is not None:
        ketu_deg = normalize(rahu_deg + 180.0)
        out.append(("KETU", ketu_deg))

    return out


# -------------- divisional mapping rules --------------
# NOTE: These are standard Parashari mappings used widely.
# If later you want to match a specific app 1:1, we can adjust rules.

def d1_sign_index0(full_deg: float) -> int:
    return sign_index_from_deg(full_deg)


# D2 Hora (Parashara):
# Odd signs: first 15° -> Sun (Leo), last 15° -> Moon (Cancer)
# Even signs: first 15° -> Moon (Cancer), last 15° -> Sun (Leo)
def d2_hora_sign_index0(full_deg: float) -> int:
    s0 = sign_index_from_deg(full_deg)
    pos = deg_in_sign(full_deg)
    is_odd = (s0 % 2 == 0)  # Aries(0)=odd sign in zodiac counting; treat Aries as "odd"
    if is_odd:
        return 4 if pos < 15 else 3  # Leo=4, Cancer=3
    else:
        return 3 if pos < 15 else 4  # Cancer then Leo


# D3 Drekkana (Parashara):
# 0-10° -> same sign
# 10-20° -> 5th from sign
# 20-30° -> 9th from sign
def d3_drekkana_sign_index0(full_deg: float) -> int:
    s0 = sign_index_from_deg(full_deg)
    pos = deg_in_sign(full_deg)
    if pos < 10:
        return s0
    elif pos < 20:
        return (s0 + 4) % 12
    else:
        return (s0 + 8) % 12


# D4 Chaturthamsa:
# 0-7.5° -> same sign
# 7.5-15° -> 4th from sign
# 15-22.5° -> 7th from sign
# 22.5-30° -> 10th from sign
def d4_chaturthamsa_sign_index0(full_deg: float) -> int:
    s0 = sign_index_from_deg(full_deg)
    pos = deg_in_sign(full_deg)
    part = int(pos / 7.5)  # 0..3
    return (s0 + part * 3) % 12


# D7 Saptamsa:
# Each sign -> 7 parts of ~4°17' (30/7)
# Odd signs start from same sign; even signs start from 7th from sign.
def d7_saptamsa_sign_index0(full_deg: float) -> int:
    s0 = sign_index_from_deg(full_deg)
    pos = deg_in_sign(full_deg)
    part = int(pos / (30.0 / 7.0))  # 0..6
    is_odd = (s0 % 2 == 0)
    start = s0 if is_odd else (s0 + 6) % 12
    return (start + part) % 12


# D9 Navamsa (standard):
# 9 parts; movable start = same, fixed start = 9th, dual start = 5th
def d9_navamsa_sign_index0(full_deg: float) -> int:
    NAV = 30.0 / 9.0
    MOVABLE = {0, 3, 6, 9}
    FIXED = {1, 4, 7, 10}
    s0 = sign_index_from_deg(full_deg)
    pos = deg_in_sign(full_deg)
    part = int(pos / NAV)  # 0..8

    if s0 in MOVABLE:
        start = s0
    elif s0 in FIXED:
        start = (s0 + 8) % 12
    else:
        start = (s0 + 4) % 12

    return (start + part) % 12


# D10 Dasamsa (standard Parashara):
# 10 parts of 3°
# Odd signs start from same sign; even signs start from 9th from sign.
def d10_dasamsa_sign_index0(full_deg: float) -> int:
    s0 = sign_index_from_deg(full_deg)
    pos = deg_in_sign(full_deg)
    part = int(pos / 3.0)  # 0..9
    is_odd = (s0 % 2 == 0)
    start = s0 if is_odd else (s0 + 8) % 12
    return (start + part) % 12


# D12 Dwadasamsa:
# 12 parts of 2°30'
# start from same sign for all
def d12_dwadasamsa_sign_index0(full_deg: float) -> int:
    s0 = sign_index_from_deg(full_deg)
    pos = deg_in_sign(full_deg)
    part = int(pos / (30.0 / 12.0))  # 0..11
    return (s0 + part) % 12


# For higher vargas (D16/D20/D24/D27/D30/D40/D45/D60):
# many apps use Parashara/standard mapping; if you want exact 1:1 with a specific app,
# we can adjust, but below will provide stable output in correct format.

def simple_varga_sign(full_deg: float, D: int) -> int:
    """
    Generic fallback:
    sign index = floor((longitude * D)/30) mod 12
    This gives consistent varga placement; for strict Parashara rules for every D,
    we can later refine chart-by-chart.
    """
    lng = normalize(full_deg)
    return int((lng * D) / 30.0) % 12


# -------------- main public function --------------

def calc_divisional_charts(jd_birth: float, asc_sidereal_deg: float):
    """
    Returns:
    [
      { name: "Chalit", chart: [...] },
      { name: "Sun", chart: [...] },
      ...
    ]
    """

    planets = get_planet_longitudes_sidereal(jd_birth)

    # D1 positions
    d1_positions = [(p, d1_sign_index0(deg)) for (p, deg) in planets]

    # Start signs for ordering
    asc_sign0 = sign_index_from_deg(asc_sidereal_deg)

    # Sun-sign ordering (D1 but chart starts from Sun sign)
    sun_sign0 = next((d1_sign_index0(deg) for (p, deg) in planets if p == "SUN"), asc_sign0)

    # Moon-sign ordering (D1 but chart starts from Moon sign)
    moon_sign0 = next((d1_sign_index0(deg) for (p, deg) in planets if p == "MOON"), asc_sign0)

    divisional = []

    # 1) "Chalit" (format only): start from asc; use D1 placements
    divisional.append({
        "name": "Chalit",
        "chart": build_ui_chart(asc_sign0, d1_positions)
    })

    # 2) "Sun" (D1 placements ordered from Sun sign)
    divisional.append({
        "name": "Sun",
        "chart": build_ui_chart(sun_sign0, d1_positions)
    })

    # 3) "Moon" (D1 placements ordered from Moon sign)
    divisional.append({
        "name": "Moon",
        "chart": build_ui_chart(moon_sign0, d1_positions)
    })

    # D2 Hora
    d2_positions = [(p, d2_hora_sign_index0(deg)) for (p, deg) in planets]
    divisional.append({
        "name": "Hora (D-2)",
        "chart": build_ui_chart(d2_hora_sign_index0(asc_sidereal_deg), d2_positions)
    })

    # D3 Drekkana
    d3_positions = [(p, d3_drekkana_sign_index0(deg)) for (p, deg) in planets]
    divisional.append({
        "name": "Drekkana (D-3)",
        "chart": build_ui_chart(d3_drekkana_sign_index0(asc_sidereal_deg), d3_positions)
    })

    # D4 Chaturthamsa
    d4_positions = [(p, d4_chaturthamsa_sign_index0(deg)) for (p, deg) in planets]
    divisional.append({
        "name": "Chaturthamsa (D-4)",
        "chart": build_ui_chart(d4_chaturthamsa_sign_index0(asc_sidereal_deg), d4_positions)
    })

    # D7 Saptamsa
    d7_positions = [(p, d7_saptamsa_sign_index0(deg)) for (p, deg) in planets]
    divisional.append({
        "name": "Saptamsa (D-7)",
        "chart": build_ui_chart(d7_saptamsa_sign_index0(asc_sidereal_deg), d7_positions)
    })

    # D9 Navamsa (you already have navamsa_chart separately, but include here too if you want)
    d9_positions = [(p, d9_navamsa_sign_index0(deg)) for (p, deg) in planets]
    divisional.append({
        "name": "Navamsa (D-9)",
        "chart": build_ui_chart(d9_navamsa_sign_index0(asc_sidereal_deg), d9_positions)
    })

    # D10 Dasamsa
    d10_positions = [(p, d10_dasamsa_sign_index0(deg)) for (p, deg) in planets]
    divisional.append({
        "name": "Dasamsa (D-10)",
        "chart": build_ui_chart(d10_dasamsa_sign_index0(asc_sidereal_deg), d10_positions)
    })

    # D12 Dwadasamsa
    d12_positions = [(p, d12_dwadasamsa_sign_index0(deg)) for (p, deg) in planets]
    divisional.append({
        "name": "Dwadasamsa (D-12)",
        "chart": build_ui_chart(d12_dwadasamsa_sign_index0(asc_sidereal_deg), d12_positions)
    })

    # Higher vargas (generic stable mapping; we can refine to strict Parashara if needed)
    for (name, D) in [
        ("Shodasamsa (D-16)", 16),
        ("Vimsamsa (D-20)", 20),
        ("Chaturvimsamsa (D-24)", 24),
        ("Saptavimsamsa (D-27)", 27),
        ("Trimsamsa (D-30)", 30),
        ("khevedamsa (D-40)", 40),
        ("Akshavedamsa (D-45)", 45),
        ("Shastiamsa (D-60)", 60),
    ]:
        d_positions = [(p, simple_varga_sign(deg, D)) for (p, deg) in planets]
        divisional.append({
            "name": name,
            "chart": build_ui_chart(simple_varga_sign(asc_sidereal_deg, D), d_positions)
        })

    return divisional
