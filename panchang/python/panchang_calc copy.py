import swisseph as swe
from astro_constants import ZODIAC, YOGAS, TITHI_BASE
from astro_utils import normalize, julday, compute_nak_charan

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
    cycle = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]
    return cycle[(n - 2) % 7]

def calc_sunrise_sunset_jd(dt_local, lat: float, lon: float) -> tuple[float, float]:
    # sunrise/sunset for LOCAL date
    local_midnight = dt_local.replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_utc = local_midnight.astimezone(dt_local.tzinfo).astimezone(__import__("pytz").utc)
    jd0 = julday(midnight_utc)

    geopos = (lon, lat, 0)
    rsmi = swe.rise_trans(jd0, swe.SUN, swe.CALC_RISE, geopos, 0, 0, swe.FLG_SWIEPH)
    ssmi = swe.rise_trans(jd0, swe.SUN, swe.CALC_SET,  geopos, 0, 0, swe.FLG_SWIEPH)
    return rsmi[1][0], ssmi[1][0]

def calc_panchang(dt_local, dt_utc, lat: float, lon: float, ref_jd: float):
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # sunrise/sunset
    sunrise_jd, sunset_jd = calc_sunrise_sunset_jd(dt_local, lat, lon)

    # panchang components at ref_jd
    sun = normalize(swe.calc_ut(ref_jd, swe.SUN, flags_sid)[0][0])
    moon = normalize(swe.calc_ut(ref_jd, swe.MOON, flags_sid)[0][0])

    moon_sign = ZODIAC[int(moon / 30)]

    diff = normalize(moon - sun)
    tithi_no = int(diff / 12) + 1
    tithi_name = get_tithi_name(tithi_no)

    nak_no, nak_name, charan, nak_offset = compute_nak_charan(moon)

    yoga_no = int(normalize(sun + moon) / 13.3333333333) + 1
    yoga_name = YOGAS[yoga_no - 1]

    half_tithi = int((diff % 12) / 6)  # 0 or 1
    karana_name = get_karana(tithi_no, half_tithi)

    panchangObj = {
        "tithi_number": tithi_no,
        "tithi_name": tithi_name,

        "nak_number": nak_no,
        "nak_name": nak_name,
        "charan": charan,
        "nak_offset": nak_offset,

        "yog_number": yoga_no,
        "yog_name": yoga_name,

        "karan_name": karana_name,
        "half_tithi": half_tithi,

        "sunrise_jd": sunrise_jd,
        "sunset_jd": sunset_jd,
    }

    debug = {
        "moon_sidereal_deg_at_ref": moon,
        "sun_sidereal_deg_at_ref": sun,
        "nakshatra_deg_offset": nak_offset,
        "charan_calc": charan
    }

    return moon_sign, panchangObj, debug
