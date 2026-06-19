import swisseph as swe
import pytz
from datetime import datetime, timedelta
from hindu_maah import compute_hindu_maah
from astro_constants import ZODIAC, YOGAS, TITHI_BASE
from astro_utils import normalize, julday, compute_nak_charan


# -----------------------------
# Name helpers
# -----------------------------

# -----------------------------
# Samvat Accurate Logic
# -----------------------------
SHAKA_CACHE = {}

def get_shaka_samvat(dt_local, ref_jd):
    year = dt_local.year

    if year not in SHAKA_CACHE:
        SHAKA_CACHE[year] = find_mesh_sankranti(year)

    sankranti_jd = SHAKA_CACHE[year]

    if not sankranti_jd:
        return year - 78

    return year - 78 if ref_jd >= sankranti_jd else year - 79

def find_mesh_sankranti(year):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    jd = swe.julday(year, 3, 20, 0)  # near real date
    step = 0.2  # ~5 hours

    prev = normalize(swe.calc_ut(jd, swe.SUN, flags)[0][0])

    for _ in range(50):  # max ~10 days scan
        jd += step
        curr = normalize(swe.calc_ut(jd, swe.SUN, flags)[0][0])

        # detect Pisces → Aries crossing
        if prev > 350 and curr < 10:
            low, high = jd - step, jd

            # binary refinement
            for _ in range(15):
                mid = (low + high) / 2
                sun = normalize(swe.calc_ut(mid, swe.SUN, flags)[0][0])
                if sun > 350:
                    low = mid
                else:
                    high = mid

            return (low + high) / 2

        prev = curr

    return None

def get_vikram_samvatOld(dt_local, hindu_maah):
    year = dt_local.year

    # Chaitra = new year
    if hindu_maah.get("amanta") == "Chaitra":
        return year + 57
    else:
        return year + 56

def get_vikram_samvat(dt_local):
    year = dt_local.year

    # Approx Hindu New Year (late March / early April)
    if dt_local.month > 3:
        return year + 57

    if dt_local.month < 3:
        return year + 56

    # March handling
    if dt_local.day >= 22:
        return year + 57

    return year + 56

def get_tithi_name(tithi_no: int) -> str:
    if tithi_no <= 15:
        return "Shukla-" + TITHI_BASE[tithi_no - 1]
    if tithi_no == 30:
        return "Krishna-Amavasya"
    return "Krishna-" + TITHI_BASE[tithi_no - 16]


def get_karana(tithi_no: int, half_tithi: int) -> str:
    n = (tithi_no - 1) * 2 + half_tithi + 1
    if n == 1:
        return "Kimstughna"
    if n == 58:
        return "Shakuni"
    if n == 59:
        return "Chatushpada"
    if n == 60:
        return "Naga"
    cycle = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]
    return cycle[(n - 2) % 7]

def get_ayana(sun_longitude):
    if 90 <= sun_longitude < 270:
        return "Dakshinayana"
    return "Uttarayana"

def get_panchang_yog(tithi, nakshatra, weekday):
    return f"{tithi}-{nakshatra}-{weekday}"

def get_disha_shool(weekday):
    mapping = {
        "Monday": "East",
        "Tuesday": "North",
        "Wednesday": "North",
        "Thursday": "South",
        "Friday": "West",
        "Saturday": "East",
        "Sunday": "West"
    }
    return mapping.get(weekday)

def paksha_from_tithi(tithi_no: int):
    if not tithi_no:
        return None
    return "Shukla-Paksha" if 1 <= tithi_no <= 15 else "Krishna-Paksha"


# -----------------------------
# Time helpers
# -----------------------------
def jd_ut_to_dt_utc(jd_ut: float) -> datetime:
    # JD -> unix seconds (UTC)
    ts = (jd_ut - 2440587.5) * 86400.0
    return datetime(1970, 1, 1, tzinfo=pytz.utc) + timedelta(seconds=ts)


def dt_local_midnight(dt_local: datetime) -> datetime:
    return dt_local.replace(hour=0, minute=0, second=0, microsecond=0)


def dt_to_hms(dt: datetime) -> str:
    return dt.strftime("%H:%M:%S")


def dt_to_hm(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def end_time_struct(end_dt_local: datetime, base_midnight_local: datetime):
    """
    Return {hour, minute, second} where hour can be >24
    based on delta from base_midnight_local (same local date).
    """
    delta = end_dt_local - base_midnight_local
    total_sec = int(delta.total_seconds())
    if total_sec < 0:
        total_sec = 0
    hh = total_sec // 3600
    mm = (total_sec % 3600) // 60
    ss = total_sec % 60
    return {"hour": hh, "minute": mm, "second": ss}


def end_time_ms(end_dt_utc: datetime) -> int:
    return int(end_dt_utc.timestamp() * 1000)


# -----------------------------
# Rise/Set helpers
# -----------------------------
def calc_rise_set_jd(dt_local, lat, lon, body, mode):

    local_mid = dt_local.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    utc_mid = local_mid.astimezone(pytz.utc)

    jd0 = swe.julday(
        utc_mid.year,
        utc_mid.month,
        utc_mid.day,
        12.0
    )

    # flags_rise = int(swe.CALC_RISE | swe.BIT_DISC_CENTER)
    # flags_set = int(swe.CALC_SET | swe.BIT_DISC_CENTER)
    flags_rise = swe.CALC_RISE
    flags_set = swe.CALC_SET

    try:
        rise_res = swe.rise_trans(
            jd0,
            body,
            flags_rise,
            (float(lon), float(lat), 0.0),
            0.0,
            15.0,
            swe.FLG_SWIEPH
        )

        set_res = swe.rise_trans(
            jd0,
            body,
            flags_set,
            (float(lon), float(lat), 0.0),
            0.0,
            15.0,
            swe.FLG_SWIEPH
        )

        rise_jd = rise_res[1][0]
        set_jd = set_res[1][0]

        return rise_jd, set_jd

    except Exception as e:
        print("Rise/Set error:", e)
        return None, None
# -----------------------------
# Kaals / Muhurta
# -----------------------------
def day_segment_times(sunrise_local: datetime, sunset_local: datetime, idx_1to8: int):
    day_len = (sunset_local - sunrise_local).total_seconds()
    part = day_len / 8.0
    start = sunrise_local + timedelta(seconds=part * (idx_1to8 - 1))
    end = start + timedelta(seconds=part)
    return start, end


def compute_rahukaal_gulika_yamagand(day_name: str, sunrise_local: datetime, sunset_local: datetime):
    rahu_map = {
        "Monday": 2, "Tuesday": 7, "Wednesday": 5, "Thursday": 6,
        "Friday": 4, "Saturday": 3, "Sunday": 8
    }
    gulika_map = {
        "Monday": 7, "Tuesday": 6, "Wednesday": 5, "Thursday": 4,
        "Friday": 3, "Saturday": 2, "Sunday": 1
    }
    yam_map = {
        "Monday": 4, "Tuesday": 3, "Wednesday": 2, "Thursday": 1,
        "Friday": 7, "Saturday": 6, "Sunday": 5
    }

    def seg(idx):
        if not idx:
            return {"start": None, "end": None}
        s, e = day_segment_times(sunrise_local, sunset_local, idx)
        return {"start": dt_to_hms(s), "end": dt_to_hms(e)}

    return {
        "rahukaal": seg(rahu_map.get(day_name)),
        "guliKaal": seg(gulika_map.get(day_name)),
        "yamghant_kaal": seg(yam_map.get(day_name)),
    }


def compute_abhijit_muhurta(sunrise_local: datetime, sunset_local: datetime):

    solar_noon = sunrise_local + ((sunset_local - sunrise_local) / 2)
    start = solar_noon - timedelta(minutes=24)
    end = solar_noon + timedelta(minutes=24)

    return {
        "start": dt_to_hm(start),
        "end": dt_to_hm(end)
    }


# -----------------------------
# Astronomical end-time solvers
# -----------------------------
def _sun_moon_sidereal(ref_jd: float):
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun = normalize(swe.calc_ut(ref_jd, swe.SUN, flags_sid)[0][0])
    moon = normalize(swe.calc_ut(ref_jd, swe.MOON, flags_sid)[0][0])
    return sun, moon


def _moon_sidereal(ref_jd: float):
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return normalize(swe.calc_ut(ref_jd, swe.MOON, flags_sid)[0][0])


def _sun_sidereal(ref_jd: float):
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return normalize(swe.calc_ut(ref_jd, swe.SUN, flags_sid)[0][0])


def solve_crossing_jd(ref_jd: float, fn_value_deg, target_deg: float, max_hours=72):
    """
    Find first time > ref_jd when fn_value_deg(jd) crosses target_deg (mod 360),
    using step scan + bisection.

    fn_value_deg returns a value in [0,360).
    """
    # We want to find t where normalize(fn(t) - target) == 0 crossing from "below" to "above"
    # Use wrapped difference in [-180,180) via normalize then shift.
    def f(jd):
        v = fn_value_deg(jd)
        # wrapped difference in [0,360)
        return normalize(v - target_deg)

    # Step scan
    step = 0.25 / 24.0  # 15 minutes in days
    limit = ref_jd + (max_hours / 24.0)

    prev_jd = ref_jd
    prev = f(prev_jd)

    jd = ref_jd + step
    while jd <= limit:
        cur = f(jd)

        # crossing near 0: detect wrap (e.g., prev high like 350, cur small like 2)
        if prev > 300 and cur < 60:
            # bracket [prev_jd, jd]
            a, b = prev_jd, jd
            for _ in range(30):
                m = (a + b) / 2.0
                fm = f(m)
                if fm > 300:
                    a = m
                else:
                    b = m
            return (a + b) / 2.0

        prev_jd, prev = jd, cur
        jd += step

    return None


def calc_end_times(dt_local: datetime, tz, lat: float, lon: float, ref_jd: float,
                   tithi_no: int, half_tithi: int, nak_no: int, yoga_no: int):
    """
    Return nested objects:
      tithi.end_time / end_time_ms
      nakshatra.end_time / end_time_ms
      yog.end_time / end_time_ms
      karan.end_time / end_time_ms
    """
    base_mid = dt_local_midnight(dt_local)

    sun0, moon0 = _sun_moon_sidereal(ref_jd)
    diff0 = normalize(moon0 - sun0)

    # Targets
    # tithi end at diff = tithi_no * 12 (mod 360)
    tithi_target = (tithi_no * 12.0) % 360.0

    # karan boundary at half tithi: base + 6 degrees within current tithi
    # if half_tithi=0 => karan ends at (tithi_no-1)*12 + 6
    # if half_tithi=1 => ends at tithi_no*12
    if half_tithi == 0:
        karan_target = (((tithi_no - 1) * 12.0) + 6.0) % 360.0
    else:
        karan_target = tithi_target

    # nakshatra end at moon = nak_no * (360/27)
    nak_span = 360.0 / 27.0
    nak_target = (nak_no * nak_span) % 360.0

    # yoga end at (sun+moon) = yoga_no * (360/27)
    yoga_target = (yoga_no * nak_span) % 360.0

    # Solve JD
    def diff_fn(jd):
        s, m = _sun_moon_sidereal(jd)
        return normalize(m - s)

    def moon_fn(jd):
        return _moon_sidereal(jd)

    def yoga_fn(jd):
        s, m = _sun_moon_sidereal(jd)
        return normalize(s + m)

    t_end_jd = solve_crossing_jd(ref_jd, diff_fn, tithi_target, max_hours=72)
    k_end_jd = solve_crossing_jd(ref_jd, diff_fn, karan_target, max_hours=72)
    n_end_jd = solve_crossing_jd(ref_jd, moon_fn, nak_target, max_hours=72)
    y_end_jd = solve_crossing_jd(ref_jd, yoga_fn, yoga_target, max_hours=72)

    def pack(jd_end):
        if not jd_end:
            return ({"hour": None, "minute": None, "second": None}, None)
        end_utc = jd_ut_to_dt_utc(jd_end)
        end_local = end_utc.astimezone(tz)
        return (end_time_struct(end_local, base_mid), end_time_ms(end_utc))

    t_end, t_ms = pack(t_end_jd)
    k_end, k_ms = pack(k_end_jd)
    n_end, n_ms = pack(n_end_jd)
    y_end, y_ms = pack(y_end_jd)

    return {
        "tithi_end": t_end, "tithi_ms": t_ms,
        "karan_end": k_end, "karan_ms": k_ms,
        "nak_end": n_end, "nak_ms": n_ms,
        "yog_end": y_end, "yog_ms": y_ms,
    }


# -----------------------------
# Main Panchang
# -----------------------------
def calc_sunrise_sunset_jd(dt_local, lat: float, lon: float, mode):
    return calc_rise_set_jd(dt_local, lat, lon, swe.SUN, mode)


def calc_panchang(dt_local, dt_utc, lat: float, lon: float, ref_jd: float, mode):
    tz = dt_local.tzinfo  # localized tz
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # sunrise/sunset (JD UT) for local date
    sunrise_jd, sunset_jd = calc_sunrise_sunset_jd(dt_local, lat, lon, mode)

    # moonrise/moonset for local date
    moonrise_jd, moonset_jd = calc_rise_set_jd(dt_local, lat, lon, swe.MOON, mode)

    # Panchang components at ref_jd
    sun = normalize(swe.calc_ut(ref_jd, swe.SUN, flags_sid)[0][0])
    moon = normalize(swe.calc_ut(ref_jd, swe.MOON, flags_sid)[0][0])
    # daily_dt = datetime.now(tz)
    # daily_utc = daily_dt.astimezone(pytz.utc)

    # daily_jd = swe.julday(
    #     daily_utc.year,
    #     daily_utc.month,
    #     daily_utc.day,
    #     daily_utc.hour +
    #     daily_utc.minute / 60.0 +
    #     daily_utc.second / 3600.0
    # )

    # sun = normalize(swe.calc_ut(daily_jd, swe.SUN, flags_sid)[0][0])
    # moon = normalize(swe.calc_ut(daily_jd, swe.MOON, flags_sid)[0][0])

    moon_sign = ZODIAC[int(moon / 30)]
    sun_sign = ZODIAC[int(sun / 30)]

    diff = normalize(moon - sun)

    tithi_no = int(diff / 12) + 1
    tithi_name = get_tithi_name(tithi_no)

    nak_no, nak_name, charan, nak_offset = compute_nak_charan(moon)

    sun_tropical = swe.calc_ut(ref_jd, swe.SUN)[0][0]   # tropical
    sun_longitude = sun_tropical

    weekday = dt_local.strftime("%A")

    yoga_no = int(normalize(sun + moon) / (360.0 / 27.0)) + 1
    yoga_name = YOGAS[yoga_no - 1]

    half_tithi = int((diff % 12) / 6)  # 0 or 1
    karana_name = get_karana(tithi_no, half_tithi)

    # day + kaals (need sunrise/sunset local datetimes)
    day_name = dt_local.strftime("%A")

    rahu = {"start": None, "end": None}
    guli = {"start": None, "end": None}
    yam = {"start": None, "end": None}
    abhijit = {"start": None, "end": None}

    if sunrise_jd and sunset_jd:
        sunrise_local = jd_ut_to_dt_utc(sunrise_jd).astimezone(tz)
        sunset_local = jd_ut_to_dt_utc(sunset_jd).astimezone(tz)
        if sunset_local <= sunrise_local:
            sunset_local = sunset_local + timedelta(days=1)

        kaal = compute_rahukaal_gulika_yamagand(day_name, sunrise_local, sunset_local)
        rahu = kaal["rahukaal"]
        guli = kaal["guliKaal"]
        yam = kaal["yamghant_kaal"]
        abhijit = compute_abhijit_muhurta(sunrise_local, sunset_local)

    # End times for tithi/nak/yog/karan
    ends = calc_end_times(
        dt_local=dt_local,
        tz=tz,
        lat=lat,
        lon=lon,
        ref_jd=ref_jd,
        tithi_no=tithi_no,
        half_tithi=half_tithi,
        nak_no=nak_no,
        yoga_no=yoga_no,
    )


    # Hindu Maah Details
    hindu_maah = compute_hindu_maah(ref_jd)
    
    date_local = datetime.now(tz) 
    vikram = get_vikram_samvat(dt_local)
    shaka = get_shaka_samvat(date_local, ref_jd)

    # Build object in your SAMPLE STRUCTURE
    panchangObj = {
        "day": day_name,

        # keep JD (node can convert to HH:mm:ss)
        "sunrise_jd": sunrise_jd,
        "sunset_jd": sunset_jd,
        "moonrise_jd": moonrise_jd,
        "moonset_jd": moonset_jd,

        # OPTIONAL: you can also fill direct time strings here if you want
        # (Node can also compute from JD, both are ok)
        "sunrise": dt_to_hms(jd_ut_to_dt_utc(sunrise_jd).astimezone(tz)) if sunrise_jd else None,
        "sunset": dt_to_hms(jd_ut_to_dt_utc(sunset_jd).astimezone(tz)) if sunset_jd else None,
        "moonrise": dt_to_hms(jd_ut_to_dt_utc(moonrise_jd).astimezone(tz)) if moonrise_jd else None,
        "moonset": dt_to_hms(jd_ut_to_dt_utc(moonset_jd).astimezone(tz)) if moonset_jd else None,

        # If you don’t have a special definition, keep vedic same as sunrise/sunset
        "vedic_sunrise": dt_to_hms(jd_ut_to_dt_utc(sunrise_jd).astimezone(tz)) if sunrise_jd else None,
        "vedic_sunset": dt_to_hms(jd_ut_to_dt_utc(sunset_jd).astimezone(tz)) if sunset_jd else None,

        "tithi": {
            "details": {
                "tithi_number": tithi_no,
                "tithi_name": tithi_name,
                "special": None,
                "summary": None,
                "deity": None
            },
            "end_time": ends["tithi_end"],
            "end_time_ms": ends["tithi_ms"]
        },

        "nakshatra": {
            "details": {
                "nak_number": nak_no,
                "nak_name": nak_name,
                "ruler": None,
                "deity": None,
                "special": None,
                "summary": None,
                "charan": charan
            },
            "end_time": ends["nak_end"],
            "end_time_ms": ends["nak_ms"]
        },

        "yog": {
            "details": {
                "yog_number": yoga_no,
                "yog_name": yoga_name,
                "special": None,
                "meaning": None
            },
            "end_time": ends["yog_end"],
            "end_time_ms": ends["yog_ms"]
        },

        "karan": {
            "details": {
                "karan_number": None,   # (you can map if you maintain a karan-number list)
                "karan_name": karana_name,
                "special": None,
                "deity": None
            },
            "end_time": ends["karan_end"],
            "end_time_ms": ends["karan_ms"]
        },

        "hindu_maah": hindu_maah,

        "paksha": paksha_from_tithi(tithi_no),
        "ritu": None,

        "sun_sign": sun_sign,
        "moon_sign": moon_sign,

        "ayana": get_ayana(sun_longitude),  # needs your rule (Uttarayana/Dakshinayana)
        "panchang_yog": get_panchang_yog(tithi_name, nak_name, weekday),

        "vikram_samvat": vikram,
        "shaka_samvat": shaka,
        "vkram_samvat_name": f"Vikram Samvat {vikram}",
        "shaka_samvat_name": f"Shaka Samvat {shaka}",

        "disha_shool": get_disha_shool(weekday),
        "disha_shool_remedies": "-",

        "nak_shool": {"direction": "none", "remedies": "-"},
        "moon_nivas": None,

        "abhijit_muhurta": abhijit,
        "rahukaal": rahu,
        "guliKaal": guli,
        "yamghant_kaal": yam,

        # keep your previous extra fields if needed by other code
        "nak_offset": nak_offset,
        "half_tithi": half_tithi,

        "date_local1 =": date_local.isoformat(),
        "hindu_maah1 =": hindu_maah,
        "tithi_no1 =": tithi_no,
    }

    debug = {
        "moon_sidereal_deg_at_ref": moon,
        "sun_sidereal_deg_at_ref": sun,
        "nakshatra_deg_offset": nak_offset,
        "charan_calc": charan
    }

    return moon_sign, panchangObj, debug
