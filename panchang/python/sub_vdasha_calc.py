from datetime import datetime, timedelta

# Vimshottari order
DASHA_ORDER = [
    "Ketu", "Venus", "Sun", "Moon",
    "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

# Mahadasha years
DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17
}

PLANET_ID = {
    "Sun": 0,
    "Moon": 1,
    "Mars": 2,
    "Mercury": 3,
    "Jupiter": 4,
    "Venus": 5,
    "Saturn": 6,
    "Rahu": 7,
    "Ketu": 8
}

def years_to_timedelta(years: float):
    # Astrology apps use civil year
    return timedelta(days=years * 365.25)

def format_dt(dt: datetime):
    return f"{dt.day}-{dt.month}-{dt.year}  {dt.hour}:{dt.minute}"

def calc_sub_vdasha(maha_planet: str, maha_start: datetime):
    maha_planet = maha_planet.capitalize()

    if maha_planet not in DASHA_YEARS:
        raise ValueError("Invalid planet name")

    maha_years = DASHA_YEARS[maha_planet]
    start_index = DASHA_ORDER.index(maha_planet)

    current = maha_start
    result = []

    for i in range(9):
        sub_planet = DASHA_ORDER[(start_index + i) % 9]
        sub_years = maha_years * (DASHA_YEARS[sub_planet] / 120.0)

        end = current + years_to_timedelta(sub_years)

        result.append({
            "planet": sub_planet,
            "planet_id": PLANET_ID[sub_planet],
            "start": format_dt(current),
            "end": format_dt(end)
        })

        current = end

    return result
