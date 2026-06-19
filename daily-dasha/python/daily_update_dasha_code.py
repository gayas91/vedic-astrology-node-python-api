import swisseph as swe
import datetime
import json
import sys
from groq import Groq
import random

from geopy.geocoders import Nominatim

swe.set_ephe_path('./ephe')
swe.set_sid_mode(swe.SIDM_LAHIRI)
SIDEREAL_YEAR = 365.25636

RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE
}

DASHA_SEQUENCE = [
    ("Ketu", 7),
    ("Venus", 20),
    ("Sun", 6),
    ("Moon", 10),
    ("Mars", 7),
    ("Rahu", 18),
    ("Jupiter", 16),
    ("Saturn", 19),
    ("Mercury", 17)
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

def julian_day(dt):
    return swe.julday(
        dt.year,
        dt.month,
        dt.day,
        dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    )


def get_rashi(longitude):
    longitude = longitude % 360
    return RASHIS[int(longitude / 30)]


def get_nakshatra(longitude):
    index = int(longitude / (360 / 27)) % 27
    return NAKSHATRAS[index]


def planet_positions(jd):
    positions = {}

    for name, planet in PLANETS.items():
        pos, _ = swe.calc_ut(jd, planet, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)

        positions[name] = pos[0] % 360

    positions["Ketu"] = (positions["Rahu"] + 180) % 360

    return positions


def get_lagna(jd, lat, lon):
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna = ascmc[0]
    return get_rashi(lagna)


def house_from_moon(moon_rashi, planet_rashi):
    moon_index = RASHIS.index(moon_rashi)
    planet_index = RASHIS.index(planet_rashi)
    return (planet_index - moon_index) % 12 + 1


def analyze_transit(moon_rashi, positions):
    positive = []
    negative = []

    saturn = get_rashi(positions["Saturn"])
    mars = get_rashi(positions["Mars"])
    jupiter = get_rashi(positions["Jupiter"])
    venus = get_rashi(positions["Venus"])
    rahu = get_rashi(positions["Rahu"])
    ketu = get_rashi(positions["Ketu"])

    jupiter_house = house_from_moon(moon_rashi, jupiter)
    venus_house = house_from_moon(moon_rashi, venus)
    saturn_house = house_from_moon(moon_rashi, saturn)
    mars_house = house_from_moon(moon_rashi, mars)

    #  POSITIVE (explained)
    if jupiter_house in [2, 5, 7, 9, 11]:
        positive.append(
            f"Jupiter is in house {jupiter_house}, which indicates growth, financial stability and support from luck. "
            "This is a good time for expansion, learning and making wise decisions."
        )

    if venus_house in [1, 2, 4, 5, 7, 9, 11]:
        positive.append(
            f"Venus is in house {venus_house}, bringing harmony in relationships, comfort and enjoyment. "
            "Good period for love, luxury and emotional satisfaction."
        )

    # NEGATIVE (explained)
    if saturn_house in [1, 2, 4, 8, 12]:
        negative.append(
            f"Saturn is in house {saturn_house}, which may bring delays, responsibilities and pressure. "
            "You may feel slow progress but patience and discipline will help."
        )

    if mars_house in [1, 4, 7, 8, 12]:
        negative.append(
            f"Mars is in house {mars_house}, indicating possible conflicts, anger or impulsive decisions. "
            "Avoid arguments and stay calm."
        )

    if rahu == moon_rashi:
        negative.append(
            "Rahu is influencing your Moon sign, which may create confusion, overthinking or sudden changes. "
            "Stay grounded and avoid risky decisions."
        )

    if ketu == moon_rashi:
        negative.append(
            "Ketu is influencing your Moon sign, which may bring detachment or lack of clarity. "
            "Focus on practical matters and avoid isolation."
        )

    return positive, negative

def generate_remedies(moon_rashi, positions, mahadasha):
    remedies = []

    saturn = get_rashi(positions["Saturn"])
    mars = get_rashi(positions["Mars"])
    rahu = get_rashi(positions["Rahu"])

    if saturn == moon_rashi or mahadasha == "Saturn":
        remedies.append(
            "Saturn influence is strong. Donate mustard oil on Saturdays and chant 'Om Sham Shanicharaya Namah'. "
            "This will reduce delays and mental pressure."
        )

    if mars == moon_rashi:
        remedies.append(
            "Mars is affecting your emotions. Read Hanuman Chalisa regularly and avoid anger. "
            "This will bring stability and courage."
        )

    if rahu == moon_rashi:
        remedies.append(
            "Rahu influence can create confusion. Worship Lord Shiva and practice meditation daily. "
            "This will bring clarity and control over thoughts."
        )

    if not remedies:
        remedies.append(
            "Overall planetary position is stable. Maintain discipline, positive thinking and consistency in actions."
        )

    return remedies

def generate_kundli(dob, time, lat, lon):
    birth_dt = datetime.datetime.combine(dob, time) - datetime.timedelta(hours=5, minutes=30)
    jd_birth = julian_day(birth_dt)
    planets = planet_positions(jd_birth)
    moon_long = planets["Moon"]
    moon_rashi = get_rashi(moon_long)
    nakshatra = get_nakshatra(moon_long)
    lagna = get_lagna(jd_birth, lat, lon)
    return lagna, moon_rashi, nakshatra


def get_planet_house(lagna_rashi, planet_rashi):
    lagna_index = RASHIS.index(lagna_rashi)
    planet_index = RASHIS.index(planet_rashi)
    return (planet_index - lagna_index) % 12 + 1


def check_manglik(lagna_rashi, mars_rashi):
    house = get_planet_house(lagna_rashi, mars_rashi)
    if house not in [1, 4, 7, 8, 12]:
        return False
    if mars_rashi in ["Aries", "Scorpio", "Capricorn"]:
        return False
    if lagna_rashi in ["Gemini", "Virgo"] and house == 2:
        return False
    if lagna_rashi in ["Aries", "Scorpio"] and house == 4:
        return False
    if lagna_rashi in ["Cancer", "Capricorn"] and house == 7:
        return False
    if lagna_rashi in ["Sagittarius", "Pisces"] and house == 8:
        return False
    return True


def generate_ai_interpretation(client, data):
    prompt = f"""
    You are a highly experienced Vedic astrologer using Brighu-Naadi principles.

    Your goal is to give a DAILY prediction based on transit + dasha.

    STYLE:
    - Talk like a real astrologer (not an app)
    - Use very simple and easy English
    - Keep tone personal and real
    - Make everything feel about TODAY (use "today", "right now")

    STRICT RULES:
    - No generic lines like "career is good"
    - Every line must feel real and specific
    - Write like the user is already feeling this TODAY
    - Do not repeat same pattern again and again

    TONE:
    - Do not sound 100% sure
    - Use:
      - "today you may feel"
      - "you might feel today"
      - "this can happen today"
    - Keep some lines strong for impact

    DEPTH RULE:
    Each point must include:
    1. What user is feeling TODAY
    2. Why (planet + house + dasha)
    3. Small impact on their day

    EXAMPLES:

    BAD:
    "You feel confident"

    GOOD:
    "Today you may feel people noticing you more, and you may try to speak more"

    BAD:
    "Money improving"

    GOOD:
    "Today money may come, but one sudden expense can also happen"

    LANGUAGE RULE:
    - Use very simple English (like daily speaking)
    - Use small and clear sentences
    - Avoid hard or formal words
    - Write like you are talking to a normal person

    CONTENT:
    - Mix emotions, work, money, relationships

    OUTPUT:
    - 6–8 positive
    - 6–8 negative

    CTA RULE (VERY IMPORTANT):
    - Short and clear
    - Max 6–7 words
    - Must create curiosity
    - Use simple English only
    - One line only (no \\n)

    👉 Format:
    "[problem]? Ask astrologer"

    GOOD CTA:
    - Why stress today? Ask astrologer
    - What should I do now? Ask astrologer
    - Why money issue today? Ask astrologer
    - Is this a warning? Ask astrologer
    - Can this be fixed? Ask astrologer

    FORMAT (STRICT JSON):

    {{
      "positive_points": [
        {{
          "point": "Simple easy English feeling",
          "reason": "Simple astro reason",
          "cta": "Short question"
        }}
      ],
      "negative_points": [
        {{
          "point": "User problem",
          "reason": "Astro cause",
          "cta": "Short question"
        }}
      ]
    }}

    ASTRO DATA:
    - Today Moon Rashi: {data['today_moon_rashi']}
    - Nakshatra: {data['today_nakshatra']}
    - Mahadasha: {data['mahadasha']}
    - Antardasha: {data['antardasha']}
    - Jupiter House: {data['jupiter_house']}
    - Saturn House: {data['saturn_house']}
    - Rahu Rashi: {data['rahu_rashi']}
    - Ketu Rashi: {data['ketu_rashi']}
    - Sade Sati: {data['sade_sati']}
    - Manglik: {data['manglik']}

    IMPORTANT:
    - Use only easy English
    - Make it feel real and about today
    - No Hindi at all
    - No \\n in CTA

    Return ONLY JSON.
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a Brighu-Naadi expert astrologer."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.6
        )

        text = response.choices[0].message.content
        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        print("AI Error:", e)
        return {"positive_points": [], "negative_points": []}

def fix_cta_format(analysis):
    for section in ["positive_points", "negative_points"]:
        for item in analysis.get(section, []):
            cta = item.get("cta", "").strip()

            # remove unwanted \n if model sends
            cta = cta.replace("\\n", " ")

            # ensure proper format
            if not cta.lower().endswith("ask astrologer"):
                if "?" in cta:
                    cta = cta.split("?")[0] + "? Ask astrologer"
                else:
                    cta = cta + "? Ask astrologer"

            item["cta"] = cta

    return analysis

def daily_prediction(dob, time, lat, lon, client):
    birth_dt = datetime.datetime.combine(dob, time) - datetime.timedelta(hours=5, minutes=30)
    lagna, moon_rashi, nakshatra = generate_kundli(dob, time, lat, lon)
    jd_birth = julian_day(birth_dt)
    birth_positions = planet_positions(jd_birth)
    moon_long = birth_positions["Moon"]
    md_data = get_current_mahadasha(birth_dt, moon_long)
    md_duration = calculate_duration(md_data["start"], md_data["end"])
    mahadasha = md_data["mahadasha"]
    md_start = md_data["start"]
    md_end = md_data["end"]
    ad_data = get_antardasha_full(mahadasha, md_start)
    ad_duration = calculate_duration(ad_data["start"], ad_data["end"])
    antardasha = ad_data["antardasha"]
    today = datetime.datetime.utcnow()
    jd_today = julian_day(today)
    positions = planet_positions(jd_today)
    positive, negative = analyze_transit(moon_rashi, positions)
    planet_messages = generate_planet_messages(moon_rashi, positions)
    saturn_rashi = get_rashi(positions["Saturn"])
    remedies = generate_remedies(moon_rashi, positions, mahadasha)
    sade_sati = check_sade_sati(moon_rashi, saturn_rashi)
    dasha_timeline = generate_dasha_timeline(birth_dt, moon_long)
    jupiter_rashi = get_rashi(positions["Jupiter"])
    saturn_rashi = get_rashi(positions["Saturn"])
    jupiter_house = house_from_moon(moon_rashi, jupiter_rashi)
    saturn_house = house_from_moon(moon_rashi, saturn_rashi)
    birth_mars_rashi = get_rashi(birth_positions["Mars"])
    manglik = check_manglik(lagna, birth_mars_rashi)
    today_moon_long = positions["Moon"]
    today_moon_rashi = get_rashi(today_moon_long)
    today_nakshatra = get_nakshatra(today_moon_long)
    rahu_rashi = get_rashi(positions["Rahu"])
    ketu_rashi = get_rashi(positions["Ketu"])
    rahu_house = house_from_moon(moon_rashi, rahu_rashi)
    ketu_house = house_from_moon(moon_rashi, ketu_rashi)
    # ai_analysis = generate_ai_interpretation(client, {
    #     "moon_rashi": moon_rashi,
    #     "nakshatra": nakshatra,
    #     "today_moon_rashi": today_moon_rashi,
    #     "today_nakshatra": today_nakshatra,
    #     "mahadasha": mahadasha,
    #     "antardasha": antardasha,
    #     "jupiter_house": jupiter_house,
    #     "saturn_house": saturn_house,
    #     "rahu_rashi": get_rashi(positions["Rahu"]),
    #     "ketu_rashi": get_rashi(positions["Ketu"]),
    #     "sade_sati": sade_sati,
    #     "manglik": manglik
    # })
    # ai_analysis = fix_cta_format(ai_analysis)
    # popup = get_popup_insight(ai_analysis)

    return {
        "ai_analysis": {}, #ai_analysis,
        "remedies": remedies,
        "date": str(today.date()),
        "moon_rashi": moon_rashi,
        "nakshatra": nakshatra,
        "today_moon_rashi": today_moon_rashi,
        "today_nakshatra": today_nakshatra,
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "planet_messages": planet_messages,
        "sade_sati": sade_sati,
        "manglik": manglik,
        "jupiter_house": jupiter_house,
        "saturn_house": saturn_house,
        "rahu_rashi": rahu_rashi,
        "ketu_rashi": ketu_rashi,
        "rahu_house": rahu_house,
        "ketu_house": ketu_house,
        "dasha_timeline": dasha_timeline,
        "positive": positive,
        "mahadasha_start": md_start,
        "mahadasha_end": md_end,
        "mahadasha_duration_years": md_data["duration_years"],
        "antardasha_start": ad_data["start"],
        "antardasha_end": ad_data["end"],
        "antardasha_duration_days": ad_data["duration_days"],
        "antardasha_duration_years": ad_data["duration_years"],
        "antardasha_duration_breakdown": ad_duration,
        "mahadasha_duration_breakdown": md_duration,
        "negative": negative,
        "popup": {} #popup,
    }


def calculate_vimshottari(moon_longitude):
    nak_deg = 13 + 20 / 60  # 13°20'
    nak_index = int(moon_longitude / nak_deg) % 27
    nak_lord = NAKSHATRA_LORDS[nak_index]
    position_in_nak = moon_longitude % nak_deg
    remaining_fraction = (nak_deg - position_in_nak) / nak_deg
    dasha_years = dict(DASHA_SEQUENCE)[nak_lord]
    balance_years = remaining_fraction * dasha_years
    return nak_lord, balance_years


def get_current_mahadasha(birth_date, moon_longitude):
    lord, balance = calculate_vimshottari(moon_longitude)

    dasha_order = [d[0] for d in DASHA_SEQUENCE]
    dasha_years = dict(DASHA_SEQUENCE)

    start_date = birth_date
    start_index = dasha_order.index(lord)

    years_passed = (datetime.datetime.utcnow() - start_date).days / 365.25

    current_index = start_index
    remaining = balance
    current_start = start_date

    while years_passed > remaining:
        years_passed -= remaining
        current_start += datetime.timedelta(days=remaining * SIDEREAL_YEAR)
        current_index = (current_index + 1) % 9
        remaining = dasha_years[dasha_order[current_index]]

    current_lord = dasha_order[current_index]
    current_end = current_start + datetime.timedelta(days=remaining * SIDEREAL_YEAR)

    return {
        "mahadasha": current_lord,
        "start": current_start,
        "end": current_end,
        "duration_years": remaining
    }


def get_antardasha_full(mahadasha, md_start_date):
    dasha_order = [d[0] for d in DASHA_SEQUENCE]
    dasha_years = dict(DASHA_SEQUENCE)

    md_years = dasha_years[mahadasha]
    elapsed_days = (datetime.datetime.utcnow() - md_start_date).days

    start_index = dasha_order.index(mahadasha)
    sequence = dasha_order[start_index:] + dasha_order[:start_index]

    current_start = md_start_date
    current_days = 0

    for planet in sequence:
        ad_years = (md_years * dasha_years[planet]) / 120
        ad_days = ad_years * SIDEREAL_YEAR

        start = current_start
        end = current_start + datetime.timedelta(days=ad_days)

        if elapsed_days < current_days + ad_days:
            return {
                "antardasha": planet,
                "start": start,
                "end": end,
                "duration_days": round(ad_days),
                "duration_years": round(ad_years, 2)
            }

        current_start = end
        current_days += ad_days


def calculate_duration(start, end):
    delta = end - start
    days = delta.days

    years = days // 365
    months = (days % 365) // 30
    remaining_days = (days % 365) % 30

    return {
        "years": years,
        "months": months,
        "days": remaining_days
    }



def check_sade_sati(moon_rashi, saturn_rashi):
    moon_index = RASHIS.index(moon_rashi)
    saturn_index = RASHIS.index(saturn_rashi)

    house = (saturn_index - moon_index) % 12 + 1

    if house == 12:
        return "First Phase (Start of Sade Sati)"

    elif house == 1:
        return "Second Phase (Peak Sade Sati)"

    elif house == 2:
        return "Third Phase (End Phase)"

    else:
        return "No Sade Sati"


def generate_dasha_timeline(birth_dt, moon_longitude):
    lord, balance = calculate_vimshottari(moon_longitude)
    dasha_order = [d[0] for d in DASHA_SEQUENCE]
    dasha_years = dict(DASHA_SEQUENCE)
    timeline = []
    current_lord = lord
    current_start = birth_dt
    remaining = balance
    timeline.append({
        "mahadasha": current_lord,
        "start": current_start.date(),
        "end": (current_start + datetime.timedelta(days=remaining * 365.25)).date()
    })
    current_start = current_start + datetime.timedelta(days=remaining * 365.25)
    index = dasha_order.index(current_lord)
    for i in range(1, 9):
        next_lord = dasha_order[(index + i) % 9]
        years = dasha_years[next_lord]
        end_date = current_start + datetime.timedelta(days=years * 365.25)
        timeline.append({
            "mahadasha": next_lord,
            "start": current_start.date(),
            "end": end_date.date()
        })
        current_start = end_date
    return timeline


def generate_planet_messages(moon_rashi, positions):
    messages = []
    jupiter = get_rashi(positions["Jupiter"])
    venus = get_rashi(positions["Venus"])
    saturn = get_rashi(positions["Saturn"])
    mars = get_rashi(positions["Mars"])
    rahu = get_rashi(positions["Rahu"])
    ketu = get_rashi(positions["Ketu"])
    jupiter_house = house_from_moon(moon_rashi, jupiter)
    venus_house = house_from_moon(moon_rashi, venus)
    saturn_house = house_from_moon(moon_rashi, saturn)
    mars_house = house_from_moon(moon_rashi, mars)
    if jupiter_house in [2, 5, 7, 9, 11]:
        messages.append("Jupiter is supporting growth, wisdom and opportunities.")
    if venus_house in [1, 2, 4, 5, 7, 9, 11]:
        messages.append("Venus is strengthening relationships and comforts.")
    if saturn_house in [1, 2, 4, 8, 12]:
        messages.append("Saturn influence may bring responsibilities and slow progress.")
    if mars_house in [1, 4, 7, 8, 12]:
        messages.append("Mars energy may create tension or impulsive actions.")
    if rahu == moon_rashi:
        messages.append("Rahu influence may create confusion or sudden changes.")
    if ketu == moon_rashi:
        messages.append("Ketu influence may bring detachment or spiritual thinking.")
    return messages

def get_popup_insight(analysis):
    negative = analysis.get("negative_points", [])
    positive = analysis.get("positive_points", [])

    # 70% chance → negative (high conversion)
    if negative and random.random() < 0.9:
        return random.choice(negative)

    # 30% → positive
    if positive:
        return random.choice(positive)

    return None

def get_lat_long(city, state, country="India"):
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.geocode(f"{city}, {state}, {country}")
    if location:
        lat = location.latitude
        lon = location.longitude
        return lat, lon
    else:
        return None, None

def parse_time_string(time_str):
    return datetime.datetime.strptime(time_str, "%H:%M").time()

def main():
    payload = json.loads(sys.argv[1])
    groq_key = payload.get("groq_api_key")
    dob = datetime.datetime.strptime(payload["dob"], "%Y-%m-%d").date()
    birth_time = parse_time_string(payload["birth_time"])
    lat = float(payload["lat"])
    lon = float(payload["lon"])

    client = Groq(api_key=groq_key)

    result = daily_prediction(dob, birth_time, lat, lon, client)
    # print(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()