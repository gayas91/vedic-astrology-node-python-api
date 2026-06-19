import sys, json
import swisseph as swe
import pytz
from datetime import datetime

from astro_utils import normalize, julday
from astro_constants import ZODIAC
from panchang_calc import calc_panchang
from planets_calc import calc_planets_detailed, append_ascendant_as_planet
from lagna_chart_calc import calc_lagna_chart_ui
from mhadasha_calc import calc_mhadasha
from navamsa_chart_calc import calc_navamsa_chart_ui
from divisional_charts_calc import calc_divisional_charts
from varshaphal_calc import calc_varshaphal


# Lahiri ayanamsha
swe.set_sid_mode(swe.SIDM_LAHIRI)

def main():
    data = json.loads(sys.argv[1])

    tz = pytz.timezone(data.get("timezone", "Asia/Kolkata"))
    include_debug = bool(data.get("include_debug", False))

    dt_local = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S")
    dt_local = tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.utc)

    lat = float(data["lat"])
    lon = float(data["lon"])

    mode = data["mode"]

    jd_birth = julday(dt_utc)

    # reference for panchang (offset-hours behavior you already have)
    offset_hours = float(data.get("avakhada_ref_offset_hours", 0))
    ref_jd = jd_birth + (offset_hours / 24.0)

    # Ascendant (birth-time)
    cusps, ascmc = swe.houses(jd_birth, lat, lon)
    asc_trop = ascmc[0]
    ayan = swe.get_ayanamsa(jd_birth)
    asc_sid = normalize(asc_trop - ayan)
    asc_sign = ZODIAC[int(asc_sid / 30)]

    # Panchang (uses ref_jd)
    moon_sign, panchangObj, p_debug = calc_panchang(dt_local, dt_utc, lat, lon, ref_jd, mode)

    out = {
        "moon_sign": moon_sign,
        "ascendant_sign": asc_sign,
        "panchangObj": panchangObj
    }

    # Planets detailed (uses birth-time jd)
    planets_detailed = calc_planets_detailed(jd_birth, asc_sid)
    append_ascendant_as_planet(planets_detailed, asc_sid, asc_sign)
    out["planets_detailed"] = planets_detailed

    # Lagna chart UI array (uses birth-time jd)
    out["lagna_chart_ui"] = calc_lagna_chart_ui(jd_birth, asc_sid)

    # Mahadasha (Vimshottari)
    out["mhadasha"] = calc_mhadasha(dt_local, jd_birth)

    # Navamsa Chart
    out["navamsa_chart"] = calc_navamsa_chart_ui(jd_birth, asc_sid)

    # Divisional Charts
    out["divisional_charts"] = calc_divisional_charts(jd_birth, asc_sid)

    # Varshaphal / Vershful
    varshaphal_year = data.get("varshaphal_year")  # optional
    out["Vershful"] = calc_varshaphal(
        dt_local_birth=dt_local,
        jd_birth=jd_birth,
        lat=lat,
        lon=lon,
        timezone=data.get("timezone", "Asia/Kolkata"),
        varshaphal_year=int(varshaphal_year) if varshaphal_year else None
    )

    if include_debug:
        out["debug"] = {
            "birth_jd": jd_birth,
            "avakhada_ref_offset_hours": offset_hours,
            "ref_jd_used": ref_jd,
            "asc_sidereal_deg": asc_sid,
            "asc_sign": asc_sign,
            **p_debug
        }

    print(json.dumps(out))

if __name__ == "__main__":
    main()
