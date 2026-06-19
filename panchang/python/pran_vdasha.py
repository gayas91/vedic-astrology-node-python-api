import sys, json
from datetime import datetime
from pran_vdasha_calc import calc_pran_vdasha

DATE_FORMAT = "%d-%m-%Y %H:%M"

def main():
    data = json.loads(sys.argv[1])

    maha = data["maha"]
    antar = data["antar"]
    praty = data["pratyantar"]
    sook = data["sookshma"]

    if "start" not in data or not data["start"]:
        raise ValueError("start datetime is required for pran v-dasha")

    try:
        start = datetime.strptime(data["start"], DATE_FORMAT)
    except ValueError:
        raise ValueError(
            f"Invalid date format. Expected '{DATE_FORMAT}', got '{data['start']}'"
        )

    out = calc_pran_vdasha(maha, antar, praty, sook, start)
    print(json.dumps(out))

if __name__ == "__main__":
    main()
