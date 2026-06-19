const { t } = require("../../i18n");

function safeLang(lang) {
    return lang === "hi" ? "hi" : "en";
}

function toKey(str = "") {
    return String(str)
        .trim()
        .toLowerCase()
        .replace(/&/g, "and")
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "");
}

// "Sun" -> "sun", "Rahu" -> "rahu", "Ascendant" -> "ascendant"
function planetNameToKey(name = "") {
    return toKey(name);
}

function localizePlanets(planets = [], lang = "en") {
    const L = safeLang(lang);
    if (!Array.isArray(planets)) return planets;

    return planets.map((p) => {
        const nameRaw = p?.name ?? null;
        const signRaw = p?.sign ?? null;
        const signLordRaw = p?.signLord ?? null;
        const nakRaw = p?.nakshatra ?? null;
        const nakLordRaw = p?.nakshatraLord ?? null;
        const awasthaRaw = p?.planet_awastha ?? null;

        const name = nameRaw ? t(`planet.${planetNameToKey(nameRaw)}`, L) : nameRaw;
        const sign = signRaw ? t(`rashi.${toKey(signRaw)}`, L) : signRaw;
        const signLord = signLordRaw ? t(`planet.${planetNameToKey(signLordRaw)}`, L) : signLordRaw;

        // nakshatra keys you already use: nakshatra.magha, nakshatra.hasta ...
        // Your toKey will convert "Purva Phalguni" -> "purva_phalguni"  matches your hi.json
        const nakshatra = nakRaw ? t(`nakshatra.${toKey(nakRaw)}`, L) : nakRaw;
        const nakshatraLord = nakLordRaw ? t(`planet.${planetNameToKey(nakLordRaw)}`, L) : nakLordRaw;

        // awastha: Vridha/Kumara/Bala/Mrityu/--
        const awKey = awasthaRaw === "--" ? "awastha.__" : `awastha.${toKey(awasthaRaw)}`;
        const planet_awastha = awasthaRaw ? t(awKey, L) : awasthaRaw;

        // Return SAME keys, only translated values
        return {
            ...p,
            name,
            sign,
            signLord,
            nakshatra,
            nakshatraLord,
            planet_awastha
        };
    });
}

module.exports = { localizePlanets };
