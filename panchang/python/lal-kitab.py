import sys, json
import swisseph as swe
import pytz
from datetime import datetime

from astro_utils import normalize, julday
from astro_constants import ZODIAC
from lagna_chart_calc import calc_lagna_chart_ui
from lal_kitab_varshphal import get_lal_kitab_varshphal


def main():
    data = json.loads(sys.argv[1])

    tz = pytz.timezone(data.get("timezone", "Asia/Kolkata"))
    include_debug = bool(data.get("include_debug", False))

    dt_local = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M")
    dt_local = tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.utc)

    lat = float(data["lat"])
    lon = float(data["lon"])

    jd_birth = julday(dt_utc)

    # Ascendant (birth-time)
    cusps, ascmc = swe.houses(jd_birth, lat, lon)
    asc_trop = ascmc[0]
    ayan = swe.get_ayanamsa(jd_birth)
    asc_sid = normalize(asc_trop - ayan)

    # Lagna chart UI array (uses birth-time jd)
    lagna_chart = calc_lagna_chart_ui(jd_birth, asc_sid)

    out = get_lal_kitab_varshphal( lagna_chart, data["dob"], int(data["year"]))

    print(json.dumps(out))

if __name__ == "__main__":
    main()
