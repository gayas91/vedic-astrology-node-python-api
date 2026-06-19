import swisseph as swe
from datetime import datetime
from astro_constants import ZODIAC, NAKSHATRAS

def normalize(x: float) -> float:
    x = x % 360
    return x + 360 if x < 0 else x

def julday(dt_utc: datetime) -> float:
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )

def sign_index_from_deg(deg: float) -> int:
    return int(normalize(deg) / 30)

def sign_name_from_index(i: int) -> str:
    return ZODIAC[i % 12]

def to_sign_number(sign_index_0: int) -> int:
    return (sign_index_0 % 12) + 1

def deg_in_sign(deg: float) -> float:
    return normalize(deg) % 30

def compute_nak_charan(deg: float):
    nak_no = int(deg / 13.3333333333) + 1
    nak_name = NAKSHATRAS[nak_no - 1]
    nak_offset = deg % 13.3333333333
    charan = int(nak_offset / 3.3333333333) + 1
    return nak_no, nak_name, charan, nak_offset

def get_planet_awastha(norm_deg: float) -> str:
    if norm_deg < 6:
        return "Bala"
    if norm_deg < 12:
        return "Kumara"
    if norm_deg < 18:
        return "Yuva"
    if norm_deg < 24:
        return "Vridha"
    return "Mrityu"

def house_from_asc_sign(asc_sign_index0: int, planet_sign_index0: int) -> int:
    return ((planet_sign_index0 - asc_sign_index0) % 12) + 1
