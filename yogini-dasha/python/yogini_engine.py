import sys
import json
from datetime import datetime, timedelta

import swisseph as swe

from yogini_constants import TROPICAL_YEAR_DAYS
from yogini_utils import (
    normalize_deg,
    get_nakshatra_from_longitude,
    get_birth_yogini_from_nakshatra,
    years_to_days,
    add_days,
    format_dt,
    build_yogini_item
)

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS = [
    ("Sun", 0, "Su"),
    ("Moon", 1, "Mo"),
    ("Mercury", 2, "Me"),
    ("Venus", 3, "Ve"),
    ("Mars", 4, "Ma"),
    ("Jupiter", 5, "Ju"),
    ("Saturn", 6, "Sa")
]

OPTIONAL_OUTER_PLANETS = [
    ("Uranus", 7, "Ur"),
    ("Neptune", 8, "Ne"),
    ("Pluto", 9, "Pl")
]


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


def calc_moon_longitude(jd):
    return calc_planet_longitude(jd, swe.MOON)


def calc_rahu_ketu(jd):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    xx, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    rahu = normalize_deg(xx[0])
    ketu = normalize_deg(rahu + 180.0)
    return rahu, ketu


def calc_houses(jd, lat, lon):
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    except TypeError:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P')

    cusp_list = [normalize_deg(c) for c in cusps[:12]]
    asc = normalize_deg(ascmc[0])
    mc = normalize_deg(ascmc[1])
    return cusp_list, asc, mc


def sign_number_from_longitude(longitude):
    return int(normalize_deg(longitude) // 30) + 1


def sign_name(sign_no):
    return SIGNS[sign_no - 1]


def angular_distance(start, end):
    return (end - start) % 360.0


def is_between_cusps(start, end, point):
    total_arc = angular_distance(start, end)
    point_arc = angular_distance(start, point)
    return point_arc <= total_arc + 1e-8


def find_house_for_longitude(longitude, cusps):
    longitude = normalize_deg(longitude)
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if is_between_cusps(start, end, longitude):
            return i + 1
    return 12


def build_rashi_chart(jd, lat, lon):
    cusps, asc, mc = calc_houses(jd, lat, lon)
    asc_sign_no = sign_number_from_longitude(asc)

    houses = []
    for i, cusp_lon in enumerate(cusps, start=1):
        houses.append({
            "house": i,
            "sign_no": sign_number_from_longitude(cusp_lon),
            "sign": sign_name(sign_number_from_longitude(cusp_lon)),
            "planets": []
        })

    planet_rows = []
    order = 1

    for planet_name, planet_id, short_name in PLANETS:
        lon_val = calc_planet_longitude(jd, planet_id)
        house_no = find_house_for_longitude(lon_val, cusps)

        planet_rows.append({
            "planet": planet_name,
            "short_name": short_name,
            "longitude": round(lon_val, 6),
            "house": house_no,
            "sign_no": sign_number_from_longitude(lon_val),
            "sign": sign_name(sign_number_from_longitude(lon_val)),
            "order": order
        })
        order += 1

    rahu, ketu = calc_rahu_ketu(jd)
    for planet_name, short_name, lon_val in [
        ("Rahu", "Ra", rahu),
        ("Ketu", "Ke", ketu)
    ]:
        house_no = find_house_for_longitude(lon_val, cusps)
        planet_rows.append({
            "planet": planet_name,
            "short_name": short_name,
            "longitude": round(lon_val, 6),
            "house": house_no,
            "sign_no": sign_number_from_longitude(lon_val),
            "sign": sign_name(sign_number_from_longitude(lon_val)),
            "order": order
        })
        order += 1

    for planet_name, planet_id, short_name in OPTIONAL_OUTER_PLANETS:
        try:
            lon_val = calc_planet_longitude(jd, planet_id)
            house_no = find_house_for_longitude(lon_val, cusps)
            planet_rows.append({
                "planet": planet_name,
                "short_name": short_name,
                "longitude": round(lon_val, 6),
                "house": house_no,
                "sign_no": sign_number_from_longitude(lon_val),
                "sign": sign_name(sign_number_from_longitude(lon_val)),
                "order": order
            })
            order += 1
        except Exception:
            pass

    for p in planet_rows:
        houses[p["house"] - 1]["planets"].append(p["short_name"])

    return {
        "chart_style": "north_indian",
        "lagna_sign_no": asc_sign_no,
        "lagna_sign": sign_name(asc_sign_no),
        "asc_longitude": round(asc, 6),
        "mc_longitude": round(mc, 6),
        "houses": houses
    }


def build_mahadasha_timeline(birth_dt_local, start_index, balance_days, total_years):
    timeline = []

    running_item = build_yogini_item(start_index)
    running_full_days = years_to_days(running_item["years"])
    elapsed_days = max(0.0, running_full_days - balance_days)

    current_start = add_days(birth_dt_local, -elapsed_days)
    current_end = add_days(birth_dt_local, balance_days)

    age_start_days = -elapsed_days
    age_end_days = balance_days

    timeline.append({
        "yogini": running_item["key"],
        "yogini_short_name": running_item["short_name"],
        "lord": running_item["lord"],
        "duration_years": running_item["years"],
        "start": format_dt(current_start),
        "end": format_dt(current_end),
        "age_start_years": round(age_start_days / TROPICAL_YEAR_DAYS, 6),
        "age_end_years": round(age_end_days / TROPICAL_YEAR_DAYS, 6),
        "is_running_at_birth": True
    })

    covered_days = balance_days
    cursor_start = current_end
    idx = start_index + 1

    while (covered_days / TROPICAL_YEAR_DAYS) < total_years:
        item = build_yogini_item(idx)
        item_days = years_to_days(item["years"])
        item_end = add_days(cursor_start, item_days)

        age_start = covered_days / TROPICAL_YEAR_DAYS
        covered_days += item_days
        age_end = covered_days / TROPICAL_YEAR_DAYS

        timeline.append({
            "yogini": item["key"],
            "yogini_short_name": item["short_name"],
            "lord": item["lord"],
            "duration_years": item["years"],
            "start": format_dt(cursor_start),
            "end": format_dt(item_end),
            "age_start_years": round(age_start, 6),
            "age_end_years": round(age_end, 6),
            "is_running_at_birth": False
        })

        cursor_start = item_end
        idx += 1

    return timeline


def format_ui_date(datetime_str):
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%d-%b-%Y")


def main():
    try:
        payload = parse_payload()

        dob = payload["dob"]
        time_str = payload["time"]
        lat = float(payload["lat"])
        lon = float(payload["lon"])
        timezone_hours = float(payload["timezone"])

        swe.set_sid_mode(swe.SIDM_LAHIRI)

        birth_local, birth_utc = local_to_utc(dob, time_str, timezone_hours)
        jd = julian_day_from_utc(birth_utc)

        moon_longitude = calc_moon_longitude(jd)
        moon_nak = get_nakshatra_from_longitude(moon_longitude)
        birth_yogini = get_birth_yogini_from_nakshatra(moon_nak["nak_number"])

        balance_years = birth_yogini["years"] * moon_nak["fraction_remaining"]
        balance_days = years_to_days(balance_years)

        # only generate one cycle worth of entries, like screenshot UI
        timeline = build_mahadasha_timeline(
            birth_dt_local=birth_local,
            start_index=birth_yogini["index"],
            balance_days=balance_days,
            total_years=100
        )

        first_cycle = timeline

        mahadasha_table = []
        for i, item in enumerate(first_cycle):
            mahadasha_table.append({
                "planet": item["yogini_short_name"],
                "start": "Birth" if i == 0 else format_ui_date(item["start"]),
                "end": format_ui_date(item["end"])
            })

        rashi_chart = build_rashi_chart(jd, lat, lon)

        result = {
            "title": first_cycle[0]["yogini"],
            "mahadasha_table": mahadasha_table,
            "rashi_chart": rashi_chart
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