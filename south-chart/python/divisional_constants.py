SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_SHORT = {
    1: "Ar",
    2: "Ta",
    3: "Ge",
    4: "Cn",
    5: "Le",
    6: "Vi",
    7: "Li",
    8: "Sc",
    9: "Sg",
    10: "Cp",
    11: "Aq",
    12: "Pi"
}

PLANETS = [
    ("Sun", 0, "Su"),
    ("Moon", 1, "Mo"),
    ("Mercury", 2, "Me"),
    ("Venus", 3, "Ve"),
    ("Mars", 4, "Ma"),
    ("Jupiter", 5, "Ju"),
    ("Saturn", 6, "Sa")
]

NODES = [
    ("Rahu", "Ra"),
    ("Ketu", "Ke")
]

OPTIONAL_OUTER = [
    ("Uranus", 7, "Ur"),
    ("Neptune", 8, "Ne"),
    ("Pluto", 9, "Pl")
]

MOVABLE_SIGNS = {1, 4, 7, 10}
FIXED_SIGNS = {2, 5, 8, 11}
DUAL_SIGNS = {3, 6, 9, 12}

# South Indian fixed sign layout
# Row-wise 4x4, center 2x2 blank
SOUTH_LAYOUT = [
    [12, 1, 2, 3],
    [11, None, None, 4],
    [10, None, None, 5],
    [9, 8, 7, 6]
]

DIVISIONAL_TAB_ORDER = [
    "chalit",
    "sun",
    "moon",
    "D2",
    "D3",
    "D4",
    "D7",
    "D9",
    "D10",
    "D12",
    "D16",
    "D20",
    "D24",
    "D27",
    "D30",
    "D40",
    "D45",
    "D60"
]

DIVISIONAL_LABELS = {
    "lagna": "Lagna",
    "navamsa": "Navamsa",
    "transit": "Transit",
    "chalit": "Chalit",
    "sun": "Sun",
    "moon": "Moon",
    "D1": "Rasi (D-1)",
    "D2": "Hora (D-2)",
    "D3": "Drekkana (D-3)",
    "D4": "Chaturthamsa (D-4)",
    "D7": "Saptamsa (D-7)",
    "D9": "Navamsa (D-9)",
    "D10": "Dasamsa (D-10)",
    "D12": "Dwadasamsa (D-12)",
    "D16": "Shodasamsa (D-16)",
    "D20": "Vimsamsa (D-20)",
    "D24": "Chaturvimsamsa (D-24)",
    "D27": "Saptavimsamsa (D-27)",
    "D30": "Trimsamsa (D-30)",
    "D40": "Khavedamsa (D-40)",
    "D45": "Akshavedamsa (D-45)",
    "D60": "Shastiamsa (D-60)"
}