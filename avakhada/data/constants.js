// avakhada/data/constants.js

const SIGN_LORD = {
    Aries: "Mars",
    Taurus: "Venus",
    Gemini: "Mercury",
    Cancer: "Moon",
    Leo: "Sun",
    Virgo: "Mercury",
    Libra: "Venus",
    Scorpio: "Mars",
    Sagittarius: "Jupiter",
    Capricorn: "Saturn",
    Aquarius: "Saturn",
    Pisces: "Jupiter"
};

//  App label match: Vipra == Brahmin
const VARNA_BY_SIGN = {
    Aries: "Kshatriya",
    Taurus: "Vaishya",
    Gemini: "Shoodra",
    Cancer: "Vipra",
    Leo: "Kshatriya",
    Virgo: "Vaishya",
    Libra: "Shoodra",
    Scorpio: "Vipra",
    Sagittarius: "Kshatriya",
    Capricorn: "Vaishya",
    Aquarius: "Shoodra",
    Pisces: "Vipra"
};

//  Keep your vashya mapping, but normalize spellings used by apps
const VASHYA_BY_SIGN = {
    Aries: "Chatushpada",
    Taurus: "Chatushpada",
    Gemini: "Maanav",
    Cancer: "Jalchar",
    Leo: "Vanachar",
    Virgo: "Maanav",
    Libra: "Maanav",
    Scorpio: "Keetak",
    Sagittarius: "Dwipad",
    Capricorn: "Chatushpada",
    Aquarius: "Maanav",
    Pisces: "Jalchar"
};

const TATVA_BY_SIGN = {
    Aries: "Fire",
    Leo: "Fire",
    Sagittarius: "Fire",
    Taurus: "Earth",
    Virgo: "Earth",
    Capricorn: "Earth",
    Gemini: "Air",
    Libra: "Air",
    Aquarius: "Air",
    Cancer: "Water",
    Scorpio: "Water",
    Pisces: "Water"
};

// Nakshatra order: used to derive nak_number if it isn’t passed in
const NAKSHATRA_ORDER = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati"
];

function getNakNumber(nakName) {
    if (!nakName) return null;
    const idx = NAKSHATRA_ORDER.indexOf(nakName);
    return idx >= 0 ? idx + 1 : null;
}

/**
 * =========================================================
 * 1) NADI (App mode)
 * =========================================================
 * Your evidence: “Magha charan 3 = Antya” in the authentic chart.
 * That means nadi must support charan-wise overrides.
 *
 * Add more nakshatras here as you verify from the authentic table/app.
 */
const NADI_BY_NAK_CHARAN_OVERRIDE = {
    //  Based on your message: Magha 3rd charan = Antya
    Magha: { 3: "Antya", 4: "Antya" }
};

function getNadiApp(nakName, charan, fallbackNadi) {
    const ov = NADI_BY_NAK_CHARAN_OVERRIDE[nakName];
    if (ov && ov[charan]) return ov[charan];
    return fallbackNadi || null;
}

/**
 * =========================================================
 * 2) YUNJA (App mode)
 * =========================================================
 * Apps show values like “Parbhaag”, so it cannot be only Adi/Madhya/Antya.
 * We use a base mapping + per-nakshatra overrides.
 */
const YUNJA_BY_CHARAN_BASE = {
    1: "Aadi",
    2: "Madhya",
    3: "Madhya",
    4: "Madhya"
};


const YUNJA_BY_NAK_CHARAN_OVERRIDE = {
    // Uttara Ashadha charan 4 => Parbhaag
    "Uttara Ashadha": { 4: "Parbhaag" }
};

function getYunjaApp(nakName, charan) {
    const ov = YUNJA_BY_NAK_CHARAN_OVERRIDE[nakName];
    if (ov && ov[charan]) return ov[charan];
    return YUNJA_BY_CHARAN_BASE[charan] || null;
}

/**
 * =========================================================
 * 3) PAYA (App mode)
 * =========================================================
 * There are multiple systems in astrology.
 * - Anuradha (17) charan 3 => Silver
 * - Uttara Ashadha (21) charan 4 => Copper
 *
 * We implement:
 *   (A) default = nakshatra-group method (commonly used)
 *   (B) per-nakshatra+charan overrides to match your target app
 */

// (A) Default by nakshatra number group:
// function payaByNakGroup(nakNumber) {
//     if (!Number.isFinite(nakNumber)) return null;
//     // Gold: 27 or 1-5, Silver: 6-15, Copper: 16-24, Iron: 25-26
//     if (nakNumber === 27 || (nakNumber >= 1 && nakNumber <= 5)) return "Gold";
//     if (nakNumber >= 6 && nakNumber <= 15) return "Silver";
//     if (nakNumber >= 16 && nakNumber <= 24) return "Copper";
//     if (nakNumber >= 25 && nakNumber <= 26) return "Iron";
//     return null;
// }


// const PAYA_BY_NAK_CHARAN_OVERRIDE = {
//     // Anuradha charan 3 => Silver
//     Anuradha: { 3: "Silver" }
//     // Uttara Ashadha will naturally become Copper from nak group (21 => Copper),
//     // so override not required, but you can add if needed.
// };

// function getPayaApp(nakName, charan, nakNumber) {
//     const ov = PAYA_BY_NAK_CHARAN_OVERRIDE[nakName];
//     if (ov && ov[charan]) return ov[charan];

//     // Default to group method (this matched your Uttara Ashadha => Copper)
//     return payaByNakGroup(nakNumber);
// }

const PAYA_BY_NAK_SERIAL = {
    Gold: new Set([1, 2, 3, 26, 27]),
    Silver: new Set([6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
    Copper: new Set([16, 17, 18, 19, 20, 21, 22, 23, 24, 25]),
    Iron: new Set([4, 5]),
};

/**
 * New rule: paya is decided ONLY by nakshatra serial number (1..27)
 * @param {number} nakNumber - nakshatra serial number (Ashwini=1 ... Revati=27)
 * @returns {"Gold"|"Silver"|"Copper"|"Iron"|null}
 */
function payaByNakSerial(nakNumber) {
    if (!Number.isFinite(nakNumber)) return null;

    if (PAYA_BY_NAK_SERIAL.Gold.has(nakNumber)) return "Gold";
    if (PAYA_BY_NAK_SERIAL.Silver.has(nakNumber)) return "Silver";
    if (PAYA_BY_NAK_SERIAL.Copper.has(nakNumber)) return "Copper";
    if (PAYA_BY_NAK_SERIAL.Iron.has(nakNumber)) return "Iron";

    // IMPORTANT:
    // Returning null makes it obvious something is missing in the rule.
    return null;
}

/**
 * Keep same signature if you want, but charan/nakName are no longer needed for paya.
 */
function getPayaApp(nakName, charan, nakNumber) {
    return payaByNakSerial(nakNumber);
}

/**
 * =========================================================
 * 4) NAME ALPHABET (App transliteration)
 * =========================================================
 * Your app-table syllables are shorter (Nu, Ji).
 * Target app uses long vowel spellings (Noo, Jee).
 */
const NAME_ALPHABET_OVERRIDE = {
    Anuradha: { 3: "Noo" },
    "Uttara Ashadha": { 4: "Jee" }
};

function getNameAlphabetApp(nakName, charan, fallbackArray) {
    if (NAME_ALPHABET_OVERRIDE?.[nakName]?.[charan]) {
        return NAME_ALPHABET_OVERRIDE[nakName][charan];
    }
    if (Array.isArray(fallbackArray)) {
        return fallbackArray[charan - 1] || null;
    }
    return null;
}

module.exports = {
    SIGN_LORD,
    VARNA_BY_SIGN,
    VASHYA_BY_SIGN,
    TATVA_BY_SIGN,

    getNakNumber,
    getNadiApp,
    getYunjaApp,
    getPayaApp,
    getNameAlphabetApp
};
