import swisseph as swe
import pytz
from datetime import datetime, timedelta

from astro_utils import normalize, sign_index_from_deg, sign_name_from_index, to_sign_number
from astro_constants import SIGN_LORD, PLANETS_D1, PLANET_SMALL_UI, ZODIAC


def jd_to_datetime_utc(jd: float) -> datetime:
    # JD -> UTC datetime
    # Unix epoch JD = 2440587.5
    sec = (jd - 2440587.5) * 86400.0
    return datetime(1970, 1, 1, tzinfo=pytz.utc) + timedelta(seconds=sec)


def datetime_utc_to_jd(dt_utc: datetime) -> float:
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )


def angle_diff(a, b):
    """
    returns shortest signed difference a-b in degrees in (-180..180]
    """
    d = (a - b) % 360.0
    if d > 180:
        d -= 360.0
    return d


def sun_sidereal_deg(jd_ut: float) -> float:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return normalize(swe.calc_ut(jd_ut, swe.SUN, flags)[0][0])


def find_solar_return_jd(natal_sun_deg: float, approx_jd: float) -> float:
    """
    Find JD when Sun sidereal longitude matches natal_sun_deg near approx_jd.
    Uses bracket + binary search on angle difference.
    """
    # Search window +/- 3 days
    left = approx_jd - 3.0
    right = approx_jd + 3.0

    def f(jd):
        return angle_diff(sun_sidereal_deg(jd), natal_sun_deg)

    # Try to bracket a sign change
    fl = f(left)
    fr = f(right)

    # If not bracketed, expand a bit
    if fl * fr > 0:
        left -= 5.0
        right += 5.0
        fl = f(left)
        fr = f(right)

    # If still not bracketed, fallback: do a local scan and bracket
    if fl * fr > 0:
        step = 0.25  # 6 hours
        prev_jd = left
        prev_f = f(prev_jd)
        found = False
        jd = left + step
        while jd <= right:
            cur_f = f(jd)
            if prev_f * cur_f <= 0:
                left, right = prev_jd, jd
                fl, fr = prev_f, cur_f
                found = True
                break
            prev_jd, prev_f = jd, cur_f
            jd += step

        if not found:
            # As a last resort, just return approx_jd (won't be exact)
            return approx_jd

    # Binary search
    for _ in range(80):
        mid = (left + right) / 2.0
        fm = f(mid)
        if abs(fm) < 1e-7:
            return mid
        if fl * fm <= 0:
            right = mid
            fr = fm
        else:
            left = mid
            fl = fm

    return (left + right) / 2.0


def get_varshaphal_chart_ui(jd_return: float, lat: float, lon: float):
    """
    Build the same 12-sign UI chart array at jd_return.
    Chart ordering starts from Varshaphal Ascendant sign.
    """
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # Ascendant at return time (sidereal)
    cusps, ascmc = swe.houses(jd_return, lat, lon)
    asc_trop = ascmc[0]
    ayan = swe.get_ayanamsa(jd_return)
    asc_sid = normalize(asc_trop - ayan)

    asc_sign_index0 = sign_index_from_deg(asc_sid)

    # Planet positions in D1 at jd_return
    planet_positions = []  # {name, sign_index0}

    for pname, pcode in PLANETS_D1:
        xx, _ = swe.calc_ut(jd_return, pcode, flags_sid)
        pdeg = normalize(xx[0])
        psign0 = sign_index_from_deg(pdeg)
        planet_positions.append((pname, psign0))

    # Add Ketu from Rahu+180
    rahu_deg = normalize(swe.calc_ut(jd_return, swe.MEAN_NODE, flags_sid)[0][0])
    ketu_deg = normalize(rahu_deg + 180.0)
    planet_positions.append(("KETU", sign_index_from_deg(ketu_deg)))

    # Build 12 blocks from asc
    chart = []
    for i in range(12):
        si0 = (asc_sign_index0 + i) % 12
        sname = sign_name_from_index(si0)
        snum = to_sign_number(si0)

        plist = [p for (p, sidx) in planet_positions if sidx == si0]
        psmall = [PLANET_SMALL_UI.get(p, (p[:2].title() + " ")) for p in plist]

        chart.append({
            "sign": snum,
            "sign_name": sname,
            "planet": plist,
            "planet_small": psmall,
            "planet_degree": []
        })

    year_lord = SIGN_LORD.get(ZODIAC[asc_sign_index0], None)

    return year_lord, chart


def format_dt_seconds(dt_local: datetime) -> str:
    return f"{dt_local.day:02d}-{dt_local.month:02d}-{dt_local.year} {dt_local.hour:02d}:{dt_local.minute:02d}:{dt_local.second:02d}"


def calc_varshaphal(dt_local_birth: datetime, jd_birth: float, lat: float, lon: float, timezone: str, varshaphal_year: int = None):
    """
    Returns:
    {
      "year_lord": "...",
      "varshaphal_date": "DD-MM-YYYY HH:MM:SS",
      "chart": [...]
    }

    varshaphal_year:
      If not provided -> uses current year in that timezone.
    """
    tz = pytz.timezone(timezone)

    # Natal sun sidereal longitude
    natal_sun = sun_sidereal_deg(jd_birth)

    # Decide target year
    if varshaphal_year is None:
        now_local = datetime.now(tz)
        varshaphal_year = now_local.year

    # Approx: same calendar date as birth, in target year
    approx_local = dt_local_birth.replace(year=varshaphal_year)
    approx_utc = approx_local.astimezone(pytz.utc)
    approx_jd = datetime_utc_to_jd(approx_utc)

    # Find exact solar return JD
    jd_return = find_solar_return_jd(natal_sun, approx_jd)

    # Convert to local datetime for output
    dt_return_utc = jd_to_datetime_utc(jd_return)
    dt_return_local = dt_return_utc.astimezone(tz)

    year_lord, chart = get_varshaphal_chart_ui(jd_return, lat, lon)

    return {
        "year_lord": year_lord,
        "varshaphal_date": format_dt_seconds(dt_return_local),
        "chart": chart
    }
