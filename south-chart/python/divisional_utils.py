from divisional_constants import (
    SIGNS,
    SIGN_SHORT,
    MOVABLE_SIGNS,
    FIXED_SIGNS,
    DUAL_SIGNS,
    SOUTH_LAYOUT
)

def normalize_deg(value):
    return value % 360.0

def wrap_sign(sign_no):
    return ((sign_no - 1) % 12) + 1

def add_signs(sign_no, offset):
    return wrap_sign(sign_no + offset)

def sign_name(sign_no):
    return SIGNS[sign_no - 1]

def sign_short(sign_no):
    return SIGN_SHORT[sign_no]

def sign_number_from_longitude(longitude):
    longitude = normalize_deg(longitude)
    return int(longitude // 30) + 1

def degrees_in_sign(longitude):
    longitude = normalize_deg(longitude)
    return longitude % 30.0

def is_odd_sign(sign_no):
    return sign_no % 2 == 1

def sign_mode(sign_no):
    if sign_no in MOVABLE_SIGNS:
        return "movable"
    if sign_no in FIXED_SIGNS:
        return "fixed"
    return "dual"

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

def cusp_sign_map(cusps):
    result = {}
    for i, lon in enumerate(cusps, start=1):
        result[i] = sign_number_from_longitude(lon)
    return result

def south_cells_from_sign_map(sign_map, lagna_sign_no=None, reference_sign_no=None):
    cells = []

    for row_index, row in enumerate(SOUTH_LAYOUT):
        for col_index, sign_no in enumerate(row):
            if sign_no is None:
                cells.append({
                    "row": row_index,
                    "col": col_index,
                    "blank": True
                })
                continue

            house_no = None
            if reference_sign_no:
                house_no = ((sign_no - reference_sign_no) % 12) + 1

            item = {
                "row": row_index,
                "col": col_index,
                "blank": False,
                "sign_no": sign_no,
                "sign": sign_name(sign_no),
                "sign_short": sign_short(sign_no),
                "is_lagna": lagna_sign_no == sign_no,
                "house_no": house_no,
                "items": sign_map.get(sign_no, [])
            }
            cells.append(item)

    return cells

def empty_planet_sign_map():
    return {i: [] for i in range(1, 13)}

def append_to_sign_map(sign_map, sign_no, item):
    sign_map[sign_no].append(item)

def sort_sign_map(sign_map):
    for sign_no in sign_map:
        sign_map[sign_no] = sorted(sign_map[sign_no], key=lambda x: x.get("order", 999))
    return sign_map

def build_chart_payload(key, title, sign_map, lagna_sign_no=None, reference_sign_no=None, meta=None):
    return {
        "key": key,
        "title": title,
        "chart_style": "south_indian",
        "lagna_sign_no": lagna_sign_no,
        "reference_sign_no": reference_sign_no,
        "cells": south_cells_from_sign_map(
            sign_map=sort_sign_map(sign_map),
            lagna_sign_no=lagna_sign_no,
            reference_sign_no=reference_sign_no
        ),
        "meta": meta or {}
    }

def part_index_in_sign(longitude, divisions):
    deg = degrees_in_sign(longitude)
    size = 30.0 / divisions
    idx = int(deg / size)
    if idx >= divisions:
        idx = divisions - 1
    return idx

def varga_sign(longitude, chart_code):
    lon = normalize_deg(longitude)
    sign_no = sign_number_from_longitude(lon)
    deg = degrees_in_sign(lon)

    if chart_code == "D1":
        return sign_no

    if chart_code == "D2":
        # Parashara Hora
        if is_odd_sign(sign_no):
            return 5 if deg < 15 else 4   # Leo / Cancer
        return 4 if deg < 15 else 5       # Cancer / Leo

    if chart_code == "D3":
        idx = part_index_in_sign(lon, 3)
        offsets = [0, 4, 8]
        return add_signs(sign_no, offsets[idx])

    if chart_code == "D4":
        idx = part_index_in_sign(lon, 4)
        offsets = [0, 3, 6, 9]
        return add_signs(sign_no, offsets[idx])

    if chart_code == "D7":
        idx = part_index_in_sign(lon, 7)
        start = sign_no if is_odd_sign(sign_no) else add_signs(sign_no, 6)
        return add_signs(start, idx)

    if chart_code == "D9":
        idx = part_index_in_sign(lon, 9)
        mode = sign_mode(sign_no)
        if mode == "movable":
            start = sign_no
        elif mode == "fixed":
            start = add_signs(sign_no, 8)
        else:
            start = add_signs(sign_no, 4)
        return add_signs(start, idx)

    if chart_code == "D10":
        idx = part_index_in_sign(lon, 10)
        start = sign_no if is_odd_sign(sign_no) else add_signs(sign_no, 8)
        return add_signs(start, idx)

    if chart_code == "D12":
        idx = part_index_in_sign(lon, 12)
        return add_signs(sign_no, idx)

    if chart_code == "D16":
        idx = part_index_in_sign(lon, 16)
        mode = sign_mode(sign_no)
        start = 1 if mode == "movable" else (5 if mode == "fixed" else 9)
        return add_signs(start, idx)

    if chart_code == "D20":
        idx = part_index_in_sign(lon, 20)
        mode = sign_mode(sign_no)
        start = 1 if mode == "movable" else (9 if mode == "fixed" else 5)
        return add_signs(start, idx)

    if chart_code == "D24":
        idx = part_index_in_sign(lon, 24)
        start = 5 if is_odd_sign(sign_no) else 4
        return add_signs(start, idx)

    if chart_code == "D27":
        idx = part_index_in_sign(lon, 27)
        start = 1 if is_odd_sign(sign_no) else 7
        return add_signs(start, idx)

    if chart_code == "D30":
        # Parashara Trimsamsa (unequal)
        if is_odd_sign(sign_no):
            if deg < 5:
                return 1   # Mars -> Aries
            elif deg < 10:
                return 11  # Saturn -> Aquarius
            elif deg < 18:
                return 9   # Jupiter -> Sagittarius
            elif deg < 25:
                return 3   # Mercury -> Gemini
            else:
                return 7   # Venus -> Libra
        else:
            if deg < 5:
                return 2   # Venus -> Taurus
            elif deg < 12:
                return 6   # Mercury -> Virgo
            elif deg < 20:
                return 12  # Jupiter -> Pisces
            elif deg < 25:
                return 10  # Saturn -> Capricorn
            else:
                return 8   # Mars -> Scorpio

    if chart_code == "D40":
        idx = part_index_in_sign(lon, 40)
        start = 1 if is_odd_sign(sign_no) else 7
        return add_signs(start, idx)

    if chart_code == "D45":
        idx = part_index_in_sign(lon, 45)
        mode = sign_mode(sign_no)
        start = 1 if mode == "movable" else (5 if mode == "fixed" else 9)
        return add_signs(start, idx)

    if chart_code == "D60":
        idx = part_index_in_sign(lon, 60)
        start = 1 if is_odd_sign(sign_no) else 7
        return add_signs(start, idx)

    raise ValueError(f"Unsupported chart_code: {chart_code}")