import sys
import json
from datetime import datetime, timedelta

import swisseph as swe

from yogini_utils import (
    normalize_deg,
    get_nakshatra_from_longitude,
    get_birth_yogini_from_nakshatra,
    years_to_days,
    add_days,
    build_yogini_item
)

YOGINI_NAME_TO_INDEX = {
    "MAN": 0,
    "MANGALA": 0,

    "PIN": 1,
    "PINGALA": 1,

    "DHA": 2,
    "DHANYA": 2,

    "BHR": 3,
    "BHRAMARI": 3,

    "BHA": 4,
    "BHADRIKA": 4,

    "ULK": 5,
    "ULKA": 5,

    "SID": 6,
    "SIDDHA": 6,

    "SAN": 7,
    "SANKATA": 7
}


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
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal, swe.GREG_CAL)


def calc_moon_longitude(jd):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    xx, _ = swe.calc_ut(jd, swe.MOON, flags)
    return normalize_deg(xx[0])


def normalize_mahadasha_input(value):
    if value is None:
        return ""
    return str(value).strip().upper()


def build_birth_mahadasha_cycle(birth_dt_local, start_index, balance_days, total_years):
    timeline = []

    running_item = build_yogini_item(start_index)
    running_full_days = years_to_days(running_item["years"])
    elapsed_days = max(0.0, running_full_days - balance_days)

    current_start = add_days(birth_dt_local, -elapsed_days)
    current_end = add_days(birth_dt_local, balance_days)

    timeline.append({
        "index": start_index % 8,
        "yogini": running_item["key"],
        "yogini_short_name": running_item["short_name"],
        "years": running_item["years"],
        "start": current_start,
        "end": current_end
    })
    covered_days = balance_days
    cursor_start = current_end
    idx = start_index + 1
    
    while (covered_days / 365.2425) < total_years:
        item = build_yogini_item(idx)
        item_days = years_to_days(item["years"])
        item_end = add_days(cursor_start, item_days)

        timeline.append({
            "index": idx % 8,
            "yogini": item["key"],
            "yogini_short_name": item["short_name"],
            "years": item["years"],
            "start": cursor_start,
            "end": item_end
        })
        covered_days += item_days
        cursor_start = item_end
        idx += 1

    return timeline


def format_ui_date(dt):
    return dt.strftime("%d-%b-%Y")


def build_antardasha_table(mahadasha_index, maha_start, maha_end, is_birth_mahadasha=False):
    maha_item = build_yogini_item(mahadasha_index)
    maha_short = maha_item["short_name"]

    rows = []
    cursor = maha_start

    total_seconds = (maha_end - maha_start).total_seconds()
    if total_seconds <= 0:
        raise ValueError("Invalid Mahadasha span")

    for step in range(8):
        antar_item = build_yogini_item(mahadasha_index + step)

        antar_seconds = total_seconds * (antar_item["years"] / 36.0)
        antar_end = cursor + timedelta(seconds=antar_seconds)

        if step == 7:
            antar_end = maha_end

        if step == 0:
            start_label = "Birth" if is_birth_mahadasha else format_ui_date(cursor)
        else:
            start_label = format_ui_date(cursor)

        rows.append({
            "planet": f"{maha_short}-{antar_item['short_name']}",
            "start": start_label,
            "end": format_ui_date(antar_end)
        })

        cursor = antar_end

    return rows


def main():
    try:
        payload = parse_payload()

        dob = payload["dob"]
        time_str = payload["time"]
        timezone_hours = float(payload["timezone"])
        raw_mahadasha = payload["mahadasha"]

        mahadasha_input = normalize_mahadasha_input(raw_mahadasha)

        if mahadasha_input not in YOGINI_NAME_TO_INDEX:
            raise ValueError(
                f"Invalid mahadasha value: {raw_mahadasha}. "
                f"Use one of MAN, PIN, DHA, BHR, BHA, ULK, SID, SAN "
                f"or full names Mangala, Pingala, Dhanya, Bhramari, Bhadrika, Ulka, Siddha, Sankata."
            )

        swe.set_sid_mode(swe.SIDM_LAHIRI)

        birth_local, birth_utc = local_to_utc(dob, time_str, timezone_hours)
        jd = julian_day_from_utc(birth_utc)

        moon_longitude = calc_moon_longitude(jd)
        moon_nak = get_nakshatra_from_longitude(moon_longitude)
        birth_yogini = get_birth_yogini_from_nakshatra(moon_nak["nak_number"])

        balance_years = birth_yogini["years"] * moon_nak["fraction_remaining"]
        balance_days = years_to_days(balance_years)

        maha_cycle = build_birth_mahadasha_cycle(
            birth_dt_local=birth_local,
            start_index=birth_yogini["index"],
            balance_days=balance_days,
            total_years=100
        )

        wanted_index = YOGINI_NAME_TO_INDEX[mahadasha_input]
        selected = next((x for x in maha_cycle if x["index"] == wanted_index), None)

        if not selected:
            raise ValueError("Selected mahadasha not found in first cycle")

        is_birth_mahadasha = (selected["index"] == birth_yogini["index"])

        antardasha_table = build_antardasha_table(
            mahadasha_index=selected["index"],
            maha_start=selected["start"],
            maha_end=selected["end"],
            is_birth_mahadasha=is_birth_mahadasha
        )

        result = {
            "title": selected["yogini"],
            "antardasha_table": antardasha_table
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