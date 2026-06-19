import swisseph as swe

ZODIAC = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
    "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
    "Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
    "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati"
]

YOGAS = [
    "Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda",
    "Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva",
    "Vyaghata","Harshana","Vajra","Siddhi","Vyatipata","Variyana",
    "Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla",
    "Brahma","Indra","Vaidhriti"
]

TITHI_BASE = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami",
    "Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi",
    "Purnima"
]

SIGN_LORD = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter"
}

# 27 nakshatra lords cycle repeated 3 times
NAK_LORDS_CYCLE = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

def nakshatra_lord_by_no(nak_no: int) -> str:
    return NAK_LORDS_CYCLE[(nak_no - 1) % 9]

# Planet short strings for lagna_chart_ui
PLANET_SMALL_UI = {
    "SUN": "Su ",
    "MOON": "Mo ",
    "MARS": "Ma ",
    "MERCURY": "Me ",
    "JUPITER": "Ju ",
    "VENUS": "Ve ",
    "SATURN": "Sa ",
    "RAHU": "Ra ",
    "KETU": "Ke "
}

# D1 planets for lagna_chart_ui
PLANETS_D1 = [
    ("SUN", swe.SUN),
    ("MOON", swe.MOON),
    ("MARS", swe.MARS),
    ("MERCURY", swe.MERCURY),
    ("JUPITER", swe.JUPITER),
    ("VENUS", swe.VENUS),
    ("SATURN", swe.SATURN),
    ("RAHU", swe.MEAN_NODE)  # KETU derived
]

# Planets order for planets_detailed
PLANETS_ORDER = [
    (0, "Sun", swe.SUN),
    (1, "Moon", swe.MOON),
    (2, "Mars", swe.MARS),
    (3, "Mercury", swe.MERCURY),
    (4, "Jupiter", swe.JUPITER),
    (5, "Venus", swe.VENUS),
    (6, "Saturn", swe.SATURN),
    (7, "Rahu", swe.MEAN_NODE)  # Ketu derived
]
