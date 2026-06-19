import swisseph as swe
from astro_constants import ZODIAC, SIGN_LORD, PLANETS_ORDER, nakshatra_lord_by_no
from astro_utils import (
    normalize, deg_in_sign, sign_index_from_deg,
    compute_nak_charan, get_planet_awastha, house_from_asc_sign
)

def calc_planets_detailed(jd_birth: float, asc_sidereal_deg: float):
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    asc_sign_index0 = sign_index_from_deg(asc_sidereal_deg)

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

        nak_no, nak_name, nak_pad, _ = compute_nak_charan(full_deg)
        nak_lord = nakshatra_lord_by_no(nak_no)

        # speed == 0 => stationary, NOT retro. This is fine.
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

    # Ketu derived from Rahu
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

    return planets_detailed

def append_ascendant_as_planet(planets_detailed: list, asc_sidereal_deg: float, asc_sign: str):
    from astro_constants import SIGN_LORD, nakshatra_lord_by_no
    from astro_utils import normalize, deg_in_sign, compute_nak_charan

    asc_full = normalize(asc_sidereal_deg)
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
