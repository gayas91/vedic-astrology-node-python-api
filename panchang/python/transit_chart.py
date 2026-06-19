import sys
import json
import swisseph as swe
import pytz

from datetime import datetime

from astro_utils import normalize, julday
from transit_chart_calc import calc_transit_chart_ui


# Lahiri Ayanamsha
swe.set_sid_mode(swe.SIDM_LAHIRI)


def main():
    data = json.loads(sys.argv[1])

    tz = pytz.timezone(
        data.get("timezone", "Asia/Kolkata")
    )

    # ----------------------------------
    # USER BIRTH DATA
    # ----------------------------------

    dt_local = datetime.strptime(
        data["datetime"],
        "%Y-%m-%d %H:%M:%S"
    )

    dt_local = tz.localize(dt_local)

    dt_utc = dt_local.astimezone(
        pytz.utc
    )

    lat = float(data["lat"])
    lon = float(data["lon"])

    # ----------------------------------
    # BIRTH ASCENDANT
    # (same as Lagna Chart)
    # ----------------------------------

    jd_birth = julday(dt_utc)

    cusps, ascmc = swe.houses(
        jd_birth,
        lat,
        lon
    )

    asc_trop = ascmc[0]

    ayan = swe.get_ayanamsa(
        jd_birth
    )

    asc_sid = normalize(
        asc_trop - ayan
    )

    # ----------------------------------
    # CURRENT TRANSIT TIME
    # ----------------------------------

    current_local = datetime.now(tz)

    current_utc = current_local.astimezone(
        pytz.utc
    )

    jd_now = julday(
        current_utc
    )

    # ----------------------------------
    # TRANSIT PLANETS
    # CURRENT PLANETS
    # BIRTH ASCENDANT
    # ----------------------------------

    out = calc_transit_chart_ui(
        jd_now,
        asc_sid
    )

    print(
        json.dumps(out)
    )


if __name__ == "__main__":
    main()