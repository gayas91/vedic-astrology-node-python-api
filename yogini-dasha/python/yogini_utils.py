from datetime import timedelta
from yogini_constants import (
    NAKSHATRAS,
    YOGINI_SEQUENCE,
    NAKSHATRA_SIZE_DEG,
    TROPICAL_YEAR_DAYS
)


def normalize_deg(value):
    return value % 360.0


def get_nakshatra_from_longitude(longitude):
    longitude = normalize_deg(longitude)

    nak_index = int(longitude // NAKSHATRA_SIZE_DEG)
    if nak_index >= 27:
        nak_index = 26

    start_deg = nak_index * NAKSHATRA_SIZE_DEG
    end_deg = start_deg + NAKSHATRA_SIZE_DEG
    offset_in_nak = longitude - start_deg
    remaining_in_nak = end_deg - longitude

    return {
        "nak_number": nak_index + 1,
        "nakshatra": NAKSHATRAS[nak_index],
        "start_deg": start_deg,
        "end_deg": end_deg,
        "offset_in_nak": offset_in_nak,
        "remaining_in_nak": remaining_in_nak,
        "fraction_elapsed": offset_in_nak / NAKSHATRA_SIZE_DEG,
        "fraction_remaining": remaining_in_nak / NAKSHATRA_SIZE_DEG
    }


def get_birth_yogini_from_nakshatra(nak_number):
    """
    Keep your original project mapping.
    This is the mapping your earlier working outputs were based on.
    """
    remainder = (nak_number + 3) % 8
    if remainder == 0:
        yogini_index = 7
    else:
        yogini_index = remainder - 1

    item = YOGINI_SEQUENCE[yogini_index]
    return {
        "index": yogini_index,
        "remainder": remainder,
        "key": item["key"],
        "short_name": item["short_name"],
        "lord": item["lord"],
        "years": item["years"]
    }


def years_to_days(years_float):
    return years_float * TROPICAL_YEAR_DAYS


def days_to_ymd_approx(total_days):
    year_days = TROPICAL_YEAR_DAYS
    month_days = year_days / 12.0

    years = int(total_days // year_days)
    rem = total_days - (years * year_days)

    months = int(rem // month_days)
    rem = rem - (months * month_days)

    days = int(round(rem))

    if days >= 30:
        days -= 30
        months += 1

    if months >= 12:
        months -= 12
        years += 1

    return {
        "years": years,
        "months": months,
        "days": days
    }


def add_days(dt, days_float):
    return dt + timedelta(days=days_float)


def format_dt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_ui_date(dt):
    return dt.strftime("%d-%b-%Y")


def build_yogini_item(index):
    idx = index % len(YOGINI_SEQUENCE)
    item = YOGINI_SEQUENCE[idx]
    return {
        "index": idx,
        "key": item["key"],
        "short_name": item["short_name"],
        "lord": item["lord"],
        "years": item["years"]
    }


def build_birth_mahadasha_cycle(birth_dt_local, start_index, balance_days, total_items=8):
    timeline = []

    running_item = build_yogini_item(start_index)
    running_full_days = years_to_days(running_item["years"])
    elapsed_days = max(0.0, running_full_days - balance_days)

    current_start = add_days(birth_dt_local, -elapsed_days)
    current_end = add_days(birth_dt_local, balance_days)

    timeline.append({
        "index": running_item["index"],
        "yogini": running_item["key"],
        "yogini_short_name": running_item["short_name"],
        "lord": running_item["lord"],
        "years": running_item["years"],
        "start": current_start,
        "end": current_end
    })

    cursor_start = current_end
    idx = start_index + 1

    while len(timeline) < total_items:
        item = build_yogini_item(idx)
        item_days = years_to_days(item["years"])
        item_end = add_days(cursor_start, item_days)

        timeline.append({
            "index": item["index"],
            "yogini": item["key"],
            "yogini_short_name": item["short_name"],
            "lord": item["lord"],
            "years": item["years"],
            "start": cursor_start,
            "end": item_end
        })

        cursor_start = item_end
        idx += 1

    return timeline