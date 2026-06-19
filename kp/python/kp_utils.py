from kp_constants import (
    SIGNS,
    SIGN_LORDS,
    NAKSHATRAS,
    VIMSHOTTARI_ORDER,
    DASHA_YEARS,
    NAKSHATRA_SIZE
)

def normalize_deg(value):
    return value % 360.0

def angular_distance(start, end):
    return (end - start) % 360.0

def format_degree(value, digits=2):
    return round(normalize_deg(value), digits)

def get_sign(longitude):
    longitude = normalize_deg(longitude)
    sign_index = int(longitude // 30)
    sign_name = SIGNS[sign_index]
    return {
        "sign_no": sign_index + 1,
        "sign": sign_name,
        "degree_in_sign": longitude % 30
    }

def get_sign_lord(sign_name):
    return SIGN_LORDS[sign_name]

def get_nakshatra(longitude):
    longitude = normalize_deg(longitude)
    nak_index = int(longitude // NAKSHATRA_SIZE)
    if nak_index >= 27:
        nak_index = 26

    nak_name = NAKSHATRAS[nak_index]
    star_lord = VIMSHOTTARI_ORDER[nak_index % 9]
    start_deg = nak_index * NAKSHATRA_SIZE
    offset_in_nak = longitude - start_deg

    return {
        "nak_number": nak_index + 1,
        "nakshatra": nak_name,
        "star_lord": star_lord,
        "offset_in_nak": offset_in_nak,
        "start_deg": start_deg
    }

def get_sub_lord(longitude):
    nk = get_nakshatra(longitude)
    star_lord = nk["star_lord"]
    offset = nk["offset_in_nak"]

    start_index = VIMSHOTTARI_ORDER.index(star_lord)
    ordered = VIMSHOTTARI_ORDER[start_index:] + VIMSHOTTARI_ORDER[:start_index]

    offset_arcmin = offset * 60.0
    cumulative = 0.0

    for lord in ordered:
        sub_size_arcmin = 800.0 * (DASHA_YEARS[lord] / 120.0)
        cumulative += sub_size_arcmin
        if offset_arcmin <= cumulative + 1e-8:
            return {
                "nakshatra": nk["nakshatra"],
                "star_lord": star_lord,
                "sub_lord": lord
            }

    return {
        "nakshatra": nk["nakshatra"],
        "star_lord": star_lord,
        "sub_lord": ordered[-1]
    }

def build_longitude_meta(longitude):
    s = get_sign(longitude)
    nk = get_sub_lord(longitude)

    return {
        "longitude": normalize_deg(longitude),
        "sign_no": s["sign_no"],
        "sign": s["sign"],
        "degree_in_sign": s["degree_in_sign"],
        "sign_lord": get_sign_lord(s["sign"]),
        "nakshatra": nk["nakshatra"],
        "star_lord": nk["star_lord"],
        "sub_lord": nk["sub_lord"]
    }

def is_between_cusps(start, end, point):
    start = normalize_deg(start)
    end = normalize_deg(end)
    point = normalize_deg(point)

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

def build_chart_houses(cusps, planets):
    houses = []

    for i in range(12):
        cusp_meta = build_longitude_meta(cusps[i])
        houses.append({
            "house": i + 1,
            "sign": cusp_meta["sign"],
            "sign_no": cusp_meta["sign_no"],
            "planets": []
        })

    for planet in planets:
        house_no = planet["cusp"]
        houses[house_no - 1]["planets"].append(planet["short_name"])

    return houses

def build_sign_chart(planets):
    sign_chart = []

    # Initialize 12 signs
    for i in range(12):
        sign_chart.append({
            "sign": i + 1,
            "sign_name": SIGNS[i],
            "planet": [],
            "planet_small": [],
            "planet_degree": []
        })

    for p in planets:
        sign_name = p["sign"]
        sign_index = SIGNS.index(sign_name)

        # Degree inside sign
        degree_in_sign = p["longitude"] % 30

        sign_chart[sign_index]["planet"].append(p["planet"].upper())
        sign_chart[sign_index]["planet_small"].append(p["short_name"] + " ")
        sign_chart[sign_index]["planet_degree"].append(round(degree_in_sign, 2))

    return sign_chart

def build_bhav_chalit_chart(cusps, planets):
    houses = []

    for i in range(12):
        cusp_meta = build_longitude_meta(cusps[i])

        houses.append({
            "house": i + 1,
            "sign": cusp_meta["sign_no"],
            "sign_name": cusp_meta["sign"],
            "planet": [],
            "planet_small": [],
            "planet_degree": []
        })

    for p in planets:
        house_no = p["cusp"]

        degree_in_sign = p["longitude"] % 30

        houses[house_no - 1]["planet"].append(
            p["planet"].upper()
        )

        houses[house_no - 1]["planet_small"].append(
            p["short_name"]
        )

        houses[house_no - 1]["planet_degree"].append(
            round(degree_in_sign, 2)
        )

    return houses