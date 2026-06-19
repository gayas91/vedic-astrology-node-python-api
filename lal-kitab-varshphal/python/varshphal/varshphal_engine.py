import sys
import json
import swisseph as swe
import pytz
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
swe.set_sid_mode(swe.SIDM_LAHIRI)

FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_TRUEPOS

# -----------------------------
# PLANETS (INCLUDING OUTER) 
# -----------------------------
PLANETS = {
    swe.SUN: "Su",
    swe.MOON: "Mo",
    swe.MARS: "Ma",
    swe.MERCURY: "Me",
    swe.JUPITER: "Ju",
    swe.VENUS: "Ve",
    swe.SATURN: "Sa",
    swe.URANUS: "Ur",
    swe.NEPTUNE: "Ne",
    swe.PLUTO: "Pl"
}

def julday(dt_utc):
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )

# -----------------------------
# SOLAR RETURN (HIGH PRECISION)
# -----------------------------
from datetime import datetime, timedelta

def solar_return(dt_birth_utc, year):
    natal_sun = swe.calc_ut(julday(dt_birth_utc), swe.SUN, FLAGS)[0][0]

    # initial guess (same date next year)
    dt_guess = dt_birth_utc.replace(year=year)

    # search around ±2 days
    dt = dt_guess - timedelta(days=2)

    best_dt = dt
    min_diff = 999

    #  coarse search (hour level)
    for i in range(96):  # 4 days × 24 hours
        jd = julday(dt)
        sun = swe.calc_ut(jd, swe.SUN, FLAGS)[0][0]

        diff = abs(sun - natal_sun)

        if diff < min_diff:
            min_diff = diff
            best_dt = dt

        dt += timedelta(hours=1)

    #  fine tuning (minute level)
    dt = best_dt - timedelta(hours=1)

    for i in range(120):  # 2 hours × 60 minutes
        jd = julday(dt)
        sun = swe.calc_ut(jd, swe.SUN, FLAGS)[0][0]

        diff = abs(sun - natal_sun)

        if diff < min_diff:
            min_diff = diff
            best_dt = dt

        dt += timedelta(minutes=1)

    return best_dt


# -----------------------------
# GENERATE VARSHPHAL
# -----------------------------
def generate_varshphal(payload, dt_utc):
    dob = payload["dob"]
    time = payload["time"]
    lat = float(payload["lat"])
    lon = float(payload["lon"])
    year = int(payload["year"])

    # DOB split
    y, m, d = map(int, dob.split("-"))
    hh, mm = map(int, time.split(":"))
    utc_hour = hh + mm/60.0 - 5.5
    jd_birth = swe.julday(y, m, d, utc_hour)

    # Solar return
    dt_sr_utc = solar_return(dt_utc, year)
    jd_sr = julday(dt_sr_utc)

    houses = {str(i): [] for i in range(1, 13)}

    # -----------------------------
    # ASCENDANT (FIXED)
    # -----------------------------
    cusps, ascmc = swe.houses_ex(jd_sr, lat, lon, b'W')  # Whole Sign
    asc = ascmc[0]
    asc_sign = int(asc / 30)

    def get_house(lonp):
        sign = int(lonp / 30)
        return (sign - asc_sign + 12) % 12 + 1

    # -----------------------------
    # PLANETS
    # -----------------------------
    for p, name in PLANETS.items():
        lonp = swe.calc_ut(jd_sr, p, FLAGS)[0][0]
        house = get_house(lonp)
        houses[str(house)].append(name)

    # -----------------------------
    # RAHU / KETU
    # -----------------------------
    rahu = swe.calc_ut(jd_sr, swe.MEAN_NODE, FLAGS)[0][0]
    ketu = (rahu + 180) % 360

    houses[str(get_house(rahu))].append("Ra")
    houses[str(get_house(ketu))].append("Ke")

    # -----------------------------
    # ASCENDANT LABEL
    # -----------------------------
    houses["1"].append("La")

    return {
        "status": True,
        "year": year,
        "year_range": f"Sep {year} - Sep {year+1}",
        "houses": houses
    }


# -----------------------------
# MAIN
# -----------------------------
def main():
    try:
        payload = json.loads(sys.argv[1])

        # datetime parse
        tz = pytz.timezone(payload.get("timezone", "Asia/Kolkata"))

        dt_local = datetime.strptime(
            payload["dob"] + " " + payload["time"],
            "%Y-%m-%d %H:%M"
        )

        dt_local = tz.localize(dt_local)
        dt_utc = dt_local.astimezone(pytz.utc)

        # pass dt_utc
        result = generate_varshphal(payload, dt_utc)

        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({
            "status": False,
            "message": str(e)
        }))

if __name__ == "__main__":
    main()