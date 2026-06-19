const { t } = require("../../i18n");

function safeLang(lang) {
    return lang === "hi" ? "hi" : "en";
}

// same helper you used
function toKey(str = "") {
    return String(str)
        .trim()
        .toLowerCase()
        .replace(/&/g, "and")
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "");
}

function planetCodeToKey(code = "") {
    // "SUN" -> "sun"
    return String(code).trim().toLowerCase();
}

function localizeLagnaChart(lagnaChart = [], lang = "en") {
    const L = safeLang(lang);
    if (!Array.isArray(lagnaChart)) return lagnaChart;

    // IMPORTANT: don't mutate original (keep english stable)
    return lagnaChart.map((cell) => {
        const signNameRaw = cell?.sign_name ?? null;

        // sign_name: use your existing rashi.* translations (already in hi/en)
        const signName = signNameRaw ? t(`rashi.${toKey(signNameRaw)}`, L) : signNameRaw;

        // planet: ["SUN","MOON"] -> ["सूर्य","चंद्र"] for hi
        const planetArr = Array.isArray(cell?.planet) ? cell.planet : [];
        const planetLocalized = planetArr.map((p) => {
            const k = planetCodeToKey(p);
            return t(`planet.${k}`, L);
        });

        // planet_small: use planet_short.* mapping
        const planetSmallArr = Array.isArray(cell?.planet_small) ? cell.planet_small : [];
        // if planet list length matches, rebuild from codes (best)
        const planetSmallLocalized =
            planetArr.length > 0
                ? planetArr.map((p) => {
                    const k = planetCodeToKey(p);
                    return t(`planet_short.${k}`, L);
                })
                : planetSmallArr;

        return {
            sign: cell?.sign ?? null, // keep as is
            sign_name: signName,      // localized
            planet: planetLocalized,  // localized
            planet_small: planetSmallLocalized, // localized
            planet_degree: Array.isArray(cell?.planet_degree) ? cell.planet_degree : [] // keep as is
        };
    });
}

module.exports = { localizeLagnaChart };
