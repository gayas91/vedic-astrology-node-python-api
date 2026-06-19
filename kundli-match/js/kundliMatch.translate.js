const { t } = require("../../i18n");

function isKey(v) {
    return typeof v === "string" && v.includes(".");
}

function lc(v) {
    return String(v || "").trim().toLowerCase();
}

function translateManglikStatus(status, lang) {
    if (typeof status !== "string") return status;

    if (status.startsWith("manglik.")) return t(status, lang);

    const s = lc(status);
    if (s === "effective") return t("manglik.effective", lang);
    if (s === "cancelled" || s === "canceled") return t("manglik.cancelled", lang);
    if (s === "not_present" || s === "not present" || s === "absent") return t("manglik.not_present", lang);

    return status;
}

function mapAttributeToKey(val) {
    if (typeof val !== "string") return null;

    const raw = val.trim();
    const low = raw.toLowerCase();   //  normalize

    const map = {
        // nadi (support both spellings)
        "adi": "nadi.adi",
        "aadi": "nadi.adi",
        "madhya": "nadi.madhya",
        "antya": "nadi.antya",

        // varna
        "brahmin": "varna.brahmin",
        "kshatriya": "varna.kshatriya",
        "vaishya": "varna.vaishya",
        "shudra": "varna.shudra",

        // vashya (support jalchar/jalachar)
        "jalchar": "vashya.jalchar",
        "jalachar": "vashya.jalchar",
        "manav": "vashya.manav",
        "vanachar": "vashya.vanachar",
        "keet": "vashya.keet",
        "chatushpad": "vashya.chatushpad",

        // gan
        "rakshasa": "gan.rakshas",
        "rakshas": "gan.rakshas",
        "deva": "gan.dev",
        "dev": "gan.dev",
        "manushya": "gan.manushya",

        // planets (support uppercases like MOON)
        "sun": "planet.sun",
        "moon": "planet.moon",
        "mars": "planet.mars",
        "mercury": "planet.mercury",
        "jupiter": "planet.jupiter",
        "venus": "planet.venus",
        "saturn": "planet.saturn",
        "rahu": "planet.rahu",
        "ketu": "planet.ketu",

        // rashi
        "aries": "rashi.aries",
        "taurus": "rashi.taurus",
        "gemini": "rashi.gemini",
        "cancer": "rashi.cancer",
        "leo": "rashi.leo",
        "virgo": "rashi.virgo",
        "libra": "rashi.libra",
        "scorpio": "rashi.scorpio",
        "sagittarius": "rashi.sagittarius",
        "capricorn": "rashi.capricorn",
        "aquarius": "rashi.aquarius",
        "pisces": "rashi.pisces",

        // yoni
        "cat": "yoni.marjar",
        "marjar": "yoni.marjar"
    };

    return map[low] || null;
}

function translateNakshatraIfPossible(val, lang) {
    if (typeof val !== "string") return val;
    const slug = lc(val).replace(/\s+/g, "_");
    const key = `nakshatra.${slug}`;

    const translated = t(key, lang);
    if (translated !== key) return translated;

    return val;
}

function translateAttribute(val, lang) {
    if (typeof val !== "string") return val;

    if (isKey(val)) return t(val, lang);

    const mappedKey = mapAttributeToKey(val);
    if (mappedKey) return t(mappedKey, lang);

    return translateNakshatraIfPossible(val, lang);
}

function titleSuffixFromIndex(totalPoints) {
    const map = {
        1: "varna",
        2: "vashya",
        3: "tara",
        4: "yoni",
        5: "maitri",
        6: "gan",
        7: "bhakut",
        8: "nadi",
    };
    return map[Number(totalPoints)] || null;
}

/* ---------------------------------------
   NEW: Translate Python rule sentences
---------------------------------------- */
function houseWordToNumber(word) {
    const w = String(word || "").trim().toLowerCase();
    const map = {
        first: 1, second: 2, third: 3, fourth: 4, fifth: 5, sixth: 6,
        seventh: 7, eighth: 8, ninth: 9, tenth: 10, eleventh: 11,
        twelfth: 12,
        // python typo safety
        twefth: 12,
    };
    return map[w] || null;
}

function translateManglikRuleLine(line, lang) {
    if (typeof line !== "string") return line;

    // Pattern 1: "Planet Mars is situated in Fourth house in your birth chart."
    const m1 = line.match(/^Planet\s+Mars\s+is\s+situated\s+in\s+(\w+)\s+house\s+in\s+your\s+birth\s+chart\.$/i);
    if (m1) {
        const houseWord = m1[1];
        const houseNo = houseWordToNumber(houseWord);

        // Prefer i18n key if you added it; otherwise fallback to direct Hindi
        const key = "manglik.rule.planet_in_house";
        const maybe = t(key, lang, {
            planet: t("planet.mars", lang),
            house: houseNo ? t(`house.${houseNo}`, lang) : houseWord,
        });

        if (maybe !== key) return maybe;

        // Fallback Hindi (if you didn't add i18n keys yet)
        if (lang === "hi") {
            const h = houseNo ? t(`house.${houseNo}`, "hi") : houseWord;
            return `ग्रह ${t("planet.mars", "hi")} आपकी जन्म कुंडली के ${h} भाव में स्थित है।`;
        }

        return line;
    }

    // Pattern 2: "Planet Mars is not in Manglik houses (1,2,4,7,8,12) from Lagna."
    const m2 = line.match(/^Planet\s+Mars\s+is\s+not\s+in\s+Manglik\s+houses\s+\(([^)]+)\)\s+from\s+Lagna\.$/i);
    if (m2) {
        const houses = m2[1].trim();
        const key = "manglik.rule.not_in_manglik_houses";

        const maybe = t(key, lang, { houses });
        if (maybe !== key) return maybe;

        if (lang === "hi") return `ग्रह ${t("planet.mars", "hi")} लग्न से मांगलिक भावों (${houses}) में स्थित नहीं है।`;

        return line;
    }

    return line;
}

function translateManglikRulesBlock(obj, lang) {
    const rules = obj?.manglik_present_rule;
    if (!rules) return;

    if (Array.isArray(rules.based_on_house)) {
        rules.based_on_house = rules.based_on_house.map(x => translateManglikRuleLine(x, lang));
    }
    if (Array.isArray(rules.based_on_aspect)) {
        rules.based_on_aspect = rules.based_on_aspect.map(x => translateManglikRuleLine(x, lang));
    }
}

/* ---------------------------------------
   Main
---------------------------------------- */
module.exports = function translateMatchResponse(serviceResp, lang = "en") {
    const L = typeof lang === "string" ? lang : "en";

    // unwrap {status,data}
    const data =
        serviceResp && typeof serviceResp === "object" && serviceResp.data && typeof serviceResp.data === "object"
            ? serviceResp.data
            : serviceResp;

    if (!data || typeof data !== "object") return data;

    // ---------------- Manglik ----------------
    if (data.manglikDosha) {
        ["male", "female"].forEach(type => {
            const obj = data.manglikDosha[type];
            if (!obj) return;

            //  NEW: translate rule sentences from python
            translateManglikRulesBlock(obj, L);

            // status
            if (obj.manglik_status) obj.manglik_status = translateManglikStatus(obj.manglik_status, L);

            // report: standardize using i18n keys (already working for you)
            if (obj.is_present) {
                obj.manglik_report = obj.is_mars_manglik_cancelled
                    ? t("manglik.report.cancelled", L)
                    : t("manglik.report.effective", L);
            } else {
                obj.manglik_report = t("manglik.report.not_present", L);
            }
        });

        // conclusion
        if (data.manglikDosha.conclusion) {
            data.manglikDosha.conclusion.report = data.manglikDosha.conclusion.match
                ? t("manglik.conclusion.match", L)
                : t("manglik.conclusion.not_match", L);
        }
    }

    // ---------------- Ashtakoot ----------------
    if (Array.isArray(data.ashtkootPoints)) {
        const totalRow = data.ashtkootPoints.find(x => Number(x?.total_points) === 36) || null;
        const points = typeof totalRow?.received_points === "number" ? totalRow.received_points : "";

        data.ashtkootPoints.forEach(item => {
            if (!item || typeof item !== "object") return;

            // title
            if (typeof item.title === "string") {
                if (item.title.startsWith("ashtakoot.")) item.title = t(item.title, L);
                else {
                    const key = `ashtakoot.${lc(item.title)}`;
                    const tr = t(key, L);
                    if (tr !== key) item.title = tr;
                }
            }

            // description override
            const suffix = titleSuffixFromIndex(item.total_points);
            if (suffix) {
                const dk = `ashtakoot.desc.${suffix}`;
                const dtr = t(dk, L);
                if (dtr !== dk) item.description = dtr;
            }

            // attributes translate
            if (item.male_koot_attribute) item.male_koot_attribute = translateAttribute(item.male_koot_attribute, L);
            if (item.female_koot_attribute) item.female_koot_attribute = translateAttribute(item.female_koot_attribute, L);

            // total row title
            if (Number(item.total_points) === 36) item.title = t("ashtakoot.total", L);

            // conclusion row
            if (typeof item.status === "boolean") {
                item.title = t("ashtakoot.conclusion", L);
                item.report = item.status
                    ? t("ashtakoot.conclusion.pass", L, { points })
                    : t("ashtakoot.conclusion.fail", L, { points });
            }
        });
    }

    return data;
};