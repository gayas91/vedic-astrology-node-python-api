import sys, json
from datetime import datetime
from pratyantar_vdasha_calc import calc_pratyantar_vdasha

DATE_FORMAT = "%d-%m-%Y %H:%M"

def main():
    data = json.loads(sys.argv[1])

    maha = data["maha"]
    antar = data["antar"]

    if "start" not in data or not data["start"]:
        raise ValueError("start datetime is required for pratyantar v-dasha")

    try:
        start = datetime.strptime(data["start"], DATE_FORMAT)
    except ValueError:
        raise ValueError(
            f"Invalid date format. Expected '{DATE_FORMAT}', got '{data['start']}'"
        )

    out = calc_pratyantar_vdasha(maha, antar, start)
    print(json.dumps(out))

if __name__ == "__main__":
    main()
