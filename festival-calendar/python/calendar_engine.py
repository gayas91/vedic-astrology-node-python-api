import sys
import json
import ephem
import math
from datetime import datetime, timedelta, date
from fastapi import FastAPI
from geopy.geocoders import Nominatim
import holidays
from calendar import monthrange
import csv
import os

app = FastAPI()

from functools import lru_cache

@lru_cache(maxsize=10000)
def get_longitudes_cached(date_val, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = date_val

    moon = ephem.Moon(obs)
    sun = ephem.Sun(obs)

    moon.compute(obs)
    sun.compute(obs)

    return (
        math.degrees(ephem.Ecliptic(moon).lon),
        math.degrees(ephem.Ecliptic(sun).lon)
    )

def get_global_holidays(date_obj, country_code="IN"):
    try:
        country_holidays = holidays.country_holidays(country_code, years=date_obj.year)
        if date_obj in country_holidays:
            return country_holidays.get(date_obj)
    except Exception as e:
        print(f"Error: {e}")
        return None


# ================= CONSTANTS =================
VIKRAM_OFFSET = 57

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

YOGAS = [
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva",
    "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana",
    "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
    "Brahma", "Indra", "Vaidhriti"
]

RAHU = {0: "07:30-09:00", 1: "15:30-17:00", 2: "12:00-13:30", 3: "13:30-15:00", 4: "10:30-12:00", 5: "09:00-10:30",
        6: "06:00-07:30"}
YAMAGANDA = {0: "12:00-13:30", 1: "10:30-12:00", 2: "09:00-10:30", 3: "07:30-09:00", 4: "06:00-07:30", 5: "15:00-16:30",
             6: "13:30-15:00"}
GULIKA = {0: "15:00-16:30", 1: "07:30-09:00", 2: "06:00-07:30", 3: "13:30-15:00", 4: "10:30-12:00", 5: "12:00-13:30",
          6: "09:00-10:30"}


def get_moon_phase(observer):
    moon = ephem.Moon(observer)
    moon.compute(observer)
    phase = moon.phase
    return round(phase, 2)


# ================= LOCATION =================
def get_lat_long(city):
    geolocator = Nominatim(user_agent="astro_app")
    location = geolocator.geocode(city)
    if not location:
        raise ValueError("City not found")
    return location.latitude, location.longitude


def get_longitudes(observer):
    return get_longitudes_cached(observer.date, observer.lat, observer.lon)


def get_tithi(observer):
    moon_long, sun_long = get_longitudes(observer)
    elong = (moon_long - sun_long) % 360
    tithi_num = int(elong / 12) + 1

    names = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Poornima",
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
    ]

    return names[tithi_num - 1], tithi_num


def get_nakshatra(observer):
    moon = ephem.Moon(observer)
    moon.compute(observer)
    moon_long = math.degrees(ephem.Ecliptic(moon).lon)
    return int(moon_long / 13.3333) % 27


def get_yoga(observer):
    moon_long, sun_long = get_longitudes(observer)
    total = (moon_long + sun_long) % 360
    index = int(total / 13.3333) % 27
    return YOGAS[index], index + 1


# ================= SUNRISE/SUNSET =================
def get_sunrise(date_obj, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = ephem.Date(date_obj)

    sun = ephem.Sun(obs)
    sunrise = obs.next_rising(sun)

    return ephem.Date(sunrise).datetime()


def to_ist(dt):
    return dt + timedelta(hours=5, minutes=30)


def get_sunrise_sunset(date_obj, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = ephem.Date(date_obj)

    sun = ephem.Sun(obs)
    sunrise = obs.next_rising(sun)
    sunset = obs.next_setting(sun)

    sr = to_ist(ephem.Date(sunrise).datetime())
    ss = to_ist(ephem.Date(sunset).datetime())

    return sr.strftime("%I:%M %p"), ss.strftime("%I:%M %p")


# ================= TITHI END =================
def get_tithi_end_exact(date_obj, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)

    base = ephem.Date(get_sunrise(date_obj, lat, lon))
    obs.date = base

    prev_tithi = get_tithi(obs)[1]

    low = base
    high = base + 1  # next 1 day

    for _ in range(20):  # binary search
        mid = (low + high) / 2
        obs.date = mid

        curr = get_tithi(obs)[1]

        if curr == prev_tithi:
            low = mid
        else:
            high = mid

    dt = to_ist(ephem.Date(high).datetime())
    return dt.strftime("%I:%M:%S %p")


def get_tithi_start(date_obj, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)

    base = ephem.Date(get_sunrise(date_obj, lat, lon))
    obs.date = base

    curr_tithi = get_tithi(obs)[1]

    low = base - 1
    high = base

    for _ in range(20):
        mid = (low + high) / 2
        obs.date = mid

        t = get_tithi(obs)[1]

        if t == curr_tithi:
            high = mid
        else:
            low = mid

    dt = to_ist(ephem.Date(high).datetime())
    return dt.strftime("%I:%M:%S %p")


def get_tithi_duration(start, end):
    try:
        s = parse_time(start)
        e = parse_time(end)

        if e < s:
            e += timedelta(days=1)

        diff = e - s
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60

        return f"{hours}h {minutes}m"
    except Exception as e:
        print(f"Error: {e}")
        return ""


def get_lagna(observer):
    lst = observer.sidereal_time()
    deg = math.degrees(lst) % 360

    rashis = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    index = int(deg / 30)
    return rashis[index]


def get_choghadiya(sunrise_str, sunset_str, weekday):
    fmt = "%I:%M %p"
    sr = datetime.strptime(sunrise_str, fmt)
    ss = datetime.strptime(sunset_str, fmt)

    duration = (ss - sr) / 8

    names = ["Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"]

    result = []
    for i in range(8):
        start = sr + i * duration
        end = start + duration
        result.append(f"{names[i]} ({start.strftime('%H:%M')} - {end.strftime('%H:%M')})")

    return " | ".join(result)


def get_abhijit_muhurat(sunrise_str, sunset_str):
    fmt = "%I:%M %p"
    sr = datetime.strptime(sunrise_str, fmt)
    ss = datetime.strptime(sunset_str, fmt)

    total = (ss - sr).seconds / 2
    mid = sr + timedelta(seconds=total)

    start = mid - timedelta(minutes=24)
    end = mid + timedelta(minutes=24)

    return f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"


def get_bhadra_kaal(tithi_num, tithi_end):
    if tithi_num in [7, 8, 14, 29]:
        return f"Till {tithi_end}"
    return "No Bhadra"

def parse_time(t):
    for fmt in ("%I:%M:%S %p", "%I:%M %p"):
        try:
            return datetime.strptime(t, fmt)
        except:
            continue
    raise ValueError(f"Invalid time format: {t}")

# ================= HINDU MONTH (FIXED) =================
def get_hindu_month_accurate(date_obj, tithi_num=None):
    """
    Accurate Hindu month calculation with Adhik Masa support
    """
    date_str = date_obj.strftime("%Y-%m-%d")

    # Adhik Masa periods (extra months)
    adhik_masa_periods = {
        2026: {
            "Jyeshtha": ("2026-06-14", "2026-07-13")
        },
        2023: {
            "Ashadha": ("2023-06-19", "2023-07-17")
        },
        2025: {
            "Ashadha": ("2025-06-27", "2025-07-25")
        }
    }

    # Check if date falls in Adhik Masa
    if date_obj.year in adhik_masa_periods:
        for month_name, (start, end) in adhik_masa_periods[date_obj.year].items():
            if start <= date_str <= end:
                return f"Adhik {month_name}"

    # Define exact Hindu month start dates for 2026-2027
    month_ranges = {
        2026: [
            ("Phalguna", "2026-02-03", "2026-03-04"),
            ("Chaitra", "2026-03-05", "2026-04-03"),
            ("Vaishakha", "2026-04-04", "2026-05-03"),
            ("Jyeshtha", "2026-05-04", "2026-06-13"),
            ("Adhik Jyeshtha", "2026-06-14", "2026-07-13"),
            ("Ashadha", "2026-07-14", "2026-08-12"),
            ("Shravana", "2026-08-13", "2026-09-12"),
            ("Bhadrapada", "2026-09-13", "2026-10-11"),
            ("Ashvina", "2026-10-12", "2026-11-10"),
            ("Kartika", "2026-11-11", "2026-12-10"),
            ("Agrahayana", "2026-12-11", "2027-01-09"),
        ],
        2027: [
            ("Pausha", "2027-01-10", "2027-02-08"),
            ("Magha", "2027-02-09", "2027-03-10"),
            ("Phalguna", "2027-03-11", "2027-04-08"),
        ]
    }

    # Check which month this date falls into
    year = date_obj.year
    if year in month_ranges:
        for month_name, start_str, end_str in month_ranges[year]:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

            if start_date <= date_obj <= end_date:
                return month_name

    # Handle year boundary
    if date_obj.year == 2026 and date_obj.month == 12 and date_obj.day >= 11:
        return "Agrahayana"

    if date_obj.year == 2027 and date_obj.month == 1 and date_obj.day <= 9:
        return "Agrahayana"

    # Fallback to tithi-based calculation
    if tithi_num is not None:
        month_names = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
                       "Shravana", "Bhadrapada", "Ashvina", "Kartika",
                       "Agrahayana", "Pausha", "Magha", "Phalguna"]

        # Base on Gregorian month
        base_index = (date_obj.month - 1) % 12

        # Adjust based on tithi
        if tithi_num <= 15:  # Shukla Paksha
            month_index = base_index
        else:  # Krishna Paksha
            month_index = (base_index + 1) % 12

        return month_names[month_index]

    # Final fallback
    month_names = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
                   "Shravana", "Bhadrapada", "Ashvina", "Kartika",
                   "Agrahayana", "Pausha", "Magha", "Phalguna"]

    return month_names[(date_obj.month - 1) % 12]


def get_all_indian_holidays(date_obj):
    try:
        india_holidays = holidays.country_holidays("IN", years=date_obj.year)
        return india_holidays.get(date_obj)
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_world_holidays(date_obj):
    countries = ["IN", "US", "GB", "AE", "CA", "AU"]
    all_holidays = []

    for c in countries:
        try:
            h = holidays.country_holidays(c, years=date_obj.year)
            if date_obj in h:
                all_holidays.append(h.get(date_obj))
        except:
            continue

    return list(set(all_holidays))

def festival_engine(tithi, nak, month, date_obj, tithi_end, tithi_num, sunrise, sunset, lat, lon):
    festivals = []

    paksha = "Shukla" if tithi_num <= 15 else "Krishna"
    hindu_month = get_hindu_month_accurate(date_obj, tithi_num)

    def add(name):
        if name not in [f["name"] for f in festivals]:
            festivals.append({"name": name})


    # ================= CORE VRATS =================
    if tithi == "Ekadashi":
        add("Ekadashi Vrat")

    if tithi == "Pradosh" or tithi == "Trayodashi":
        add("Pradosh Vrat")

    if tithi == "Amavasya":
        add("Amavasya")

    if tithi == "Poornima":
        add("Purnima")

    # ================= ALL MAJOR FESTIVALS =================

    # CHAITRA
    if hindu_month == "Chaitra":
        if paksha == "Shukla" and tithi == "Pratipada":
            add("Ugadi / Gudi Padwa")
        if tithi == "Navami":
            add("Ram Navami")
        if tithi == "Poornima":
            add("Hanuman Jayanti")

    # VAISHAKHA
    if hindu_month == "Vaishakha":
        if tithi == "Tritiya":
            add("Akshaya Tritiya")
        if tithi == "Poornima":
            add("Buddha Purnima")

    # JYESHTHA
    if hindu_month == "Jyeshtha":
        if tithi == "Amavasya":
            add("Shani Jayanti")
        if tithi == "Poornima":
            add("Vat Savitri Vrat")

    # ASHADHA
    if hindu_month == "Ashadha":
        if tithi == "Ekadashi":
            add("Devshayani Ekadashi")
        if tithi == "Poornima":
            add("Guru Purnima")

    # SHRAVANA
    if hindu_month == "Shravana":
        if tithi == "Poornima":
            add("Raksha Bandhan")
        if tithi == "Chaturthi":
            add("Sankashti Chaturthi")

    # BHADRAPADA
    if hindu_month == "Bhadrapada":
        if tithi == "Chaturthi":
            add("Ganesh Chaturthi")
        if tithi == "Ashtami":
            add("Krishna Janmashtami")
        if tithi == "Chaturdashi":
            add("Anant Chaturdashi")

    # ASHVINA
    if hindu_month == "Ashvina":
        if paksha == "Shukla" and tithi == "Pratipada":
            add("Navratri Begins")
        if tithi == "Ashtami":
            add("Durga Ashtami")
        if tithi == "Navami":
            add("Maha Navami")
        if tithi == "Dashami":
            add("Dussehra")

    # KARTIKA (FIXED)
    if hindu_month == "Kartika":

        if tithi == "Amavasya":
            add("Diwali")

        if tithi == "Pratipada":
            add("Govardhan Puja")

            # NEXT DAY CHECK
            next_day = date_obj + timedelta(days=1)
            try:
                obs = ephem.Observer()
                obs.lat, obs.lon = str(lat), str(lon)
                obs.date = ephem.Date(get_sunrise(next_day, float(obs.lat), float(obs.lon)))
                if get_tithi(obs)[0] == "Dwitiya":
                    add("Bhai Dooj")
            except:
                pass

        if tithi == "Dwitiya":
            add("Bhai Dooj")

        if tithi == "Trayodashi":
            add("Dhanteras")

        if tithi == "Chaturdashi":
            add("Choti Diwali")

        if tithi == "Poornima":
            add("Dev Diwali")

    # PHALGUNA
    if hindu_month == "Phalguna":
        if tithi == "Chaturdashi":
            add("Maha Shivratri")
        if tithi == "Poornima":
            add("Holi")

    # ================= WEEKDAY BASED =================
    if date_obj.weekday() == 0:
        add("Somwar Vrat")
    if date_obj.weekday() == 5:
        add("Shani Vrat")

    # ================= NAKSHATRA =================
    if nak == 3:
        add("Rohini Vrat")

    # ================= GLOBAL HOLIDAYS =================
    all_holidays = set()

    for w in get_world_holidays(date_obj):
        all_holidays.add(w)

    govt = get_all_indian_holidays(date_obj)
    if govt:
        all_holidays.add(govt)

    for h in all_holidays:
        add(h)

    return festivals


# ================= API ENDPOINT =================
@app.get("/calendar")
def get_calendar(year: int, month: int, lat: float, lon: float):
    result = []
    days_in_month = monthrange(year, month)[1]
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    for day in range(1, days_in_month + 1):
        d = date(year, month, day)

        sunrise_utc = get_sunrise(d, lat, lon)


        obs.date = ephem.Date(sunrise_utc)

        tithi, tithi_num = get_tithi(obs)
        hindu_month = get_hindu_month_accurate(d, tithi_num)
        nak = get_nakshatra(obs)
        yoga, yoga_num = get_yoga(obs)

        tithi_start = get_tithi_start(d, lat, lon)
        tithi_end = get_tithi_end_exact(d, lat, lon)
        tithi_duration = get_tithi_duration(tithi_start, tithi_end)
        moon_phase = get_moon_phase(obs)
        lagna = get_lagna(obs)
        sunrise, sunset = get_sunrise_sunset(d, lat, lon)

        choghadiya = get_choghadiya(sunrise, sunset, d.weekday())

        festivals = festival_engine(
            tithi, nak, d.month, d, tithi_end, tithi_num, sunrise, sunset, lat, lon
        )

        vikram = year + VIKRAM_OFFSET if d.month >= 4 else year + 56

        result.append({
            "Date": str(d),
            "Day": d.strftime("%A"),
            "Hindu Month": hindu_month,

            "Tithi": tithi,
            "Tithi Start": tithi_start,
            "Tithi End": tithi_end,

            "Paksha": "Shukla-Paksha" if tithi_num <= 15 else "Krishna-Paksha",

            "Sunrise": sunrise,
            "Sunset": sunset,

            "Festivals": [f["name"] for f in festivals]  # clean list
        })

    return result


# ================= CSV GENERATION =================
def save_calendar_to_csv(data, filename):
    """Save calendar data to CSV file"""
    if not data:
        print("⚠️ No data to save")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Date", "Day", "Hindu Month",
            "Tithi", "Tithi Start", "Tithi End",
            "Paksha", "Sunrise", "Sunset", "Festivals"
        ])

        # Data rows
        for row in data:
            festivals_str = " | ".join(row["Festivals"]) if row["Festivals"] else ""

            writer.writerow([
                row["Date"],
                row["Day"],
                row["Hindu Month"],
                row["Tithi"],
                row["Tithi Start"],
                row["Tithi End"],
                row["Paksha"],
                row["Sunrise"],
                row["Sunset"],
                festivals_str
            ])

    print(f" CSV saved: {filename}")
    print(f"📊 Total rows: {len(data)}")


def generate_calendar_for_year(year, lat, lon, output_dir="calendars"):
    """Generate CSV for all months of a year"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for month in range(1, 13):
        print(f"📅 Generating {year}-{month:02d}...")
        data = get_calendar(year, month, lat, lon)
        filename = f"{output_dir}/{year}_{month:02d}_calendar.csv"
        save_calendar_to_csv(data, filename)

    print(f"\n All {year} calendars saved to '{output_dir}/' folder")


def main():
    try:
        # Agar JSON input diya gaya hai (sys.argv)
        if len(sys.argv) > 1:
            payload = json.loads(sys.argv[1])

            year = int(payload["year"])
            month = int(payload["month"])
            lat = float(payload["lat"])
            lon = float(payload["lon"])

            data = get_calendar(year, month, lat, lon)

            print(json.dumps({
                "status": "success",
                "data": data
            }, ensure_ascii=False))

        else:
            # 👉 CLI MODE (interactive)
            print("=" * 70)
            print("🕉️  HINDU CALENDAR GENERATOR - CSV OUTPUT")
            print("=" * 70)

            city = input("Enter city name (default: New Delhi): ").strip() or "New Delhi"

            try:
                lat, lon = get_lat_long(city)
                print(f"📍 Location: {city} ({lat:.4f}, {lon:.4f})")
            except:
                print("⚠️ Using default coordinates for New Delhi")
                lat, lon = 28.6139, 77.2090

            print("\nChoose an option:")
            print("1. Generate calendar for a specific month")
            print("2. Generate calendar for full year 2026")

            choice = input("\nEnter choice (1 or 2): ").strip()

            if choice == "1":
                year = int(input("Enter year (e.g., 2026): "))
                month = int(input("Enter month (1-12): "))

                print(f"\n📅 Generating calendar for {year}-{month:02d}...")
                data = get_calendar(year, month, lat, lon)

                filename = f"{year}_{month:02d}_calendar.csv"
                save_calendar_to_csv(data, filename)

            elif choice == "2":
                generate_calendar_for_year(2026, lat, lon)

            else:
                print("Invalid choice")

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }))


if __name__ == "__main__":
    main()