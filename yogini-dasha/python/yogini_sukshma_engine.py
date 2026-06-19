import sys
import json
from datetime import datetime, timedelta

import swisseph as swe

from yogini_utils import (
    normalize_deg,
    get_nakshatra_from_longitude,
    get_birth_yogini_from_nakshatra,
    build_birth_mahadasha_cycle,
    build_yogini_item,
    format_ui_date,
    years_to_days
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


def normalize_dasha_input(value):
    if value is None:
        return ""
    return str(value).strip().upper()


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
            "index": antar_item["index"],
            "planet": f"{maha_short}-{antar_item['short_name']}",
            "start": start_label,
            "end": format_ui_date(antar_end),
            "_start_dt": cursor,
            "_end_dt": antar_end,
            "_short_name": antar_item["short_name"],
            "_key": antar_item["key"]
        })

        cursor = antar_end

    return rows


def build_pratyantardasha_table(
    mahadasha_index,
    antardasha_index,
    antar_start,
    antar_end,
    is_birth_pratyantardasha=False
):
    maha_item = build_yogini_item(mahadasha_index)
    antar_item = build_yogini_item(antardasha_index)

    maha_short = maha_item["short_name"]
    antar_short = antar_item["short_name"]

    rows = []
    cursor = antar_start

    total_seconds = (antar_end - antar_start).total_seconds()
    if total_seconds <= 0:
        raise ValueError("Invalid Antardasha span")

    for step in range(8):
        prat_item = build_yogini_item(antardasha_index + step)

        prat_seconds = total_seconds * (prat_item["years"] / 36.0)
        prat_end = cursor + timedelta(seconds=prat_seconds)

        if step == 7:
            prat_end = antar_end

        if step == 0:
            start_label = "Birth" if is_birth_pratyantardasha else format_ui_date(cursor)
        else:
            start_label = format_ui_date(cursor)

        rows.append({
            "index": prat_item["index"],
            "planet": f"{maha_short}-{antar_short}-{prat_item['short_name']}",
            "start": start_label,
            "end": format_ui_date(prat_end),
            "_start_dt": cursor,
            "_end_dt": prat_end,
            "_short_name": prat_item["short_name"],
            "_key": prat_item["key"]
        })

        cursor = prat_end

    return rows


def build_sukshma_table(
    mahadasha_index,
    antardasha_index,
    pratyantardasha_index,
    prat_start,
    prat_end,
    is_birth_sukshma=False
):
    maha_item = build_yogini_item(mahadasha_index)
    antar_item = build_yogini_item(antardasha_index)
    prat_item = build_yogini_item(pratyantardasha_index)

    maha_short = maha_item["short_name"]
    antar_short = antar_item["short_name"]
    prat_short = prat_item["short_name"]

    rows = []
    cursor = prat_start

    total_seconds = (prat_end - prat_start).total_seconds()
    if total_seconds <= 0:
        raise ValueError("Invalid Pratyantardasha span")

    for step in range(8):
        suk_item = build_yogini_item(pratyantardasha_index + step)

        suk_seconds = total_seconds * (suk_item["years"] / 36.0)
        suk_end = cursor + timedelta(seconds=suk_seconds)

        if step == 7:
            suk_end = prat_end

        if step == 0:
            start_label = "Birth" if is_birth_sukshma else format_ui_date(cursor)
        else:
            start_label = format_ui_date(cursor)

        rows.append({
            "planet": f"{maha_short}-{antar_short}-{prat_short}-{suk_item['short_name']}",
            "start": start_label,
            "end": format_ui_date(suk_end)
        })

        cursor = suk_end

    return rows


def main():
    try:
        payload = parse_payload()

        dob = payload["dob"]
        time_str = payload["time"]
        timezone_hours = float(payload["timezone"])
        raw_mahadasha = payload["mahadasha"]
        raw_antardasha = payload["antardasha"]
        raw_pratyantardasha = payload["pratyantardasha"]

        mahadasha_input = normalize_dasha_input(raw_mahadasha)
        antardasha_input = normalize_dasha_input(raw_antardasha)
        pratyantardasha_input = normalize_dasha_input(raw_pratyantardasha)

        if mahadasha_input not in YOGINI_NAME_TO_INDEX:
            raise ValueError(f"Invalid mahadasha value: {raw_mahadasha}")

        if antardasha_input not in YOGINI_NAME_TO_INDEX:
            raise ValueError(f"Invalid antardasha value: {raw_antardasha}")

        if pratyantardasha_input not in YOGINI_NAME_TO_INDEX:
            raise ValueError(f"Invalid pratyantardasha value: {raw_pratyantardasha}")

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
            total_items=8
        )

        wanted_maha_index = YOGINI_NAME_TO_INDEX[mahadasha_input]
        selected_maha = next((x for x in maha_cycle if x["index"] == wanted_maha_index), None)
        if not selected_maha:
            raise ValueError("Selected mahadasha not found in first cycle")

        is_birth_mahadasha = (selected_maha["index"] == birth_yogini["index"])

        antardasha_table = build_antardasha_table(
            mahadasha_index=selected_maha["index"],
            maha_start=selected_maha["start"],
            maha_end=selected_maha["end"],
            is_birth_mahadasha=is_birth_mahadasha
        )

        wanted_antar_index = YOGINI_NAME_TO_INDEX[antardasha_input]
        selected_antar = next((x for x in antardasha_table if x["index"] == wanted_antar_index), None)
        if not selected_antar:
            raise ValueError("Selected antardasha not found inside selected mahadasha")

        is_birth_pratyantardasha = (
            selected_maha["index"] == birth_yogini["index"]
            and selected_antar["index"] == birth_yogini["index"]
        )

        pratyantardasha_table = build_pratyantardasha_table(
            mahadasha_index=selected_maha["index"],
            antardasha_index=selected_antar["index"],
            antar_start=selected_antar["_start_dt"],
            antar_end=selected_antar["_end_dt"],
            is_birth_pratyantardasha=is_birth_pratyantardasha
        )

        wanted_prat_index = YOGINI_NAME_TO_INDEX[pratyantardasha_input]
        selected_prat = next((x for x in pratyantardasha_table if x["index"] == wanted_prat_index), None)
        if not selected_prat:
            raise ValueError("Selected pratyantardasha not found inside selected antardasha")

        is_birth_sukshma = (
            selected_maha["index"] == birth_yogini["index"]
            and selected_antar["index"] == birth_yogini["index"]
            and selected_prat["index"] == birth_yogini["index"]
        )

        sukshma_table = build_sukshma_table(
            mahadasha_index=selected_maha["index"],
            antardasha_index=selected_antar["index"],
            pratyantardasha_index=selected_prat["index"],
            prat_start=selected_prat["_start_dt"],
            prat_end=selected_prat["_end_dt"],
            is_birth_sukshma=is_birth_sukshma
        )

        result = {
            "title": f"{selected_maha['yogini']}-{selected_antar['_key']}-{selected_prat['_key']}",
            "sukshma_table": sukshma_table
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