// horoscopeEngine.js
const crypto = require("crypto");
const { getAspect } = require("./aspects");
const { getHouse } = require("./house");
const categoryRules = require("./categoryRules");

/* -----------------------------
  LANGUAGE LOADER
------------------------------ */
function loadLang(lang = "en") {
    return {
        meanings: require(`./lang/${lang}/planetMeaning`),
        textBank: require(`./lang/${lang}/textBank`),
        houseMeaning: require(`./lang/${lang}/houseMeaning`),
        names: require(`./lang/${lang}/names`),
        intros: require(`./lang/${lang}/intros`)
    };
}

/* -----------------------------
  DAILY DATE KEY (UTC safe)
------------------------------ */
function getDateKey(dateObj = new Date()) {
    const d = dateObj;
    return `${d.getUTCFullYear()}-${d.getUTCMonth() + 1}-${d.getUTCDate()}`;
}

/* -----------------------------
  SEEDED RANDOM ENGINE
------------------------------ */
function createSeededRandom(seed) {
    let hash = crypto.createHash("sha256").update(seed).digest("hex");
    let index = 0;

    return function () {
        if (index + 8 > hash.length) {
            hash = crypto.createHash("sha256").update(hash).digest("hex");
            index = 0;
        }
        const part = hash.substring(index, index + 8);
        index += 8;
        return parseInt(part, 16) / 0xffffffff;
    };
}

/* ---- multi-entropy random ---- */
function subRand(seed, salt) {
    return createSeededRandom(seed + "::" + salt);
}

function pick(arr, rand) {
    if (!Array.isArray(arr) || arr.length === 0) return "";
    return arr[Math.floor(rand() * arr.length)];
}

/* -----------------------------
  ASPECT → TONE
------------------------------ */
function getTone(aspect) {
    if (aspect === "conjunction" || aspect === "trine") return "good";
    if (aspect === "opposition" || aspect === "square") return "bad";
    return "strong";
}

/* -----------------------------
  SCOPE FIXER (remove "today" for week/month/year)
------------------------------ */
function applyScope(text, period, lang) {
    if (!text || !period || period === "day") return text;

    // Hindi
    if (lang === "hi") {
        if (period === "week") return text.replaceAll("आज", "इस सप्ताह");
        if (period === "month") return text.replaceAll("आज", "इस महीने");
        if (period === "year") return text.replaceAll("आज", "इस साल");
        return text;
    }

    // English
    if (period === "week") return text.replaceAll("Today", "This week").replaceAll("today", "this week");
    if (period === "month") return text.replaceAll("Today", "This month").replaceAll("today", "this month");
    if (period === "year") return text.replaceAll("Today", "This year").replaceAll("today", "this year");
    return text;
}

/* -----------------------------
  NORMALIZE 4TH ARG
  Supports:
  - generateHoroscope(sign, planets, lang, Date)
  - generateHoroscope(sign, planets, lang, { period, date })
------------------------------ */
function normalizeOptions(arg4) {
    if (!arg4 || arg4 instanceof Date) {
        return { period: "day", forDate: arg4 || new Date() };
    }

    const period = typeof arg4.period === "string" ? arg4.period : "day";
    const forDate =
        arg4.date instanceof Date
            ? arg4.date
            : arg4.forDate instanceof Date
                ? arg4.forDate
                : new Date();

    return { period, forDate };
}

/* -----------------------------
  GET TONE ARRAY WITH FALLBACKS
------------------------------ */
function getToneArray(textBank, category, tone, lang) {
    let toneArr =
        textBank?.[category]?.[tone] ||
        textBank?.[tone] ||
        textBank?.default?.[tone] ||
        textBank?.default ||
        [];

    if (!Array.isArray(toneArr) || toneArr.length === 0) {
        toneArr =
            lang === "hi"
                ? ["अभी धैर्य रखें और सही दिशा में लगातार प्रयास करें।"]
                : ["Stay steady and keep moving in the right direction."];
    }
    return toneArr;
}

/* -----------------------------
  BUILD ONE CATEGORY
------------------------------ */
function buildParagraph(sign, category, planets, langData, seed, lang, period = "day") {
    const { meanings, textBank, houseMeaning, intros } = langData;
    const usedPlanets = categoryRules?.[category];

    // If category mapping missing, return fallback
    if (!Array.isArray(usedPlanets) || usedPlanets.length === 0) {
        return lang === "hi"
            ? "स्थितियों को समझकर सोच-समझकर कदम उठाएँ।"
            : "Take thoughtful steps after understanding the situation.";
    }

    const sentences = [];
    const usedToneLines = new Set();

    const baseRand = createSeededRandom(seed);
    const stopSign = lang === "en" ? "." : "।";

    /* Intro */
    if (intros?.[category]) {
        const intro = pick(intros[category], baseRand);
        if (intro) sentences.push(applyScope(intro, period, lang));
    }

    /* shuffle planets */
    const shuffled = [...usedPlanets].sort(() => baseRand() - 0.5);
    const dropIndex = Math.floor(baseRand() * shuffled.length);

    for (let i = 0; i < shuffled.length; i++) {
        if (i === dropIndex) continue;

        const planet = shuffled[i];
        const pos = planets?.[planet];
        if (!pos) continue;

        const house = getHouse(pos, sign);
        const aspect = getAspect(pos, planets.Moon);
        const tone = getTone(aspect);

        /* 🧠 multi-seed entropy */
        const houseRand = subRand(seed, "house-" + house + "-" + planet);
        const planetRand = subRand(seed, "planet-" + planet);
        const toneRand = subRand(seed, "tone-" + tone + "-" + i);

        const houseArr = houseMeaning?.[house] || [];
        const planetArr = meanings?.[planet] || [];

        const houseText = (pick(houseArr, houseRand) || "").trim();
        const planetText = (pick(planetArr, planetRand) || "").trim();

        const toneArr = getToneArray(textBank, category, tone, lang);

        let toneText = (pick(toneArr, toneRand) || "").trim();
        toneText = applyScope(toneText, period, lang).trim();

        let safety = 0;
        while (usedToneLines.has(toneText) && safety < 10) {
            toneText = (pick(toneArr, toneRand) || "").trim();
            toneText = applyScope(toneText, period, lang).trim();
            safety++;
        }
        usedToneLines.add(toneText);

        const left = `${houseText} ${planetText}`.trim();
        const right = toneText;

        if (left && right) sentences.push(`${left}${stopSign} ${right}`);
        else if (right) sentences.push(right);
    }

    if (sentences.length === 0) {
        return lang === "hi"
            ? "स्थितियों को समझकर सोच-समझकर कदम उठाएँ।"
            : "Take thoughtful steps after understanding the situation.";
    }

    return sentences.join(" ");
}

/* -----------------------------
  MAIN HOROSCOPE
------------------------------ */
function generateHoroscope(sign, planets, lang = "en", arg4 = new Date()) {
    const { period, forDate } = normalizeOptions(arg4);

    const langData = loadLang(lang);
    const { names } = langData;

    const dateKey = getDateKey(forDate);
    const signName = names?.signs?.[sign] || sign;

    //  Seed changes only for week/month/year
    const baseSeed =
        period === "day"
            ? `${sign}-${lang}-${dateKey}`
            : `${sign}-${lang}-${period}-${dateKey}`;

    function build(categoryKey) {
        return buildParagraph(
            sign,
            categoryKey,
            planets,
            langData,
            `${baseSeed}-${categoryKey}`,
            lang,
            period
        );
    }

    return {
        sign: signName,

        [names.categories.PersonalLife]: build("PersonalLife"),
        [names.categories.Profession]: build("Profession"),
        [names.categories.Health]: build("Health"),
        [names.categories.Emotions]: build("Emotions"),
        [names.categories.Travel]: build("Travel"),
        [names.categories.Luck]: build("Luck")
    };
}

module.exports = { generateHoroscope };