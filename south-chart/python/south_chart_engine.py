import sys
import json
from datetime import datetime, timedelta

import swisseph as swe

from divisional_constants import (
    PLANETS,
    NODES,
    OPTIONAL_OUTER,
    DIVISIONAL_TAB_ORDER,
    DIVISIONAL_LABELS
)
from divisional_utils import (
    normalize_deg,
    sign_number_from_longitude,
    sign_name,
    degrees_in_sign,
    empty_planet_sign_map,
    append_to_sign_map,
    build_chart_payload,
    varga_sign,
    find_house_for_longitude,
    cusp_sign_map
)

def parse_payload():
    if len(sys.argv) < 2:
        raise ValueError("Payload JSON is required")
    return json.loads(sys.argv[1])

def local_to_utc(date_str, time_str, timezone_hours):
    dt_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
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
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    except TypeError:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P')
    cusp_list = [normalize_deg(c) for c in cusps[:12]]
    asc = normalize_deg(ascmc[0])
    mc = normalize_deg(ascmc[1])
    return cusp_list, asc, mc

def current_transit_local(payload):
    tz_hours = float(payload["timezone"])
    if payload.get("transit_date") and payload.get("transit_time"):
        local_dt = datetime.strptime(
            f'{payload["transit_date"]} {payload["transit_time"]}',
            "%Y-%m-%d %H:%M:%S"
        )
        return local_dt

    utc_now = datetime.utcnow()
    return utc_now + timedelta(hours=tz_hours)

def build_planet_rows_for_datetime(jd, include_outer=False):
    rows = []

    order = 1
    for planet_name, planet_id, short_name in PLANETS:
        lon = calc_planet_longitude(jd, planet_id)
        rows.append({
            "planet": planet_name,
            "short_name": short_name,
            "longitude": round(lon, 6),
            "sign_no": sign_number_from_longitude(lon),
            "sign": sign_name(sign_number_from_longitude(lon)),
            "degree_in_sign": round(degrees_in_sign(lon), 6),
            "order": order
        })
        order += 1

    rahu, ketu = calc_rahu_ketu(jd)
    rows.append({
        "planet": "Rahu",
        "short_name": "Ra",
        "longitude": round(rahu, 6),
        "sign_no": sign_number_from_longitude(rahu),
        "sign": sign_name(sign_number_from_longitude(rahu)),
        "degree_in_sign": round(degrees_in_sign(rahu), 6),
        "order": order
    })
    order += 1

    rows.append({
        "planet": "Ketu",
        "short_name": "Ke",
        "longitude": round(ketu, 6),
        "sign_no": sign_number_from_longitude(ketu),
        "sign": sign_name(sign_number_from_longitude(ketu)),
        "degree_in_sign": round(degrees_in_sign(ketu), 6),
        "order": order
    })
    order += 1

    if include_outer:
        for planet_name, planet_id, short_name in OPTIONAL_OUTER:
            try:
                lon = calc_planet_longitude(jd, planet_id)
                rows.append({
                    "planet": planet_name,
                    "short_name": short_name,
                    "longitude": round(lon, 6),
                    "sign_no": sign_number_from_longitude(lon),
                    "sign": sign_name(sign_number_from_longitude(lon)),
                    "degree_in_sign": round(degrees_in_sign(lon), 6),
                    "order": order
                })
                order += 1
            except Exception:
                pass

    return rows

def build_sign_map_from_rows(rows, lagna_sign_no=None, include_lagna=True):
    sign_map = empty_planet_sign_map()

    if include_lagna and lagna_sign_no:
        append_to_sign_map(sign_map, lagna_sign_no, {
            "type": "lagna",
            "label": "La",
            "planet": "Lagna",
            "order": 0
        })

    for row in rows:
        append_to_sign_map(sign_map, row["sign_no"], {
            "type": "planet",
            "label": row["short_name"],
            "planet": row["planet"],
            "longitude": row["longitude"],
            "order": row["order"]
        })

    return sign_map

def build_varga_rows(rows, asc_lon, chart_code):
    varga_rows = []
    order = 1
    for row in rows:
        target_sign_no = varga_sign(row["longitude"], chart_code)
        varga_rows.append({
            "planet": row["planet"],
            "short_name": row["short_name"],
            "longitude": row["longitude"],
            "sign_no": target_sign_no,
            "sign": sign_name(target_sign_no),
            "order": order
        })
        order += 1

    varga_asc_sign = varga_sign(asc_lon, chart_code)
    return varga_rows, varga_asc_sign

def build_simple_chart(key, title, rows, lagna_sign_no, reference_sign_no=None, meta=None):
    sign_map = build_sign_map_from_rows(rows, lagna_sign_no=lagna_sign_no, include_lagna=True)
    return build_chart_payload(
        key=key,
        title=title,
        sign_map=sign_map,
        lagna_sign_no=lagna_sign_no,
        reference_sign_no=reference_sign_no or lagna_sign_no,
        meta=meta or {}
    )

def build_chalit_chart(natal_rows, cusps, asc_sign_no):
    house_for_planet = {}
    for row in natal_rows:
        house_for_planet[row["planet"]] = find_house_for_longitude(row["longitude"], cusps)

    house_signs = cusp_sign_map(cusps)
    sign_map = empty_planet_sign_map()

    append_to_sign_map(sign_map, asc_sign_no, {
        "type": "lagna",
        "label": "La",
        "planet": "Lagna",
        "order": 0
    })

    for house_no in range(1, 13):
        sign_no = house_signs[house_no]
        append_to_sign_map(sign_map, sign_no, {
            "type": "house",
            "label": f"H{house_no}",
            "house_no": house_no,
            "order": 100 + house_no
        })

    for row in natal_rows:
        house_no = house_for_planet[row["planet"]]
        sign_no = house_signs[house_no]
        append_to_sign_map(sign_map, sign_no, {
            "type": "planet",
            "label": row["short_name"],
            "planet": row["planet"],
            "house_no": house_no,
            "longitude": row["longitude"],
            "order": row["order"]
        })

    return build_chart_payload(
        key="chalit",
        title=DIVISIONAL_LABELS["chalit"],
        sign_map=sign_map,
        lagna_sign_no=asc_sign_no,
        reference_sign_no=asc_sign_no,
        meta={
            "mode": "bhav_chalit",
            "house_signs": house_signs
        }
    )

def build_reference_chart(key, title, natal_rows, lagna_sign_no, reference_planet):
    sign_map = build_sign_map_from_rows(natal_rows, lagna_sign_no=lagna_sign_no, include_lagna=True)

    ref_row = next((x for x in natal_rows if x["planet"] == reference_planet), None)
    reference_sign_no = ref_row["sign_no"] if ref_row else lagna_sign_no

    return build_chart_payload(
        key=key,
        title=title,
        sign_map=sign_map,
        lagna_sign_no=lagna_sign_no,
        reference_sign_no=reference_sign_no,
        meta={
            "mode": f"{reference_planet.lower()}_lagna",
            "reference_planet": reference_planet
        }
    )

def main():
    try:
        payload = parse_payload()

        dob = payload["dob"]
        time_str = payload["time"]
        lat = float(payload["lat"])
        lon = float(payload["lon"])
        timezone_hours = float(payload["timezone"])

        swe.set_sid_mode(swe.SIDM_LAHIRI)

        natal_local, natal_utc = local_to_utc(dob, time_str, timezone_hours)
        natal_jd = julian_day_from_utc(natal_utc)

        natal_rows = build_planet_rows_for_datetime(natal_jd, include_outer=False)
        natal_cusps, natal_asc, natal_mc = calc_houses(natal_jd, lat, lon)
        natal_asc_sign_no = sign_number_from_longitude(natal_asc)

        # Lagna chart (D1)
        lagna_chart = build_simple_chart(
            key="lagna",
            title=DIVISIONAL_LABELS["lagna"],
            rows=natal_rows,
            lagna_sign_no=natal_asc_sign_no,
            reference_sign_no=natal_asc_sign_no,
            meta={
                "chart_code": "D1",
                "datetime": natal_local.strftime("%Y-%m-%d %H:%M:%S"),
                "asc_longitude": round(natal_asc, 6),
                "mc_longitude": round(natal_mc, 6)
            }
        )

        # Navamsa chart (D9)
        navamsa_rows, navamsa_asc_sign = build_varga_rows(natal_rows, natal_asc, "D9")
        navamsa_chart = build_simple_chart(
            key="navamsa",
            title=DIVISIONAL_LABELS["navamsa"],
            rows=navamsa_rows,
            lagna_sign_no=navamsa_asc_sign,
            reference_sign_no=navamsa_asc_sign,
            meta={
                "chart_code": "D9"
            }
        )

        # Transit chart
        transit_local = current_transit_local(payload)
        transit_utc = transit_local - timedelta(hours=timezone_hours)
        transit_jd = julian_day_from_utc(transit_utc)
        transit_rows = build_planet_rows_for_datetime(transit_jd, include_outer=False)
        transit_cusps, transit_asc, transit_mc = calc_houses(transit_jd, lat, lon)
        transit_asc_sign_no = sign_number_from_longitude(transit_asc)

        transit_chart = build_simple_chart(
            key="transit",
            title=DIVISIONAL_LABELS["transit"],
            rows=transit_rows,
            lagna_sign_no=transit_asc_sign_no,
            reference_sign_no=transit_asc_sign_no,
            meta={
                "chart_code": "transit",
                "datetime": transit_local.strftime("%Y-%m-%d %H:%M:%S"),
                "asc_longitude": round(transit_asc, 6),
                "mc_longitude": round(transit_mc, 6)
            }
        )

        # Divisional tabs
        divisional_tabs = {}

        divisional_tabs["chalit"] = build_chalit_chart(
            natal_rows=natal_rows,
            cusps=natal_cusps,
            asc_sign_no=natal_asc_sign_no
        )

        divisional_tabs["sun"] = build_reference_chart(
            key="sun",
            title=DIVISIONAL_LABELS["sun"],
            natal_rows=natal_rows,
            lagna_sign_no=natal_asc_sign_no,
            reference_planet="Sun"
        )

        divisional_tabs["moon"] = build_reference_chart(
            key="moon",
            title=DIVISIONAL_LABELS["moon"],
            natal_rows=natal_rows,
            lagna_sign_no=natal_asc_sign_no,
            reference_planet="Moon"
        )

        for chart_code in ["D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]:
            rows, asc_sign_no = build_varga_rows(natal_rows, natal_asc, chart_code)
            divisional_tabs[chart_code] = build_simple_chart(
                key=chart_code,
                title=DIVISIONAL_LABELS[chart_code],
                rows=rows,
                lagna_sign_no=asc_sign_no,
                reference_sign_no=asc_sign_no,
                meta={
                    "chart_code": chart_code
                }
            )

        result = {
            "chart_type": "south_indian",
            "ayanamsa": "Lahiri",
            "birth_details": {
                "dob": dob,
                "time": time_str,
                "lat": lat,
                "lon": lon,
                "timezone": timezone_hours
            },
            "charts": {
                "lagna": lagna_chart,
                "navamsa": navamsa_chart,
                "transit": transit_chart,
                "divisional": {
                    "tab_order": DIVISIONAL_TAB_ORDER,
                    "tabs": divisional_tabs
                }
            }
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