import sys, json
import swisseph as swe
import pytz
from datetime import datetime

from astro_utils import normalize, julday
from astro_constants import ZODIAC
from daily_panchang_calc import daily_calc_panchang
from mhadasha_calc import calc_mhadasha
from planets_calc import calc_planets_detailed

# Lahiri ayanamsha
swe.set_sid_mode(swe.SIDM_LAHIRI)

def main():
    data = json.loads(sys.argv[1])
    lat = float(data["lat"])
    lon = float(data["lon"])
    mode = data["mode"]

    tz = pytz.timezone(data.get("timezone", "Asia/Kolkata"))
    include_debug = bool(data.get("include_debug", False))

    dt_local = datetime.now(tz)
    dt_utc = dt_local.astimezone(pytz.utc)

    dob_local = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S")
    dob_local = tz.localize(dob_local)
    dob_utc = dob_local.astimezone(pytz.utc)
    dob_jd_birth = julday(dob_utc)
    
    dob_cusps, dob_ascmc = swe.houses(dob_jd_birth, lat, lon)
    dob_asc_trop = dob_ascmc[0]
    dob_ayan = swe.get_ayanamsa(dob_jd_birth)
    dob_asc_sid = normalize(dob_asc_trop - dob_ayan)



    jd_birth = julday(dt_utc)

    # reference for panchang (offset-hours behavior you already have)
    offset_hours = float(data.get("avakhada_ref_offset_hours", 0))
    ref_jd = jd_birth + (offset_hours / 24.0) 
    dob_ref_jd = dob_jd_birth + (offset_hours / 24.0) 

    # Ascendant (birth-time)
    cusps, ascmc = swe.houses(jd_birth, lat, lon)
    asc_trop = ascmc[0]
    ayan = swe.get_ayanamsa(jd_birth)
    asc_sid = normalize(asc_trop - ayan)
    asc_sign = ZODIAC[int(asc_sid / 30)]

    # Panchang (uses ref_jd)
    moon_sign, panchangObj, p_debug = daily_calc_panchang(dt_local, dt_utc, lat, lon, ref_jd, mode)

    dob_moon_sign, panchangDob, dob_p_debug = daily_calc_panchang(dob_local, dob_utc, lat, lon, dob_ref_jd, mode)
    mhadasha = calc_mhadasha(dob_local, dob_jd_birth)
    planets_detailed = calc_planets_detailed(dob_jd_birth, dob_asc_sid)

    out = {
        "moon_sign": moon_sign,
        "ascendant_sign": asc_sign,
        "panchangObj": panchangObj,
        "dobNakshatra": panchangDob,
        "dob_moon_sign": dob_moon_sign,
        "mhadasha": mhadasha,
        "planets_detailed": planets_detailed
    }

    print(json.dumps(out))

if __name__ == "__main__":
    main()
