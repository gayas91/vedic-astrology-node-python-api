import sys, json
from datetime import datetime
from sub_vdasha_calc import calc_sub_vdasha

DATE_FORMAT = "%d-%m-%Y %H:%M"

def main():
    data = json.loads(sys.argv[1])

    planet = data["planet"]

    if "start" not in data or not data["start"]:
        raise ValueError("start datetime is required for sub v-dasha")

    try:
        start = datetime.strptime(data["start"], DATE_FORMAT)
    except ValueError:
        raise ValueError(
            f"Invalid date format. Expected '{DATE_FORMAT}', got '{data['start']}'"
        )

    out = calc_sub_vdasha(planet, start)
    print(json.dumps(out, default=str))

if __name__ == "__main__":
    main()
