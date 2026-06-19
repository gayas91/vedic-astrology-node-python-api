# match.py
import sys, json, pytz
from datetime import datetime

from charts import build_birth_chart_minimal
from manglik import compute_manglik
from ashtakoot import compute_ashtakoot

def parse_dd_mm_yyyy(s):
    return datetime.strptime(s, "%d-%m-%Y")

def parse_time_ampm(s):
    return datetime.strptime(s.strip(), "%I:%M %p").time()

def build_person(payload, prefix):
    name = payload.get(prefix + "_name")
    dob = payload.get(prefix + "_dob")
    tob = payload.get(prefix + "_birth_time")
    lat = float(payload.get(prefix + "_lat"))
    lon = float(payload.get(prefix + "_long"))
    tz_offset = payload.get(prefix + "_timezone")
    pob = payload.get(prefix + "_pob")

    tz = pytz.timezone("Asia/Kolkata")

    d = parse_dd_mm_yyyy(dob)
    t = parse_time_ampm(tob)
    dt_local = tz.localize(datetime(d.year, d.month, d.day, t.hour, t.minute, 0))

    return {
        "name": name,
        "dob": dob,
        "birth_time": tob,
        "pob": pob,
        "lat": lat,
        "lon": lon,
        "timezone": tz_offset,
        "dt_local": dt_local,
        "tz": tz
    }

def main():
    payload = json.loads(sys.argv[1])
    lang = payload.get("language", "en")
    include_debug = bool(payload.get("include_debug", False))

    male = build_person(payload, "m")
    female = build_person(payload, "f")

    male_chart = build_birth_chart_minimal(male["dt_local"], male["lat"], male["lon"])
    female_chart = build_birth_chart_minimal(female["dt_local"], female["lat"], female["lon"])

    manglik = compute_manglik(male_chart, female_chart, lang=lang)

    # NEW: pass include_debug to ashtakoot 
    ashtkoot_data, asht_debug = compute_ashtakoot(male_chart, female_chart, lang=lang, include_debug=include_debug)

    out = {
        # "params": payload,
        "manglikDosha": manglik,
        # "ashtkootPoints": ashtkoot
        "ashtkootPoints": ashtkoot_data["points"],
        "rajjuDosha": ashtkoot_data["rajju_dosha"],
        "vedhaDosha": ashtkoot_data["vedha_dosha"]
    }

    if include_debug:
        out["debug"] = {
            "male_chart": male_chart,
            "female_chart": female_chart,
            "ashtakoot_debug": asht_debug
        }

    print(json.dumps(out))

if __name__ == "__main__":
    main()
