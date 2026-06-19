from ashtakavarga_constants import SIGNS

def normalize_deg(value):
    return value % 360.0

def sign_number_from_longitude(longitude):
    longitude = normalize_deg(longitude)
    return int(longitude // 30) + 1  # 1..12

def sign_name_from_number(sign_no):
    return SIGNS[sign_no - 1]

def wrap_sign(sign_no):
    return ((sign_no - 1) % 12) + 1

def move_sign(start_sign, houses_ahead):
    # houses_ahead is 1..12, counted inclusively in Jyotish style
    return wrap_sign(start_sign + houses_ahead - 1)

def empty_sign_map(default_value=0):
    return {i: default_value for i in range(1, 13)}

def sign_map_to_rows(sign_map):
    return [
        {
            "sign_no": sign_no,
            "sign": sign_name_from_number(sign_no),
            "value": sign_map[sign_no]
        }
        for sign_no in range(1, 13)
    ]

def build_north_indian_chart_rows(sign_map, asc_sign):
    # We keep sign-wise values and also expose house-wise layout from ascendant.
    # House 1 = asc sign, House 2 = next sign, ..., House 12 = previous sign.
    houses = []
    for house_no in range(1, 13):
        sign_no = move_sign(asc_sign, house_no)
        houses.append({
            "house": house_no,
            "sign_no": sign_no,
            "sign": sign_name_from_number(sign_no),
            "value": sign_map[sign_no]
        })
    return houses

def total_of_sign_map(sign_map):
    return sum(sign_map.values())

def build_sign_chart_from_map(sign_map):
    chart = []

    for sign_no in range(1, 13):
        chart.append({
            "sign": sign_no,
            "sign_name": sign_name_from_number(sign_no),
            "planet": [],            # empty (ashtakavarga me nahi hota)
            "planet_small": [],
            "planet_degree": [],
            "value": sign_map[sign_no]
        })

    return chart