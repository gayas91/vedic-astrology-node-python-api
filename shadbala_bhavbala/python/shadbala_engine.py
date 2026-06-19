import sys
import json
from utils import get_chart
from flatlib import const

PLANETS = [
    const.SUN,
    const.MOON,
    const.MARS,
    const.MERCURY,
    const.JUPITER,
    const.VENUS,
    const.SATURN
]

def calculate_shadbala(chart):
    result = {}

    for planet in PLANETS:
        obj = chart.getObject(planet)

        # Dummy scoring logic (replace later with real shadbala calc if needed)
        strength = round(abs(obj.lon % 30) / 5)

        result[planet] = strength

    return result


def analyze_shadbala(data):
    analysis = {}

    for planet, value in data.items():
        if value >= 6:
            text = f"{planet} is very strong. You will feel confident and supported in areas ruled by this planet."
        elif value >= 4:
            text = f"{planet} has moderate strength. Results will come with some effort."
        else:
            text = f"{planet} is weak. You may face challenges and need improvement in this area."

        analysis[planet] = text

    return analysis


if __name__ == "__main__":
    dob = sys.argv[1]
    time = sys.argv[2]
    lat = float(sys.argv[3])
    lon = float(sys.argv[4])

    chart = get_chart(dob, time, lat, lon)

    shadbala = calculate_shadbala(chart)
    analysis = analyze_shadbala(shadbala)

    print(json.dumps({
        "shadbala": shadbala,
        "analysis": analysis
    }))