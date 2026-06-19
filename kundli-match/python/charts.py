import swisseph as swe
import pytz
from astro_utils import normalize, julday, compute_nak_charan, sign_index_from_deg, house_from_asc_sign
from astro_constants import ZODIAC

swe.set_sid_mode(swe.SIDM_LAHIRI)

def sidereal_lon(jd_ut, planet):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return normalize(swe.calc_ut(jd_ut, planet, flags)[0][0])

def ascendant_sidereal(jd_ut, lat, lon):
    # Compute tropical ascendant then subtract ayanamsa to get sidereal asc degree
    cusps, ascmc = swe.houses(jd_ut, lat, lon)
    asc_trop = ascmc[0]
    ayan = swe.get_ayanamsa_ut(jd_ut)
    return normalize(asc_trop - ayan)

def build_birth_chart_minimal(dt_local, lat, lon):
    # dt_local must be timezone-aware
    dt_utc = dt_local.astimezone(pytz.utc)
    jd = julday(dt_utc)

    asc_sid = ascendant_sidereal(jd, lat, lon)
    moon_sid = sidereal_lon(jd, swe.MOON)
    mars_sid = sidereal_lon(jd, swe.MARS)

    # Signs
    asc_sign_index0 = sign_index_from_deg(asc_sid)
    moon_sign_index0 = sign_index_from_deg(moon_sid)
    mars_sign_index0 = sign_index_from_deg(mars_sid)

    asc_sign = ZODIAC[asc_sign_index0]
    moon_sign = ZODIAC[moon_sign_index0]

    # Nakshatra + charan from Moon sidereal longitude
    nak_no, nak_name, charan, nak_offset = compute_nak_charan(moon_sid)

    #  Manglik house from Ascendant SIGN (standard whole-sign)
    mars_house = house_from_asc_sign(asc_sign_index0, mars_sign_index0)

    return {
        "jd_ut": jd,
        "asc_sid_deg": asc_sid,
        "ascendant_sign": asc_sign,

        "moon_sid_deg": moon_sid,
        "moon_sign": moon_sign,
        "nak_number": nak_no,
        "nak_name": nak_name,
        "charan": charan,

        "mars_sid_deg": mars_sid,
        "mars_house": mars_house
    }
