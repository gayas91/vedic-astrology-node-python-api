import swisseph as swe
import datetime
import json
import sys

# -----------------------------
# CONFIG
# -----------------------------
swe.set_ephe_path('./ephe')
swe.set_sid_mode(swe.SIDM_LAHIRI)

# -----------------------------
# CONSTANTS
# -----------------------------
RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE
}

# Element mapping
ELEMENT_MAP = {
    "Aries": "Fire", 
    "Leo": "Fire", 
    "Sagittarius": "Fire",
    "Taurus": "Earth", 
    "Virgo": "Earth", 
    "Capricorn": "Earth",
    "Gemini": "Air", 
    "Libra": "Air", 
    "Aquarius": "Air",
    "Cancer": "Water", 
    "Scorpio": "Water", 
    "Pisces": "Water"
}

# Weights (important for accuracy)
PLANET_WEIGHTS = {
    "Sun": 1.5,
    "Moon": 1.5,
    "Ascendant": 2.0,
    "Mars": 1.0,
    "Mercury": 1.0,
    "Jupiter": 1.0,
    "Venus": 1.0,
    "Saturn": 1.0,
    "Rahu": 0.5,
    "Ketu": 0.5
}

# -----------------------------
# UTILS
# -----------------------------
def julian_day(dt):
    return swe.julday(
        dt.year,
        dt.month,
        dt.day,
        dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    )


def get_rashi(longitude):
    longitude = longitude % 360
    return RASHIS[int(longitude / 30)]


# -----------------------------
# PLANET POSITIONS
# -----------------------------
def planet_positions(jd):
    positions = {}

    for name, planet in PLANETS.items():
        pos, _ = swe.calc_ut(jd, planet, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        positions[name] = pos[0] % 360

    # Ketu = Rahu + 180
    positions["Ketu"] = (positions["Rahu"] + 180) % 360

    return positions


# -----------------------------
# LAGNA
# -----------------------------
def get_lagna(jd, lat, lon):
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna = ascmc[0]
    return get_rashi(lagna)


# -----------------------------
# ELEMENT CALCULATION
# -----------------------------
def calculate_elements(jd, lat, lon):
    positions = planet_positions(jd)
    lagna = get_lagna(jd, lat, lon)

    element_score = {
        "Fire": 0,
        "Earth": 0,
        "Air": 0,
        "Water": 0
    }

    # Planets contribution
    for planet, lon in positions.items():
        rashi = get_rashi(lon)
        element = ELEMENT_MAP[rashi]
        weight = PLANET_WEIGHTS.get(planet, 1)

        element_score[element] += weight

    # Lagna contribution
    lagna_element = ELEMENT_MAP[lagna]
    element_score[lagna_element] += PLANET_WEIGHTS["Ascendant"]

    # Total
    total = sum(element_score.values())

    # Percentage
    element_percent = {
        k: round((v / total) * 100, 2)
        for k, v in element_score.items()
    }

    dominant = max(element_percent, key=element_percent.get)
    weakest = min(element_percent, key=element_percent.get)

    return {
        "elements": element_percent,
        "dominant": dominant,
        "weakest": weakest
    }


# -----------------------------
# MAIN
# -----------------------------
def main():
    payload = json.loads(sys.argv[1])

    dob = datetime.datetime.strptime(payload["dob"], "%Y-%m-%d")
    time = datetime.datetime.strptime(payload["time"], "%H:%M").time()

    lat = float(payload["lat"])
    lon = float(payload["lon"])

    # convert to UTC (India default)
    dt = datetime.datetime.combine(dob.date(), time) - datetime.timedelta(hours=5, minutes=30)

    jd = julian_day(dt)

    result = calculate_elements(jd, lat, lon)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()