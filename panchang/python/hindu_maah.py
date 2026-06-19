# hindu_maah.py  (PATCH)

import swisseph as swe
from astro_utils import normalize

LUNAR_MONTHS = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
    "Shravana", "Bhadrapada", "Ashwin", "Kartika",
    "Margashirsha", "Pausha", "Magha", "Phalguna"
]

def _sun_moon_sidereal(ref_jd: float):
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun = normalize(swe.calc_ut(ref_jd, swe.SUN, flags_sid)[0][0])
    moon = normalize(swe.calc_ut(ref_jd, swe.MOON, flags_sid)[0][0])
    return sun, moon

def _sun_sidereal(ref_jd: float):
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return normalize(swe.calc_ut(ref_jd, swe.SUN, flags_sid)[0][0])

def _sun_sign_index_at_jd(jd_ut: float) -> int:
    return int(_sun_sidereal(jd_ut) / 30)  # 0..11

def _signed_angle_deg(x: float) -> float:
    """
    Convert any angle in degrees to signed range [-180, 180)
    """
    return ((x + 180.0) % 360.0) - 180.0

def solve_crossing_jd(ref_jd: float, fn_value_deg, target_deg: float, max_hours=400):
    """
    Find first time > ref_jd where fn_value_deg crosses target_deg (mod 360),
    using signed-angle sign-change + bisection.
    """
    def g(jd):
        v = fn_value_deg(jd)  # expected [0,360) or any deg
        return _signed_angle_deg(v - target_deg)

    step = 5 / (24 * 60)  # 5 minutes in days
    limit = ref_jd + (max_hours / 24.0)

    a = ref_jd
    ga = g(a)

    jd = ref_jd + step
    while jd <= limit:
        gb = g(jd)

        # Found a bracket if sign changes OR either side is very close to 0
        if ga == 0.0 or abs(ga) < 1e-6:
            return a
        if gb == 0.0 or abs(gb) < 1e-6:
            return jd
        if (ga < 0 and gb > 0) or (ga > 0 and gb < 0):
            # bisection
            left, right = a, jd
            gl, gr = ga, gb
            for _ in range(40):
                mid = (left + right) / 2.0
                gm = g(mid)
                if abs(gm) < 1e-7:
                    return mid
                # keep the sign-change interval
                if (gl < 0 and gm > 0) or (gl > 0 and gm < 0):
                    right, gr = mid, gm
                else:
                    left, gl = mid, gm
            return (left + right) / 2.0

        a, ga = jd, gb
        jd += step

    return None

def solve_prev_crossing_jd(ref_jd: float, fn_value_deg, target_deg: float, max_hours=400):
    """
    Find last time < ref_jd where fn_value_deg crosses target_deg (mod 360),
    using signed-angle sign-change + bisection.
    """
    def g(jd):
        v = fn_value_deg(jd)
        return _signed_angle_deg(v - target_deg)

    step = 5 / (24 * 60)  # 5 minutes
    limit = ref_jd - (max_hours / 24.0)

    b = ref_jd
    gb = g(b)

    jd = ref_jd - step
    while jd >= limit:
        ga = g(jd)

        if gb == 0.0 or abs(gb) < 1e-6:
            return b
        if ga == 0.0 or abs(ga) < 1e-6:
            return jd
        if (ga < 0 and gb > 0) or (ga > 0 and gb < 0):
            left, right = jd, b
            gl, gr = ga, gb
            for _ in range(40):
                mid = (left + right) / 2.0
                gm = g(mid)
                if abs(gm) < 1e-7:
                    return mid
                if (gl < 0 and gm > 0) or (gl > 0 and gm < 0):
                    right, gr = mid, gm
                else:
                    left, gl = mid, gm
            return (left + right) / 2.0

        b, gb = jd, ga
        jd -= step

    return None

def compute_hindu_maah(ref_jd: float):
    def diff_fn(jd):
        s, m = _sun_moon_sidereal(jd)
        return normalize(m - s)

    # Amavasya: (moon - sun) = 0°
    prev_amavasya = solve_prev_crossing_jd(ref_jd, diff_fn, 0.0, max_hours=400)
    next_amavasya = solve_crossing_jd(ref_jd, diff_fn, 0.0, max_hours=400)

    # Purnima: (moon - sun) = 180°
    prev_purnima = solve_prev_crossing_jd(ref_jd, diff_fn, 180.0, max_hours=400)

    if not prev_amavasya or not next_amavasya:
        return {
            "adhik_status": None,
            "purnimanta": None,
            "amanta": None,
            "amanta_id": None,
            "purnimanta_id": None
        }

    amanta_sign = _sun_sign_index_at_jd(prev_amavasya)
    next_sign = _sun_sign_index_at_jd(next_amavasya)
    adhik = (amanta_sign == next_sign)

    amanta_id = amanta_sign + 1
    amanta_name = LUNAR_MONTHS[amanta_sign]

    purnimanta_id = None
    purnimanta_name = None
    if prev_purnima:
        purn_sign = _sun_sign_index_at_jd(prev_purnima)
        purnimanta_id = purn_sign + 1
        purnimanta_name = LUNAR_MONTHS[purn_sign]

    return {
        "adhik_status": "Adhik" if adhik else "Normal",
        "purnimanta": purnimanta_name,
        "amanta": amanta_name,
        "amanta_id": amanta_id,
        "purnimanta_id": purnimanta_id
    }