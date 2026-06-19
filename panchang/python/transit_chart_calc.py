import swisseph as swe

from astro_constants import PLANETS_D1, PLANET_SMALL_UI
from astro_utils import normalize, sign_index_from_deg, sign_name_from_index, to_sign_number


def calc_transit_chart_ui(jd, asc_sidereal_deg):
    """
    Transit Chart (D1 Gochar with Houses)

    Output EXACTLY like lagna_chart_ui:
    [
      { sign, sign_name, planet, planet_small, planet_degree }
    ]

    Order: starting from ASC sign (like Lagna chart)
    """

    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # Ascendant sign (same as Lagna chart)
    asc_sign0 = sign_index_from_deg(asc_sidereal_deg)

    planet_pos = []

    # Get current planet positions (TRANSIT)
    for pname, pcode in PLANETS_D1:
        xx, _ = swe.calc_ut(jd, pcode, flags_sid)
        full_deg = normalize(xx[0])

        sign0 = sign_index_from_deg(full_deg)

        planet_pos.append({
            "name": pname,
            "sign_index0": sign0,
            "deg": full_deg % 30
        })

    # ☊ KETU from RAHU
    xx, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags_sid)
    rahu_full = normalize(xx[0])
    ketu_full = normalize(rahu_full + 180.0)

    planet_pos.append({
        "name": "KETU",
        "sign_index0": sign_index_from_deg(ketu_full),
        "deg": ketu_full % 30
    })

    # Build 12 houses from ASC
    chart = []

    for i in range(12):
        sign0 = (asc_sign0 + i) % 12

        sname = sign_name_from_index(sign0)
        snum = to_sign_number(sign0)

        plist = [p for p in planet_pos if p["sign_index0"] == sign0]

        planets = [p["name"] for p in plist]
        planet_small = [
            PLANET_SMALL_UI.get(p["name"], p["name"][:2])
            for p in plist
        ]

        # OPTIONAL: degrees (you can keep empty like navamsa if needed)
        planet_degree = [round(p["deg"], 2) for p in plist]

        # Add ASC in first house
        if i == 0:
            planets.append("ASC")
            planet_small.append("Asc")

        chart.append({
            "sign": snum,
            "sign_name": sname,
            "planet": planets,
            "planet_small": planet_small,
            "planet_degree": planet_degree
        })

    return chart