from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos


def format_date(dob):
    # Convert YYYY-MM-DD → DD/MM/YYYY
    parts = dob.split("-")
    return f"{parts[2]}/{parts[1]}/{parts[0]}"


def get_chart(dob, time, lat, lon):
    dob = format_date(dob)

    date = Datetime(dob, time)
    pos = GeoPos(lat, lon)

    chart = Chart(date, pos)
    return chart