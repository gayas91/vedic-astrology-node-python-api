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

def antar_years(maha: str, antar: str) -> float:
    return float(DASHA_YEARS[maha]) * (float(DASHA_YEARS[antar]) / 120.0)

def pratyantar_years(maha: str, antar: str, praty: str) -> float:
    return antar_years(maha, antar) * (float(DASHA_YEARS[praty]) / 120.0)

def calc_sookshma_vdasha(maha: str, antar: str, praty: str, praty_start: datetime):
    """
    Sookshma inside Pratyantar.
    9 items, sequence starts from praty planet.
    Each duration:
      sookshma_years = praty_years * (sookshma_lord_years / 120)
    """
    maha = maha.capitalize()
    antar = antar.capitalize()
    praty = praty.capitalize()

    if maha not in DASHA_YEARS:
        raise ValueError("Invalid maha planet")
    if antar not in DASHA_YEARS:
        raise ValueError("Invalid antar planet")
    if praty not in DASHA_YEARS:
        raise ValueError("Invalid pratyantar planet")

    praty_total_years = pratyantar_years(maha, antar, praty)

    start_index = DASHA_ORDER.index(praty)
    current = praty_start

    out = []
    for i in range(9):
        lord = DASHA_ORDER[(start_index + i) % 9]
        sook_years = praty_total_years * (float(DASHA_YEARS[lord]) / 120.0)

        end = current + years_to_timedelta(sook_years)

        out.append({
            "planet": lord,
            "planet_id": PLANET_ID[lord],
            "start": format_dt(current),
            "end": format_dt(end)
        })

        current = end

    return out
