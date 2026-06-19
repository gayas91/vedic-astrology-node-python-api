import sys, json
import swisseph as swe
import pytz
from datetime import datetime

from astro_utils import normalize, julday
from astro_constants import ZODIAC
from planets_calc import calc_planets_detailed, append_ascendant_as_planet
from planets_calc_explanation import generate_all_explanations


# Lahiri ayanamsha
swe.set_sid_mode(swe.SIDM_LAHIRI)

def split_planets(planets, size=5):
    for i in range(0, len(planets), size):
        yield planets[i:i+size]

def main():
    data = json.loads(sys.argv[1])

    tz = pytz.timezone(data.get("timezone", "Asia/Kolkata"))
    include_debug = bool(data.get("include_debug", False))

    dt_local = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S")
    dt_local = tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.utc)

    lat = float(data["lat"])
    lon = float(data["lon"])
    groq_api_key = data["groq_api_key"]

    jd_birth = julday(dt_utc)

    # Ascendant (birth-time)
    cusps, ascmc = swe.houses(jd_birth, lat, lon)
    asc_trop = ascmc[0]
    ayan = swe.get_ayanamsa(jd_birth)
    asc_sid = normalize(asc_trop - ayan)
    asc_sign = ZODIAC[int(asc_sid / 30)]


    # Planets detailed (uses birth-time jd)
    planets_detailed = calc_planets_detailed(jd_birth, asc_sid)
    append_ascendant_as_planet(planets_detailed, asc_sid, asc_sign)

    # all_results = []

    # for chunk in split_planets(planets_detailed, 7):
    #     result = generate_all_explanations(groq_api_key, chunk)
    #     all_results.extend(result)

    # # FINAL FORMAT
    # out = [
    #     {
    #         "planet": item.get("planet"),
    #         "explanation": item.get("text")
    #     }
    #     for item in all_results
    # ]

    chunk1 = planets_detailed[:5]
    chunk2 = planets_detailed[5:]

    result1 = generate_all_explanations(groq_api_key, chunk1)
    result2 = generate_all_explanations(groq_api_key, chunk2)
    out = result1 + result2

    print(json.dumps(out))

if __name__ == "__main__":
    main()
