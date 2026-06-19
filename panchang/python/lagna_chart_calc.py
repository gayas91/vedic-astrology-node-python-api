import swisseph as swe
from astro_constants import PLANETS_D1, PLANET_SMALL_UI
from astro_utils import (
    normalize, deg_in_sign, sign_index_from_deg,
    sign_name_from_index, to_sign_number
)

def calc_lagna_chart_ui(jd_birth: float, asc_sidereal_deg: float):
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    asc_sign_index0 = sign_index_from_deg(asc_sidereal_deg)

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
        rahu_full = normalize((rahu_item["sign_index0"] * 30) + rahu_item["deg_in_sign"])
        ketu_full = normalize(rahu_full + 180)
        ketu_sign_index0 = sign_index_from_deg(ketu_full)
        planet_pos.append({
            "name": "KETU",
            "sign_index0": ketu_sign_index0,
            "deg_in_sign": deg_in_sign(ketu_full)
        })

    lagna_chart_ui = []
    for i in range(12):
        si0 = (asc_sign_index0 + i) % 12
        sname = sign_name_from_index(si0)
        snum = to_sign_number(si0)

        plist = [p for p in planet_pos if p["sign_index0"] == si0]
        planets = [p["name"] for p in plist]
        planet_small = [PLANET_SMALL_UI.get(p["name"], (p["name"][:2].title() + " ")) for p in plist]
        planet_degree = [round(p["deg_in_sign"], 2) for p in plist]

        lagna_chart_ui.append({
            "sign": snum,
            "sign_name": sname,
            "planet": planets,
            "planet_small": planet_small,
            "planet_degree": planet_degree
        })

    return lagna_chart_ui
