import sys
import json
from utils import get_chart
from flatlib import const

# -----------------------------
# HOUSE CONSTANTS
# -----------------------------
HOUSES = [
    const.HOUSE1, const.HOUSE2, const.HOUSE3, const.HOUSE4,
    const.HOUSE5, const.HOUSE6, const.HOUSE7, const.HOUSE8,
    const.HOUSE9, const.HOUSE10, const.HOUSE11, const.HOUSE12
]

# -----------------------------
# CALCULATE BHAVBALA
# -----------------------------
def calculate_bhavbala(chart):
    bhav_strength = {}

    for idx, house_const in enumerate(HOUSES, start=1):
        try:
            house = chart.getHouse(house_const)

            # Dummy strength logic (UI-based scaling)
            strength = round(abs(house.lon % 30) / 2.5)

            bhav_strength[str(idx)] = strength

        except Exception as e:
            # Safe fallback (never crash API)
            bhav_strength[str(idx)] = 0

    return bhav_strength


# -----------------------------
# ANALYZE BHAVBALA
# -----------------------------
def analyze_bhavbala(data):
    analysis = {}

    for house, value in data.items():
        if value >= 9:
            text = (
                f"House {house} is very strong. You will experience strong growth, "
                f"confidence, and success in this area of life."
            )
        elif value >= 5:
            text = (
                f"House {house} has balanced strength. You will see steady and stable "
                f"results with consistent effort."
            )
        else:
            text = (
                f"House {house} is weak. You may face delays or struggles here, "
                f"and conscious effort is needed for improvement."
            )

        analysis[house] = text

    return analysis


# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    try:
        dob = sys.argv[1]
        time = sys.argv[2]
        lat = float(sys.argv[3])
        lon = float(sys.argv[4])

        chart = get_chart(dob, time, lat, lon)

        bhavbala = calculate_bhavbala(chart)
        analysis = analyze_bhavbala(bhavbala)

        print(json.dumps({
            "bhavbala": bhavbala,
            "analysis": analysis
        }))

    except Exception as e:
        # Always return valid JSON (important for Node.js)
        print(json.dumps({
            "error": str(e)
        }))