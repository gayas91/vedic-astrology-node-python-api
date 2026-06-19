import os
import json
import re

_cache = {}

def _safe_lang(lang: str) -> str:
    return "hi" if lang == "hi" else "en"

def load(lang="en"):
    safe = _safe_lang(lang)

    # kundli-match/python/i18n.py  ->  kundli-match/i18n/hi.json
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "i18n", f"{safe}.json")
    file_path = os.path.normpath(file_path)

    if safe not in _cache:
        with open(file_path, "r", encoding="utf-8") as f:
            _cache[safe] = json.load(f)

    return _cache[safe]

def t(key: str, lang="en", vars=None):
    if vars is None:
        vars = {}

    d = load(lang)
    en = load("en")

    s = d.get(key) or en.get(key) or key

    # {var} replacement
    def repl(match):
        name = match.group(1)
        return str(vars.get(name, "{" + name + "}"))

    return re.sub(r"\{(\w+)\}", repl, str(s))