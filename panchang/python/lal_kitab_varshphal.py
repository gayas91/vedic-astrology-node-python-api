import json
import os


def get_age(dob: str, year: int):
    birth_year = int(dob.split("-")[0])

    # Example:
    # 1988 -> 2026
    # age = 39

    return year - birth_year + 1


def get_lal_kitab_varshphal(lagna_chart, dob, year ):
    age = get_age(dob, year)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    table_file = os.path.join(
        current_dir,
        "data",
        "varshphalTable.json"
    )
    
    with open(table_file, "r", encoding="utf-8") as f:
        table = json.load(f)

    mapping = table[str(age)]

    # Empty 12 houses
    result = []

    for house in lagna_chart:
        result.append({
            "sign": house["sign"],
            "sign_name": house["sign_name"],
            "planet": [],
            "planet_small": [],
            "planet_degree": []
        })

    # Move planets according to age table
    for source_house in range(1, 13):

        target_house = mapping[str(source_house)]

        source = lagna_chart[source_house - 1]
        target = result[target_house - 1]

        target["planet"] = source["planet"]
        target["planet_small"] = source["planet_small"]
        target["planet_degree"] = source["planet_degree"]

    return {
        "age": age,
        "varshphal_chart": result
    }