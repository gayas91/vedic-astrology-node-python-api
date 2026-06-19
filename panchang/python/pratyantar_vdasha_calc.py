from datetime import datetime, timedelta

DASHA_ORDER = [
    "Ketu", "Venus", "Sun", "Moon",
    "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

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
    return timedelta(days=years * 365.25)

def format_dt(dt: datetime):
    return f"{dt.day}-{dt.month}-{dt.year}  {dt.hour}:{dt.minute}"

def calc_antardasha_years(maha_planet: str, antar_planet: str) -> float:
    """
    Antar years inside given Mahadasha:
    antar_years = maha_years * (antar_lord_years / 120)
    """
    maha_years = float(DASHA_YEARS[maha_planet])
    antar_years = maha_years * (float(DASHA_YEARS[antar_planet]) / 120.0)
    return antar_years

def calc_pratyantar_vdasha(maha_planet: str, antar_planet: str, antar_start: datetime):
    """
    Returns 9 pratyantar periods inside the given antar.
    Pratyantar duration:
      praty_years = antar_years * (praty_lord_years / 120)
    The sequence starts from antar_planet.
    """
    maha_planet = maha_planet.capitalize()
    antar_planet = antar_planet.capitalize()

    if maha_planet not in DASHA_YEARS:
        raise ValueError("Invalid maha planet")
    if antar_planet not in DASHA_YEARS:
        raise ValueError("Invalid antar planet")

    antar_years_total = calc_antardasha_years(maha_planet, antar_planet)

    start_index = DASHA_ORDER.index(antar_planet)
    current = antar_start

    out = []
    for i in range(9):
        lord = DASHA_ORDER[(start_index + i) % 9]
        praty_years = antar_years_total * (float(DASHA_YEARS[lord]) / 120.0)

        end = current + years_to_timedelta(praty_years)

        out.append({
            "planet": lord,
            "planet_id": PLANET_ID[lord],
            "start": format_dt(current),
            "end": format_dt(end)
        })

        current = end

    return out
