import random
import json
from geopy.geocoders import Nominatim
from groq import Groq
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import sys


# -----------------------------------
# NAKSHATRA LIST WITH LORDS
# -----------------------------------

nakshatras = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

nakshatra_lords = {
    "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun",
    "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
    "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
    "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
    "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
    "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshtha": "Mercury",
    "Mula": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
    "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
    "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury"
}

signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Planet significations as per Brighu-Naadi
planet_significations = {
    "Sun": ["Father", "Government Honors", "Promotion", "Name and Fame", "Temple", "Medicine", "Leadership"],
    "Moon": ["Mother", "Foreign Travel", "Mind", "Restaurants", "Soft Nature", "Travels", "Water Bodies"],
    "Mars": ["Brothers", "Accidents", "Government Service", "Machinery", "Land", "Surgery", "Courage"],
    "Mercury": ["Education", "Intelligence", "Trade", "Law", "Business", "Languages", "Communication"],
    "Jupiter": ["Life Force", "Guru", "Religion", "Banking", "Philosophy", "Gains", "Children"],
    "Venus": ["Wife", "Riches", "Gold", "Marriage", "Vehicles", "Fine Arts", "Comfort"],
    "Saturn": ["Profession", "Karma", "Obstacles", "Delay", "Village Head", "Death", "Discipline"],
    "Rahu": ["Family Circle", "Roads", "Accidents", "Spirits", "Photography", "Fear", "Foreign"],
    "Ketu": ["Salvation", "Surgery", "Diseases", "Astrology", "Endings", "Doctors", "Spirituality"]
}

# Dasha periods (Vimshottari)
dasha_periods = {
    "Sun": 6, "Moon": 10, "Mars": 7, "Mercury": 17,
    "Jupiter": 16, "Venus": 20, "Saturn": 19, "Rahu": 18, "Ketu": 7
}


def get_sign(longitude):
    index = int(longitude / 30)
    return signs[index]


def get_nakshatra(longitude):
    index = int(longitude / 13.333333)
    nakshatra_name = nakshatras[index]
    return nakshatra_name, nakshatra_lords[nakshatra_name]


def get_nakshatra_pada(longitude):
    """Get nakshatra pada (1-4)"""
    nakshatra_start = int(longitude / 13.333333) * 13.333333
    position_in_nakshatra = longitude - nakshatra_start
    return int(position_in_nakshatra / 3.333333) + 1


def get_coordinates(place):
    geolocator = Nominatim(user_agent="astro_engine")
    location = geolocator.geocode(place)
    if location:
        return location.latitude, location.longitude
    return None, None


def generate_kundli(date, time, lat, lon):
    dt_obj = Datetime(date, time, '+05:30')
    pos = GeoPos(lat, lon)

    chart = Chart(dt_obj, pos, IDs=const.LIST_OBJECTS, hsys=const.HOUSES_WHOLE_SIGN)

    planets = [
        const.SUN, const.MOON, const.MARS, const.MERCURY,
        const.JUPITER, const.VENUS, const.SATURN,
        const.NORTH_NODE, const.SOUTH_NODE
    ]

    planet_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    kundli = {}
    ayanamsa = 24.1

    for i, p in enumerate(planets):
        obj = chart.get(p)
        sidereal_lon = (obj.lon - ayanamsa) % 360
        house = chart.houses.getHouseByLon(obj.lon)
        sign = get_sign(sidereal_lon)
        nakshatra_name, nakshatra_lord = get_nakshatra(sidereal_lon)
        nakshatra_pada = get_nakshatra_pada(sidereal_lon)

        kundli[planet_names[i]] = {
            "sign": sign,
            "house": int(house.id.replace("House", "")),
            "nakshatra": nakshatra_name,
            "nakshatra_lord": nakshatra_lord,
            "nakshatra_pada": nakshatra_pada,
            "longitude": round(sidereal_lon, 2)
        }

    asc = chart.get(const.ASC)
    asc_sidereal = (asc.lon - ayanamsa) % 360
    kundli["ASCENDANT"] = get_sign(asc_sidereal)

    return kundli


# -----------------------------------
# ENHANCED BRIGHU-NAADI INTERPRETATIONS
# -----------------------------------

def get_jupiter_interpretation(sign, house, nakshatra, nakshatra_lord):
    """Enhanced Brighu-Naadi Jupiter interpretations with timing"""
    base_text = {
        "Aries": "Ambitious person. Takes interest in Vedic studies and mantras.",
        "Taurus": "Born in rich family. Royal lifestyle indicated.",
        "Gemini": "Business-minded. Good life after 41 years.",
        "Cancer": "May face challenges. Life improves after 35.",
        "Leo": "Royal life. Will have name and fame.",
        "Virgo": "Highly intellectual and learned. Business minded.",
        "Libra": "May have enmity with own people. Gains from property.",
        "Scorpio": "Ambitious. Takes interest in Vedic studies.",
        "Sagittarius": "Forest life. Dual mentality. Good after 41.",
        "Capricorn": "Life develops in different place than birthplace.",
        "Aquarius": "Born near pilgrimage centre. May be wanderer.",
        "Pisces": "Spiritual life. Good after 41. May become preacher."
    }

    timing_text = {
        1: "Life will flourish in early years",
        2: "Wealth accumulation starts after 26",
        3: "Travel and courage develop after 27",
        4: "Property gains after 28",
        5: "Children and intelligence flourish after 29",
        6: "Health awareness needed after 30",
        7: "Marriage and partnerships after 31",
        8: "Transformations after 32",
        9: "Fortune and travels after 33",
        10: "Career peak after 34",
        11: "Gains and friends after 35",
        12: "Spiritual growth after 36"
    }

    result = base_text.get(sign, "Jupiter indicates life force")
    result += " " + timing_text.get(house, "Timing depends on Jupiter's transit")
    return result


def get_saturn_interpretation(sign, house, nakshatra, nakshatra_lord):
    """Enhanced Saturn interpretations with profession and timing"""
    profession_map = {
        "Aries": "Industrial unit, machinery sector, engineering",
        "Taurus": "Agriculture, banking, finance",
        "Gemini": "Trade, business, writing, teaching",
        "Cancer": "Aviation, restaurants, foreign service",
        "Leo": "Government service, administration, politics",
        "Virgo": "Legal profession, judiciary, consulting",
        "Libra": "Banking, gold trade, financial services",
        "Scorpio": "Iron and steel, chemicals, research",
        "Sagittarius": "Banking, teaching, religious institutions",
        "Capricorn": "Government service, liquor business, real estate",
        "Aquarius": "Technology, social work, innovation",
        "Pisces": "Medical field, juice business, spiritual work"
    }

    success_map = {
        1: "Self-made success",
        2: "Wealth through profession",
        3: "Recognition through communication",
        4: "Property from profession",
        5: "Creative success",
        6: "Success after struggles",
        7: "Partnership success",
        8: "Transformative career",
        9: "International success",
        10: "Peak career success",
        11: "Financial success",
        12: "Spiritual success"
    }

    result = f"Profession in {profession_map.get(sign, 'diverse field')}. "
    result += success_map.get(house, "Steady career growth")
    return result


def get_venus_interpretation(sign, house, jupiter_house, venus_in_jupiter_7th, nakshatra_lord):
    """Enhanced Venus interpretations with marriage timing"""
    marriage_age = {
        2: "24-25 years", 3: "26-27 years", 4: "15-16 years",
        5: "16-22 years", 6: "29-30 years", 7: "18-19 years",
        8: "20-21 years", 9: "22 years", 10: "22 years",
        11: "22-23 years", 12: "24-30 years"
    }

    if venus_in_jupiter_7th:
        marriage_text = "Early marriage indicated (18-22 years). Spouse from same community."
    else:
        marriage_text = f"Marriage around {marriage_age.get(house, '24-27')} years. When Jupiter transits Venus, marriage occurs."

    spouse_qualities = {
        "Aries": "energetic and independent",
        "Taurus": "stable and financially sound",
        "Gemini": "intelligent and communicative",
        "Cancer": "caring and family-oriented",
        "Leo": "proud and authoritative",
        "Virgo": "practical and organized",
        "Libra": "beautiful and artistic",
        "Scorpio": "passionate and intense",
        "Sagittarius": "adventurous and optimistic",
        "Capricorn": "ambitious and disciplined",
        "Aquarius": "unique and intellectual",
        "Pisces": "compassionate and spiritual"
    }

    result = marriage_text + f" Spouse will be {spouse_qualities.get(sign, 'compatible')}."
    return result


def get_rahu_ketu_interpretation(rahu_sign, ketu_sign, rahu_house, ketu_house):
    """Enhanced Rahu-Ketu interpretations from Brighu-Naadi"""
    direction_map = {
        ("Aries", "Libra"): "East to West",
        ("Taurus", "Scorpio"): "South to North",
        ("Gemini", "Sagittarius"): "East to West",
        ("Cancer", "Capricorn"): "South to North",
        ("Leo", "Aquarius"): "East to West",
        ("Virgo", "Pisces"): "South to North",
    }

    part_map = {
        "Aries": "Eastern", "Taurus": "Southern", "Gemini": "Western",
        "Cancer": "Northern", "Leo": "Eastern", "Virgo": "Southern",
        "Libra": "Western", "Scorpio": "Northern", "Sagittarius": "Eastern",
        "Capricorn": "Southern", "Aquarius": "Western", "Pisces": "Northern"
    }

    body_part_map = {
        "Aries": "head", "Taurus": "throat", "Gemini": "shoulders/arms",
        "Cancer": "chest/heart", "Leo": "stomach/spine", "Virgo": "abdomen",
        "Libra": "kidneys/lower back", "Scorpio": "reproductive organs",
        "Sagittarius": "thighs", "Capricorn": "knees", "Aquarius": "calves",
        "Pisces": "feet"
    }

    road = direction_map.get((rahu_sign, ketu_sign), "varies based on exact placement")
    part = part_map.get(rahu_sign, "Unknown")

    health_issue = f"May have health issues related to {body_part_map.get(rahu_sign, 'affected area')}."

    result = f"Born in {part} part of city. Road in front of house runs {road}. {health_issue}"
    return result


def get_mars_interpretation(house, sign, nakshatra_lord):
    """Enhanced Mars interpretations with Mangal Dosha details"""
    if house in [1, 2, 4, 7, 8, 12]:
        severity = "High" if house == 7 else "Medium"
        remedies = "Recite Hanuman Chalisa daily, fast on Tuesdays, offer red flowers to Hanuman, wear red coral after consultation"
        return f"Mangal Dosha ({severity}) in house {house}. Marriage may be delayed. {remedies}"

    brother_map = {
        3: "Younger brother(s) indicated",
        11: "Elder brother(s) indicated",
        5: "Brother in education field",
        10: "Brother in government service"
    }

    return brother_map.get(house, "Courageous and determined nature")


def get_moon_interpretation(house, sign, nakshatra_lord):
    """Enhanced Moon interpretations"""
    travel_indicator = ["Cancer", "Pisces", "Sagittarius", "Aquarius"]
    if sign in travel_indicator:
        return f"Moon in {sign} - Indicates foreign travels and pilgrimages. Will have connections with distant lands."

    mother_map = {
        4: "Close bond with mother",
        8: "Mother may have faced health challenges",
        12: "Mother is spiritual"
    }

    return mother_map.get(house, "Emotional and caring nature")


def get_mercury_interpretation(house, sign, nakshatra_lord):
    """Enhanced Mercury interpretations"""
    if sign in ["Gemini", "Virgo"]:
        field = "business/law" if sign == "Gemini" else "analytical/medical"
        return f"Mercury in {sign} - Highly intelligent. Education will be smooth. Excellence in {field} field."

    education_map = {
        2: "Good communication skills",
        4: "Higher education",
        5: "Creative intelligence",
        9: "Higher learning",
        10: "Professional expertise"
    }

    return education_map.get(house, "Intelligent and articulate")


def get_sun_interpretation(sign, house, nakshatra_lord):
    """Enhanced Sun interpretations"""
    temple_map = {
        "Aries": "Hanuman/Durga", "Taurus": "Laxmi", "Gemini": "Vishnu",
        "Cancer": "Snake God", "Leo": "Shiva", "Virgo": "Vishnu",
        "Libra": "Kanyakaparameshwari", "Scorpio": "Kali/Shakthi",
        "Sagittarius": "Ganesh/Saibaba", "Capricorn": "Byrava",
        "Aquarius": "water bodies", "Pisces": "ashram/cremation ground"
    }

    father_map = {
        1: "Father is influential",
        4: "Father's property",
        5: "Father is learned",
        9: "Father is spiritual",
        10: "Father is respected"
    }

    temple = temple_map.get(sign, "a temple")
    father = father_map.get(house, "Father's influence is significant")

    result = f"Born near {temple} temple. {father}. Will gain recognition through authority figures."
    return result




# -----------------------------------
# ENHANCED AI ANALYSIS
# -----------------------------------

def analyze_with_ai(kundli, birth_date_str, client):
    # Extract key positions
    jupiter = kundli.get("Jupiter", {})
    saturn = kundli.get("Saturn", {})
    venus = kundli.get("Venus", {})
    mars = kundli.get("Mars", {})
    rahu = kundli.get("Rahu", {})
    ketu = kundli.get("Ketu", {})
    sun = kundli.get("Sun", {})
    moon = kundli.get("Moon", {})
    mercury = kundli.get("Mercury", {})

    # Calculate Jupiter-centric houses
    jupiter_house = jupiter.get("house", 1)
    seventh_from_jupiter = ((jupiter_house + 6) % 12) or 12
    venus_house = venus.get("house", 0)
    venus_in_jupiter_7th = (venus_house == seventh_from_jupiter)

    # Calculate dasha
    # moon_nakshatra = (moon.get("nakshatra", "Ashwini"), moon.get("nakshatra_lord", "Ketu"))
    # moon_pada = moon.get("nakshatra_pada", 1)

    # Get enhanced interpretations
    jupiter_text = get_jupiter_interpretation(
        jupiter.get('sign', ''), jupiter_house,
        jupiter.get('nakshatra', ''), jupiter.get('nakshatra_lord', '')
    )
    saturn_text = get_saturn_interpretation(
        saturn.get('sign', ''), saturn.get('house', 0),
        saturn.get('nakshatra', ''), saturn.get('nakshatra_lord', '')
    )
    venus_text = get_venus_interpretation(
        venus.get('sign', ''), venus_house, jupiter_house,
        venus_in_jupiter_7th, venus.get('nakshatra_lord', '')
    )
    rahu_ketu_text = get_rahu_ketu_interpretation(
        rahu.get('sign', ''), ketu.get('sign', ''),
        rahu.get('house', 0), ketu.get('house', 0)
    )
    mars_text = get_mars_interpretation(
        mars.get('house', 0), mars.get('sign', ''),
        mars.get('nakshatra_lord', '')
    )
    moon_text = get_moon_interpretation(
        moon.get('house', 0), moon.get('sign', ''),
        moon.get('nakshatra_lord', '')
    )
    mercury_text = get_mercury_interpretation(
        mercury.get('house', 0), mercury.get('sign', ''),
        mercury.get('nakshatra_lord', '')
    )
    sun_text = get_sun_interpretation(
        sun.get('sign', ''), sun.get('house', 0),
        sun.get('nakshatra_lord', '')
    )

    # Identify yogas and doshas

    # prompt = f"""
    # You are a highly experienced Vedic astrologer using Brighu-Naadi system.

    # Your goal is to give a deeply relatable and accurate reading that makes the person feel understood.

    # STYLE:
    # - Talk like a real astrologer (not robotic)
    # - Speak directly using "you"
    # - Keep tone simple, personal and real
    # - Avoid complex or heavy English
    # - Avoid scary or medical sounding sentences
    # - Always make health lines soft, caring and calm
    # - Do not create fear, only gentle awareness

    # LANGUAGE RULE:
    # - Use very simple English (class 5 level)
    # - Use daily common words only
    # - Avoid hard words like:
    #   - regulation, tendency, vulnerability, imposter syndrome, perfectionist
    # - Use simple words like:
    #   - control emotions, habit, self doubt, confusion
    # - Keep sentences short (max 12–15 words)
    # - Make it feel like user's own thoughts

    # CONTENT:
    # - Only say things clearly visible from chart
    # - No generic lines
    # - Each point should feel real and relatable
    # - User should feel: "this is exactly me"
    # - Keep each point short (1–2 lines)

    # OUTPUT RULES:
    # - Give 8–10 positive points
    # - Give 8–10 negative points
    # - Each point must include:
    #   1. Real life feeling/pattern
    #   2. Simple astro reason (planet + house)
    # - Avoid repeating ideas

    # FORMAT (STRICT JSON ONLY):

    # {{
    #   "positive_points": [
    #     {{
    #       "point": "Simple real life pattern",
    #       "reason": "Simple astro reason",
    #       "cta": "Simple question"
    #     }}
    #   ],
    #   "negative_points": [
    #     {{
    #       "point": "Simple struggle",
    #       "reason": "Simple astro cause",
    #       "cta": "Simple question"
    #     }}
    #   ]
    # }}

    # CTA RULES (VERY IMPORTANT):
    # - Must be a QUESTION + "ask astrologer now"
    # - Max 8 words
    # - Very simple English
    # - Must feel personal and urgent

    # 👉 Format:
    # "[simple question]? ask astrologer now"

    # GOOD CTA:
    # - Why am I overthinking? ask astrologer now
    # - Why money problem today? ask astrologer now
    # - What should I do now? ask astrologer now
    # - Why feeling confused? ask astrologer now
    # - Is something wrong today? ask astrologer now

    # IMPORTANT:
    # - Do NOT skip "reason"
    # - Do NOT use hard English
    # - Keep everything simple and clear

    # BIRTH CHART:
    # {json.dumps(kundli, indent=2)}

    # INSIGHTS:
    # Jupiter: {jupiter_text}
    # Saturn: {saturn_text}
    # Venus: {venus_text}
    # Rahu-Ketu: {rahu_ketu_text}
    # Mars: {mars_text}
    # Moon: {moon_text}
    # Mercury: {mercury_text}
    # Sun: {sun_text}

    # Return ONLY JSON. No extra text.
    # """

    prompt = f"""
    You are a Vedic astrologer.

    Generate ONE short emotional astrology insight.

    RULES:
    - Very simple English
    - Max 15 words per line
    - Personal and relatable
    - No hard English
    - Must feel emotional

    Return STRICT JSON:

    {{
    "point": "...",
    "reason": "...",
    "cta": "Why this happening? ask astrologer now"
    }}

    BIRTH CHART:
    {json.dumps(kundli)}
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system",
             "content": "You are a professional Vedic astrologer expert in Brighu-Naadi system from the book by N. Srinivasan Shastry."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
        temperature=0.6
    )

    text = response.choices[0].message.content
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        analysis = json.loads(text)
        # Add yogas and doshas to the analysis
        return analysis
    except Exception as e:
        print(f"JSON parsing error: {e}")
        return {
            "positive_points": [
                {
                    "point": "You naturally think deeply before making important decisions",
                    "reason": "Strong Mercury influence gives analytical thinking",
                    "cta": "Want to use this strength more effectively?"
                }
            ],
            "negative_points": [
                {
                    "point": "You may feel confused about major life decisions at times",
                    "reason": "Moon in challenging position creates overthinking",
                    "cta": "Looking for clarity in this area?"
                }
            ]
        }


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

# -----------------------------------
# MAIN PROGRAM
# -----------------------------------
def parse_time_string(time_str):
    return datetime.datetime.strptime(time_str, "%H:%M").time()


def generate_full_analysis(dob, tob, lat, lon, client):
    # Kundli generate
    kundli = generate_kundli(dob, tob, lat, lon)

    # AI analysis
    analysis = analyze_with_ai(kundli, dob, client)

    # CTA fix
    def fix_cta(analysis):
        for section in ["positive_points", "negative_points"]:
            for item in analysis.get(section, []):
                cta = item.get("cta", "").lower()

                if "ask astrologer" not in cta:
                    cta = "What should I do now? ask astrologer now"

                cta = cta.replace(".", "").strip()

                if not cta.endswith("now"):
                    cta = cta + " now"

                item["cta"] = cta

        return analysis

    analysis = fix_cta(analysis)

    # Popup
    popup = get_popup_insight(analysis)

    return {
        "kundli": kundli,
        "analysis": analysis,
        "popup": popup
    }
 
def format_dob(dob):
    """Convert YYYY-MM-DD → YYYY/MM/DD"""
    return dob.replace("-", "/")

def main():
    payload = json.loads(sys.argv[1])

    groq_key = payload.get("groq_api_key")

    dob = payload["dob"]              # "1993/06/22"
    dob = format_dob(dob)
    tob = payload["birth_time"]       # "22:00"
    lat = float(payload["lat"])
    lon = float(payload["lon"])

    client = Groq(api_key=groq_key)

    result = generate_full_analysis(dob, tob, lat, lon, client)

    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()