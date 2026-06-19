// avakhada/js/avakhada.service.js
const { t } = require("../../i18n");
const en = require("../../i18n/en.json");
const hi = require("../../i18n/hi.json");

const nakTable = require("../data/nakshatra_table.json");
const {
    SIGN_LORD,
    VARNA_BY_SIGN,
    VASHYA_BY_SIGN,
    TATVA_BY_SIGN,

    // Helpers + overrides
    getNakNumber,
    getNadiApp,
    getYunjaApp,
    getPayaApp,
    getNameAlphabetApp,
} = require("../data/constants");

/* -----------------------------
  HELPERS
------------------------------ */
const TATVA_EN_TO_KEY = {
    Fire: "tatva.agni",
    Earth: "tatva.prithvi",
    Air: "tatva.vayu",
    Water: "tatva.jal",
    Space: "tatva.akasha",
};

const PAYA_EN_TO_KEY = {
    Gold: "paya.gold",
    Silver: "paya.silver",
    Copper: "paya.copper",
    Iron: "paya.iron",
};

const YUNJA_EN_TO_KEY = {
    Adhama: "yunja.adhama",
    Madhya: "yunja.madhya",
    Uttama: "yunja.uttama",
};

function safeLang(lang) {
    return lang === "hi" ? "hi" : "en";
}

// "Krishna-Paksha" -> "krishna_paksha"
function toKey(str = "") {
    return String(str)
        .trim()
        .toLowerCase()
        .replace(/&/g, "and")
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "");
}

// translate via i18n, fallback to original value if missing
function tr(prefix, value, lang) {
    if (value == null) return value;
    const key = `${prefix}.${toKey(value)}`;
    const out = t(key, lang);
    return out === key ? value : out;
}

//  Planet translate that supports SUN / SATURN / KETU etc (UPPERCASE) and TitleCase
function trPlanet(v, lang) {
    if (v == null) return v;
    const key = `planet.${toKey(String(v))}`; // "SUN" -> "planet.sun"
    const out = t(key, lang);
    return out === key ? v : out;
}

/**
 * Build reverse maps: hi-value -> en-value for a namespace
 * Example: "सिंह" -> "Leo" using rashi.* keys
 */
function buildHiToEnValueMap(namespacePrefix) {
    const map = new Map();

    for (const k of Object.keys(hi)) {
        if (!k.startsWith(namespacePrefix + ".")) continue;

        const hiVal = hi[k];
        const enVal = en[k];

        if (typeof hiVal === "string" && typeof enVal === "string") {
            map.set(hiVal.trim(), enVal.trim());
        }
    }
    return map;
}

// Reverse maps (Hindi value -> English value)
const HI_TO_EN_RASHI = buildHiToEnValueMap("rashi");
const HI_TO_EN_TITHI = buildHiToEnValueMap("tithi");
const HI_TO_EN_NAK = buildHiToEnValueMap("nakshatra");
const HI_TO_EN_YOG = buildHiToEnValueMap("yog");
const HI_TO_EN_KARAN = buildHiToEnValueMap("karan");

// Normalize a value to English if it looks like Hindi
function normalizeByMap(value, map) {
    if (!value || typeof value !== "string") return value;
    const v = value.trim();
    return map.get(v) || v;
}

// SIGN_LORD / VARNA_BY_SIGN may use different English key formats.
// Try a few common formats.
function normalizeSignForMaps(signEn) {
    if (!signEn || typeof signEn !== "string") return signEn;

    // direct hit
    if (SIGN_LORD[signEn] || VARNA_BY_SIGN[signEn] || VASHYA_BY_SIGN[signEn] || TATVA_BY_SIGN[signEn]) {
        return signEn;
    }

    // Try TitleCase: "leo" -> "Leo"
    const title = signEn.charAt(0).toUpperCase() + signEn.slice(1).toLowerCase();
    if (SIGN_LORD[title] || VARNA_BY_SIGN[title] || VASHYA_BY_SIGN[title] || TATVA_BY_SIGN[title]) {
        return title;
    }

    // Try key-like: "Leo" -> "leo"
    const lower = signEn.toLowerCase();
    if (SIGN_LORD[lower] || VARNA_BY_SIGN[lower] || VASHYA_BY_SIGN[lower] || TATVA_BY_SIGN[lower]) {
        return lower;
    }

    return signEn;
}

module.exports = function buildAvakhada({
    ascendant_sign,
    moon_sign,
    nak_name,
    nak_number,
    charan,
    tithi_name,
    karan_name,
    yog_name,

    //  lang support
    lang = "en",

    //  optional: choose vashya reference to match app if needed
    vashya_ref = "moon",
}) {
    const L = safeLang(lang);

    /* -----------------------------
      1) Normalize inputs back to EN for calculations
    ------------------------------ */
    let ascSignEn = normalizeByMap(ascendant_sign, HI_TO_EN_RASHI);
    let moonSignEn = normalizeByMap(moon_sign, HI_TO_EN_RASHI);

    // Normalize for internal maps
    ascSignEn = normalizeSignForMaps(ascSignEn);
    moonSignEn = normalizeSignForMaps(moonSignEn);

    const nakNameEn = normalizeByMap(nak_name, HI_TO_EN_NAK);
    const tithiNameEn = normalizeByMap(tithi_name, HI_TO_EN_TITHI);
    const yogNameEn = normalizeByMap(yog_name, HI_TO_EN_YOG);
    const karanNameEn = normalizeByMap(karan_name, HI_TO_EN_KARAN);

    // Now safe to read nakshatra table
    const nakRow = nakTable[nakNameEn];

    // Prefer computed nak_number from python; fallback derive from EN name
    const finalNakNumber =
        typeof nak_number === "number" && Number.isFinite(nak_number) ? nak_number : getNakNumber(nakNameEn);

    // Vashya reference selection
    const vashyaSignEn = vashya_ref === "ascendant" ? ascSignEn : moonSignEn;

    // App-compatible computed fields (use EN values)
    const nadiRaw = nakRow?.nadi || getNadiApp(nakNameEn, charan, nakRow?.nadi);
    const yunjaRaw = getYunjaApp(nakNameEn, charan);
    const payaRaw = getPayaApp(nakNameEn, charan, finalNakNumber);
    const nameAlphabetRaw = getNameAlphabetApp(nakNameEn, charan, nakRow?.name_alphabet);

    // Raw values from maps/tables (EN)
    const ascLordRaw = SIGN_LORD[ascSignEn] || null;
    const varnaRaw = VARNA_BY_SIGN[moonSignEn] || null;
    const vashyaRaw = VASHYA_BY_SIGN[vashyaSignEn] || null;
    const yoniRaw = nakRow?.yoni || null;
    const ganRaw = nakRow?.gan || null;
    const signLordRaw = SIGN_LORD[moonSignEn] || null;
    const nakLordRaw = nakRow?.nakshatra_lord || null;
    const tatvaRaw = TATVA_BY_SIGN[moonSignEn] || null;

    /* -----------------------------
      2) Localize output values (NO new keys added)
    ------------------------------ */
    const ascendant = tr("rashi", ascSignEn, L);
    const sign = tr("rashi", moonSignEn, L);

    //  Planets/lords: handle "SUN"/"KETU"/"SATURN" etc + translate to Hindi
    const ascendant_lord = trPlanet(ascLordRaw, L);
    const SignLord = trPlanet(signLordRaw, L);
    const NaksahtraLord = trPlanet(nakLordRaw, L);

    const Varna = tr("varna", varnaRaw, L);
    const Vashya = tr("vashya", vashyaRaw, L);
    const Yoni = tr("yoni", yoniRaw, L);
    const Gan = tr("gan", ganRaw, L);
    const Nadi = tr("nadi", nadiRaw, L);

    const Naksahtra = tr("nakshatra", nakNameEn, L);

    const Yog = tr("yog", yogNameEn, L);
    const Karan = tr("karan", karanNameEn, L);
    const Tithi = tr("tithi", tithiNameEn, L);

    //  tatva can be "Fire/Earth/Air/Water/Space" from constants
    const tatva =
        tatvaRaw && TATVA_EN_TO_KEY[tatvaRaw] ? t(TATVA_EN_TO_KEY[tatvaRaw], L) : tr("tatva", tatvaRaw, L);

    //  translate yunja + paya using mapping tables (no new keys in response)
    const yunja = yunjaRaw && YUNJA_EN_TO_KEY[yunjaRaw] ? t(YUNJA_EN_TO_KEY[yunjaRaw], L) : yunjaRaw;

    const paya = payaRaw && PAYA_EN_TO_KEY[payaRaw] ? t(PAYA_EN_TO_KEY[payaRaw], L) : payaRaw;

    const name_alphabet = nameAlphabetRaw;

    return {
        ascendant: ascendant,
        ascendant_lord: ascendant_lord,

        Varna: Varna,
        Vashya: Vashya,

        Yoni: Yoni,
        Gan: Gan,
        Nadi: Nadi,

        SignLord: SignLord,
        sign: sign,

        Naksahtra: Naksahtra,
        NaksahtraLord: NaksahtraLord,
        Charan: charan,

        Yog: Yog,
        Karan: Karan,
        Tithi: Tithi,

        yunja: yunja,
        tatva: tatva,

        name_alphabet: name_alphabet,
        paya: paya,
    };
};
