import swisseph as swe
from datetime import timedelta

from astro_constants import nakshatra_lord_by_no
from astro_utils import normalize, compute_nak_charan

# Vimshottari order + years (standard)
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
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

NAK_LEN = 13.3333333333  # degrees per nakshatra

# apps generally use "D-M-YYYY  H:M" (no leading zeros)
def format_dt(dt_local):
    return f"{dt_local.day}-{dt_local.month}-{dt_local.year}  {dt_local.hour}:{dt_local.minute}"

def years_to_timedelta(years: float) -> timedelta:
    # Most apps approximate using civil year length.
    # Keep stable and consistent.
    days = years * 365.25
    return timedelta(days=days)

def calc_mhadasha(dt_local_birth, jd_birth: float):
    """
    Returns list of 9 Mahadasha periods (start/end) covering the 120-year cycle
    starting from the beginning of the CURRENT mahadasha at birth.

    Output format matches your sample:
    [
      { planet, planet_id, start, end },
      ...
    ]
    """
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # Moon longitude at birth (sidereal)
    moon_deg = normalize(swe.calc_ut(jd_birth, swe.MOON, flags_sid)[0][0])

    # Determine nakshatra + offset in nakshatra
    nak_no, nak_name, _charan, nak_offset = compute_nak_charan(moon_deg)

    # Mahadasha lord at birth = nakshatra lord
    start_lord = nakshatra_lord_by_no(nak_no)

    # Ensure we are using same naming as dasha order keys
    # (nakshatra_lord_by_no returns: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury)
    if start_lord not in DASHA_YEARS:
        # Fallback (should never happen)
        start_lord = "Ketu"

    total_years = DASHA_YEARS[start_lord]

    # Fraction of nakshatra already passed at birth
    frac_elapsed = nak_offset / NAK_LEN
    if frac_elapsed < 0:
        frac_elapsed = 0
    if frac_elapsed > 1:
        frac_elapsed = 1

    # elapsed years in current dasha at birth
    elapsed_years = total_years * frac_elapsed

    # Start of current mahadasha (can be before birth)
    cur_start = dt_local_birth - years_to_timedelta(elapsed_years)

    # Build 9 dasha periods starting from current dasha start
    start_index = DASHA_ORDER.index(start_lord)
    out = []
    cur = cur_start

    for i in range(9):
        lord = DASHA_ORDER[(start_index + i) % 9]
        yrs = DASHA_YEARS[lord]
        end = cur + years_to_timedelta(yrs)

        out.append({
            "planet": lord,
            "planet_id": PLANET_ID[lord],
            "start": "Birth" if i == 0 else format_dt(cur),
            "end": format_dt(end)
        })

        cur = end

    return out
