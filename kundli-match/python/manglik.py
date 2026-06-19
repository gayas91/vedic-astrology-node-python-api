import os
import json
import re

MANGlik_HOUSES = {1, 2, 4, 7, 8, 12}

# -----------------------------
# I18N (reads ../i18n/en.json, ../i18n/hi.json)
# -----------------------------
_I18N_CACHE = {}

def _safe_lang(lang: str) -> str:
    return "hi" if lang == "hi" else "en"

def _load_dict(lang="en"):
    safe = _safe_lang(lang)
    if safe in _I18N_CACHE:
        return _I18N_CACHE[safe]

    base_dir = os.path.dirname(os.path.abspath(__file__))  # kundli-match/python
    file_path = os.path.normpath(os.path.join(base_dir, "..", "i18n", f"{safe}.json"))

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            _I18N_CACHE[safe] = json.load(f)
    except Exception:
        _I18N_CACHE[safe] = {}

    return _I18N_CACHE[safe]

def t(key: str, lang="en", vars=None):
    if vars is None:
        vars = {}

    d = _load_dict(lang)
    en = _load_dict("en")

    s = d.get(key) or en.get(key) or key

    def repl(m):
        name = m.group(1)
        return str(vars.get(name, "{" + name + "}"))

    return re.sub(r"\{(\w+)\}", repl, str(s))

def t_or_default(key: str, default_text: str, lang="en", vars=None):
    """
    If translation key is missing, t() returns the key itself.
    In that case, return default_text so code never breaks.
    """
    out = t(key, lang, vars or {})
    return default_text if out == key else out


# -----------------------------
# Helpers
# -----------------------------
def house_name(n: int, lang="en") -> str:
    # Uses i18n keys house.1 ... house.12
    return t_or_default(f"house.{n}", _ordinal_en(n), lang)

def _ordinal_en(n: int) -> str:
    names = {
        1:"First",2:"Second",3:"Third",4:"Fourth",5:"Fifth",6:"Sixth",
        7:"Seventh",8:"Eighth",9:"Ninth",10:"Tenth",11:"Eleventh",12:"Twelfth"
    }
    return names.get(n, str(n))


# -----------------------------
# Core Logic
# -----------------------------
def eval_person(chart, lang="en"):
    house = chart["mars_house"]
    is_present = house in MANGlik_HOUSES

    based_on_house = []

    if is_present:
        # Hindi/English sentence via i18n
        default_en = f"Planet Mars is situated in {_ordinal_en(house)} house in your birth chart."
        based_on_house.append(
            t_or_default(
                "manglik.rule.planet_in_house",
                default_en,
                lang,
                {
                    "planet": t_or_default("planet.mars", "Mars", lang),
                    "house": house_name(house, lang)
                }
            )
        )
    else:
        default_en = "Planet Mars is not in Manglik houses (1,2,4,7,8,12) from Lagna."
        based_on_house.append(
            t_or_default(
                "manglik.rule.not_in_manglik_houses",
                default_en,
                lang,
                {"houses": "1,2,4,7,8,12"}
            )
        )

    pct = 25.0 if is_present else 0.0

    # Use your existing i18n keys if present (works with your current hi.json)
    manglik_report = (
        t_or_default(
            "manglik.report.effective",
            "Manglik Dosha is present and strong enough to matter. You are Manglik and should be cautious.",
            lang
        )
        if is_present else
        t_or_default(
            "manglik.report.not_present",
            "Manglik Dosha is not present from Lagna. So, you are not considered Manglik.",
            lang
        )
    )

    return {
        "manglik_present_rule": {
            "based_on_aspect": [],
            "based_on_house": based_on_house
        },
        "manglik_cancel_rule": [],
        "is_mars_manglik_cancelled": False,
        "manglik_status": "EFFECTIVE" if is_present else "INEFFECTIVE",
        "percentage_manglik_present": pct,
        "percentage_manglik_after_cancellation": pct,
        "manglik_report": manglik_report,
        "is_present": is_present
    }

def compute_manglik(male_chart, female_chart, lang="en"):
    male = eval_person(male_chart, lang=lang)
    female = eval_person(female_chart, lang=lang)

    match = (male["is_present"] == female["is_present"])

    if match:
        # Prefer your existing key if you want (you already have manglik.conclusion.match)
        report = t_or_default(
            "manglik.conclusion.match",
            "Both have similar Manglik status. Manglik consideration is balanced for this match.",
            lang
        )
    else:
        # These mismatch lines are not in your current hi.json, so we keep safe defaults.
        if male["is_present"] and not female["is_present"]:
            report = t_or_default(
                "manglik.conclusion.boy_manglik_girl_not",
                (
                    "The boy is Manglik. The girl is, however, not Manglik. "
                    "This mismatch can result in quarrels, differences in thinking, unnecessary tensions, etc. "
                    "Hence, this match is not recommended on basis of Manglik considerations."
                ),
                lang
            )
        elif female["is_present"] and not male["is_present"]:
            report = t_or_default(
                "manglik.conclusion.girl_manglik_boy_not",
                (
                    "The girl is Manglik. The boy is, however, not Manglik. "
                    "This mismatch can result in quarrels, differences in thinking, unnecessary tensions, etc. "
                    "Hence, this match is not recommended on basis of Manglik considerations."
                ),
                lang
            )
        else:
            report = t_or_default("manglik.conclusion.not_match", "Manglik mismatch found.", lang)

    return {
        "male": male,
        "female": female,
        "conclusion": {"match": match, "report": report}
    }