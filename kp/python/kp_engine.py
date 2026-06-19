import sys
import json
from datetime import datetime, timedelta

import swisseph as swe

from kp_constants import (
    PLANETS,
    OPTIONAL_OUTER_PLANETS,
    PLANET_DISPLAY,
    WEEKDAY_LORD,
    DAY_LORDS
)
from kp_utils import (
    normalize_deg,
    format_degree,
    build_longitude_meta,
    find_house_for_longitude,
    build_chart_houses,
    build_sign_chart,
    build_bhav_chalit_chart
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

def calc_rahu_ketu(jd):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    xx, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    rahu = normalize_deg(xx[0])
    ketu = normalize_deg(rahu + 180.0)
    return rahu, ketu

def calc_houses(jd, lat, lon):
    # Placidus house system
    cusps, ascmc = swe.houses_ex(
        jd,
        lat,
        lon,
        b'P',
        swe.FLG_SIDEREAL
    )
    cusp_list = [normalize_deg(c) for c in cusps[:12]]
    asc = normalize_deg(ascmc[0])
    mc = normalize_deg(ascmc[1])
    return cusp_list, asc, mc

def build_planet_rows(jd, cusps, include_outer=True):
    rows = []

    for planet_name, planet_id in PLANETS:
        lon = calc_planet_longitude(jd, planet_id)
        meta = build_longitude_meta(lon)
        house_no = find_house_for_longitude(lon, cusps)

        rows.append({
            "planet": planet_name,
            "short_name": PLANET_DISPLAY.get(planet_name, planet_name[:2]),
            "longitude": round(lon, 6),
            "cusp": house_no,
            "sign": meta["sign"],
            "sign_lord": meta["sign_lord"],
            "star_lord": meta["star_lord"],
            "sub_lord": meta["sub_lord"],
            "nakshatra": meta["nakshatra"]
        })

    rahu, ketu = calc_rahu_ketu(jd)

    for planet_name, lon in [("Rahu", rahu), ("Ketu", ketu)]:
        meta = build_longitude_meta(lon)
        house_no = find_house_for_longitude(lon, cusps)

        rows.append({
            "planet": planet_name,
            "short_name": PLANET_DISPLAY.get(planet_name, planet_name[:2]),
            "longitude": round(lon, 6),
            "cusp": house_no,
            "sign": meta["sign"],
            "sign_lord": meta["sign_lord"],
            "star_lord": meta["star_lord"],
            "sub_lord": meta["sub_lord"],
            "nakshatra": meta["nakshatra"]
        })

    if include_outer:
        for planet_name, planet_id in OPTIONAL_OUTER_PLANETS:
            try:
                lon = calc_planet_longitude(jd, planet_id)
                meta = build_longitude_meta(lon)
                house_no = find_house_for_longitude(lon, cusps)

                rows.append({
                    "planet": planet_name,
                    "short_name": PLANET_DISPLAY.get(planet_name, planet_name[:2]),
                    "longitude": round(lon, 6),
                    "cusp": house_no,
                    "sign": meta["sign"],
                    "sign_lord": meta["sign_lord"],
                    "star_lord": meta["star_lord"],
                    "sub_lord": meta["sub_lord"],
                    "nakshatra": meta["nakshatra"]
                })
            except Exception:
                pass

    return rows

def build_cusp_rows(cusps):
    rows = []
    for i, lon in enumerate(cusps, start=1):
        meta = build_longitude_meta(lon)
        rows.append({
            "cusp": i,
            "degree": format_degree(lon, 2),
            "sign": meta["sign"],
            "sign_lord": meta["sign_lord"],
            "star_lord": meta["star_lord"],
            "sub_lord": meta["sub_lord"],
            "nakshatra": meta["nakshatra"]
        })
    return rows

def build_ruling_planets(moon_lon, asc_lon, dt_local):
    moon_meta = build_longitude_meta(moon_lon)
    asc_meta = build_longitude_meta(asc_lon)

    weekday_name = WEEKDAY_LORD[dt_local.weekday()]
    day_lord = DAY_LORDS[weekday_name]

    return {
        "moon": {
            "sign_lord": moon_meta["sign_lord"],
            "star_lord": moon_meta["star_lord"],
            "sub_lord": moon_meta["sub_lord"]
        },
        "asc": {
            "sign_lord": asc_meta["sign_lord"],
            "star_lord": asc_meta["star_lord"],
            "sub_lord": asc_meta["sub_lord"]
        },
        "day_lord": day_lord
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

        dt_local, dt_utc = local_to_utc(dob, time_str, timezone_hours)
        jd = julian_day_from_utc(dt_utc)

        cusps, asc, mc = calc_houses(jd, lat, lon)
        planet_rows = build_planet_rows(jd, cusps, include_outer=True)
        cusp_rows = build_cusp_rows(cusps)

        moon_row = next((p for p in planet_rows if p["planet"] == "Moon"), None)
        moon_lon = moon_row["longitude"] if moon_row else 0.0

        ruling_planets = build_ruling_planets(moon_lon, asc, dt_local)

        #chart_houses = build_chart_houses(cusps, planet_rows)
        sign_chart = build_sign_chart(planet_rows)

        bhav_chalit_chart = build_bhav_chalit_chart(cusps, planet_rows)

        result = {
            "chart_type": "KP",
            "ayanamsa": "Lahiri",
            "house_system": "Placidus",
            "ascendant": round(asc, 6),
            "mc": round(mc, 6),
            # "rashi_chart": {
            #     "style": "north_indian",
            #     "houses": sign_chart
            # },
            "bhav_chalit_chart": {
                "style": "north_indian",
                "houses": bhav_chalit_chart
            },
            "ruling_planets": ruling_planets,
            "planets": [
                {
                    "planet": p["planet"],
                    "cusp": p["cusp"],
                    "sign": p["sign"],
                    "sign_lord": p["sign_lord"],
                    "star_lord": p["star_lord"],
                    "sub_lord": p["sub_lord"]
                }
                for p in planet_rows
            ],
            "cusps": cusp_rows
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