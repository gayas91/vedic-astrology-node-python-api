import sys
import json
from datetime import datetime, timedelta

import swisseph as swe

from ashtakavarga_constants import (
    PLANETS,
    ASHTAKAVARGA_RULES,
    BAV_TOTALS
)
from ashtakavarga_utils import (
    normalize_deg,
    sign_number_from_longitude,
    sign_name_from_number,
    move_sign,
    empty_sign_map,
    sign_map_to_rows,
    build_north_indian_chart_rows,
    total_of_sign_map,
    build_sign_chart_from_map
)

def parse_payload():
    if len(sys.argv) < 2:
        raise ValueError("Payload JSON is required")
    return json.loads(sys.argv[1])

def local_to_utc(dob, time_str, timezone_hours):
    dt_local = datetime.strptime(f"{dob} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt_local - timedelta(hours=timezone_hours)
    return dt_local, dt_utc

def julian_day_from_utc(dt_utc):
    hour_decimal = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3600000000.0
    )
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        hour_decimal,
        swe.GREG_CAL
    )

def calc_planet_longitude(jd, planet_id):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    xx, _ = swe.calc_ut(jd, planet_id, flags)
    return normalize_deg(xx[0])

def calc_ascendant_longitude(jd, lat, lon):
    # Sidereal houses with Placidus are fine here because we only need the asc sign.
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    except TypeError:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P')
    asc = normalize_deg(ascmc[0])
    return asc

def get_base_sign_positions(jd, lat, lon):
    positions = {}

    for planet_name, planet_id in PLANETS:
        lon_val = calc_planet_longitude(jd, planet_id)
        positions[planet_name] = {
            "longitude": round(lon_val, 6),
            "sign_no": sign_number_from_longitude(lon_val),
            "sign": sign_name_from_number(sign_number_from_longitude(lon_val))
        }

    asc_lon = calc_ascendant_longitude(jd, lat, lon)
    positions["Asc"] = {
        "longitude": round(asc_lon, 6),
        "sign_no": sign_number_from_longitude(asc_lon),
        "sign": sign_name_from_number(sign_number_from_longitude(asc_lon))
    }

    return positions

def compute_bav_for_target(target_key, base_positions):
    target_rules = ASHTAKAVARGA_RULES[target_key]
    bav = empty_sign_map(0)
    contributors_debug = []

    for contributor_key, benefic_houses in target_rules.items():
        contributor_sign = base_positions[contributor_key]["sign_no"]

        contributor_row = {
            "contributor": contributor_key,
            "from_sign_no": contributor_sign,
            "from_sign": sign_name_from_number(contributor_sign),
            "benefic_houses": benefic_houses
        }
        contributors_debug.append(contributor_row)

        for house_offset in range(1, 13):
            result_sign = move_sign(contributor_sign, house_offset)
            bindu = 1 if house_offset in benefic_houses else 0
            bav[result_sign] += bindu

    return bav, contributors_debug

def compute_all_ashtakavarga(base_positions):
    bav_maps = {}
    debug_meta = {}
    for target_key in ASHTAKAVARGA_RULES.keys():
        bav_map, contributors_debug = compute_bav_for_target(target_key, base_positions)
        bav_maps[target_key] = bav_map
        debug_meta[target_key] = contributors_debug

    # Sarva Ashtakavarga = sum of 7 planet BAVs, not including Lagna BAV
    sav = empty_sign_map(0)
    for key in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        for sign_no in range(1, 13):
            sav[sign_no] += bav_maps[key][sign_no]

    return bav_maps, sav, debug_meta

def build_tab_payload(tab_key, sign_map, asc_sign):
    return {
        "tab": tab_key,
        "total": total_of_sign_map(sign_map),
        "rows": sign_map_to_rows(sign_map),
        # "chart": {
        #     "style": "north_indian",
        #     "houses": build_north_indian_chart_rows(sign_map, asc_sign)
        # }
        "chart": {
            "style": "sign_based",
            "houses": build_sign_chart_from_map(sign_map)
        }
    }

def main():
    try:
        payload = parse_payload()

        dob = payload["dob"]
        time_str = payload["time"]
        lat = float(payload["lat"])
        lon = float(payload["lon"])
        timezone_hours = float(payload["timezone"])

        swe.set_sid_mode(swe.SIDM_LAHIRI)

        _, dt_utc = local_to_utc(dob, time_str, timezone_hours)
        jd = julian_day_from_utc(dt_utc)

        base_positions = get_base_sign_positions(jd, lat, lon)
        bav_maps, sav_map, _debug_meta = compute_all_ashtakavarga(base_positions)

        asc_sign = base_positions["Asc"]["sign_no"]

        tabs = {
            "Sav": build_tab_payload("Sav", sav_map, asc_sign),
            "Asc": build_tab_payload("Asc", bav_maps["Asc"], asc_sign),
            "Sun": build_tab_payload("Sun", bav_maps["Sun"], asc_sign),
            "Moon": build_tab_payload("Moon", bav_maps["Moon"], asc_sign),
            "Mars": build_tab_payload("Mars", bav_maps["Mars"], asc_sign),
            "Mercury": build_tab_payload("Mercury", bav_maps["Mercury"], asc_sign),
            "Jupiter": build_tab_payload("Jupiter", bav_maps["Jupiter"], asc_sign),
            "Venus": build_tab_payload("Venus", bav_maps["Venus"], asc_sign),
            "Saturn": build_tab_payload("Saturn", bav_maps["Saturn"], asc_sign)
        }

        bav_totals = {
            "Sun": total_of_sign_map(bav_maps["Sun"]),
            "Moon": total_of_sign_map(bav_maps["Moon"]),
            "Mars": total_of_sign_map(bav_maps["Mars"]),
            "Mercury": total_of_sign_map(bav_maps["Mercury"]),
            "Jupiter": total_of_sign_map(bav_maps["Jupiter"]),
            "Venus": total_of_sign_map(bav_maps["Venus"]),
            "Saturn": total_of_sign_map(bav_maps["Saturn"]),
            "Asc": total_of_sign_map(bav_maps["Asc"]),
            "Sav": total_of_sign_map(sav_map)
        }

        result = {
            "chart_type": "Ashtakavarga",
            "ayanamsa": "Lahiri",
            "ascendant_sign_no": asc_sign,
            "ascendant_sign": base_positions["Asc"]["sign"],
            "base_positions": base_positions,
            "tab_order": ["Sav", "Asc", "Jupiter", "Mars", "Mercury", "Moon", "Sun", "Venus", "Saturn"],
            "tabs": tabs,
            "totals": bav_totals,
            "expected_bav_totals": {
                **BAV_TOTALS,
                "Sav": 337
            },
            "validation": {
                "sun_ok": bav_totals["Sun"] == BAV_TOTALS["Sun"],
                "moon_ok": bav_totals["Moon"] == BAV_TOTALS["Moon"],
                "mars_ok": bav_totals["Mars"] == BAV_TOTALS["Mars"],
                "mercury_ok": bav_totals["Mercury"] == BAV_TOTALS["Mercury"],
                "jupiter_ok": bav_totals["Jupiter"] == BAV_TOTALS["Jupiter"],
                "venus_ok": bav_totals["Venus"] == BAV_TOTALS["Venus"],
                "saturn_ok": bav_totals["Saturn"] == BAV_TOTALS["Saturn"],
                "sav_ok": bav_totals["Sav"] == 337
            },
            "description": {
                "en": "Ashtakavarga helps measure planetary strength in different signs of the birth chart. It gives numerical points based on the placement of planets and Lagna. Each planet has its own Bhinna Ashtakavarga chart, and when all the planetary scores are added together, it forms the Sarva Ashtakavarga or SAV. In a standard chart, the total SAV score should be 337.",
                "hi": "अष्टकवर्ग का उपयोग जन्म कुंडली में ग्रहों की शक्ति और विभिन्न राशियों में उनके प्रभाव को समझने के लिए किया जाता है। यह एक संख्यात्मक प्रणाली है, जिसमें प्रत्येक ग्रह के लिए अन्य सात ग्रहों और लग्न के आधार पर अलग-अलग राशियों में अंक दिए जाते हैं। प्रत्येक ग्रह का अपना भिन्न अष्टकवर्ग होता है। जब सभी ग्रहों के भिन्न अष्टकवर्ग अंकों को जोड़ दिया जाता है, तब सरव अष्टकवर्ग या SAV बनता है। सामान्य रूप से पूरे SAV का कुल योग 337 होना चाहिए."
            },
        }

        print(json.dumps({
            "status": True,
            "data": result
        }))

    except Exception as e:
        print(json.dumps({
            "status": False,
            "message": str(e)
        }))

if __name__ == "__main__":
    main()