import math
import swisseph as swe

from astro_constants import PLANETS_D1, PLANET_SMALL_UI, ZODIAC
from astro_utils import normalize, deg_in_sign, sign_index_from_deg, sign_name_from_index, to_sign_number

NAVAMSA_PART = 30.0 / 9.0  # 3.333333333333...

MOVABLE = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn (0-based)
FIXED   = {1, 4, 7, 10}  # Taurus, Leo, Scorpio, Aquarius
DUAL    = {2, 5, 8, 11}  # Gemini, Virgo, Sagittarius, Pisces

def navamsa_sign_index0(full_deg: float) -> int:
    """
    full_deg: 0..360 (sidereal)
    returns navamsa sign index 0..11
    """
    full_deg = normalize(full_deg)
    s0 = sign_index_from_deg(full_deg)          # base sign
    pos = deg_in_sign(full_deg)                 # degree within base sign (0..30)

    pada = int(math.floor(pos / NAVAMSA_PART))  # 0..8
    if pada < 0: pada = 0
    if pada > 8: pada = 8

    if s0 in MOVABLE:
        start = s0
    elif s0 in FIXED:
        start = (s0 + 8) % 12   # 9th from sign
    else:
        start = (s0 + 4) % 12   # 5th from sign (DUAL)

    return (start + pada) % 12

def calc_navamsa_chart_ui(jd_birth: float, asc_sidereal_deg: float):
    """
    Output format exactly like your example:
    [
      { sign, sign_name, planet, planet_small, planet_degree },
      ...
    ]
    Order: starting from Navamsa Lagna sign (D9 ascendant).
    """
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # Navamsa Lagna sign from Ascendant degree
    asc_d9_sign0 = navamsa_sign_index0(asc_sidereal_deg)

    # Compute navamsa sign for each planet at birth time
    planet_pos = []  # {name, sign_index0, deg_in_sign?}

    for pname, pcode in PLANETS_D1:
        xx, flg = swe.calc_ut(jd_birth, pcode, flags_sid)
        pdeg = normalize(xx[0])

        d9_sign0 = navamsa_sign_index0(pdeg)

        # (optional) keep degree list empty like your sample
        planet_pos.append({
            "name": pname,
            "sign_index0": d9_sign0,
            "deg": None
        })

    # Ketu = Rahu + 180 (then navamsa)
    rahu_item = next((p for p in planet_pos if p["name"] == "RAHU"), None)
    if rahu_item:
        # compute Rahu full degree again to get exact Ketu degree
        xx, flg = swe.calc_ut(jd_birth, swe.MEAN_NODE, flags_sid)
        rahu_full = normalize(xx[0])
        ketu_full = normalize(rahu_full + 180.0)

        d9_ketu_sign0 = navamsa_sign_index0(ketu_full)
        planet_pos.append({
            "name": "KETU",
            "sign_index0": d9_ketu_sign0,
            "deg": None
        })

    # Build 12-sign array starting from Navamsa Lagna sign
    navamsa_chart = []
    for i in range(12):
        si0 = (asc_d9_sign0 + i) % 12
        sname = sign_name_from_index(si0)
        snum = to_sign_number(si0)

        plist = [p for p in planet_pos if p["sign_index0"] == si0]
        planets = [p["name"] for p in plist]
        planet_small = [PLANET_SMALL_UI.get(p["name"], (p["name"][:2].title() + " ")) for p in plist]

        # Your sample shows empty list, so keep it empty
        planet_degree = []

        navamsa_chart.append({
            "sign": snum,
            "sign_name": sname,
            "planet": planets,
            "planet_small": planet_small,
            "planet_degree": planet_degree
        })

    return navamsa_chart
