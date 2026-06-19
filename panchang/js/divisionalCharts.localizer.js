const { t } = require("../../i18n");
const { localizeLagnaChart } = require("./lagnaChart.localizer"); // the generic one you used for lagna/navamsa

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

// Convert chart name to stable key
// "Hora (D-2)" -> "hora_d_2"
function chartNameToKey(name = "") {
    return toKey(name).replace(/^d_/, ""); // safe
}

function localizeDivisionalCharts(list = [], lang = "en") {
    const L = safeLang(lang);
    if (!Array.isArray(list)) return list;

    return list.map((item) => {
        const nameRaw = item?.name ?? null;
        const chartRaw = item?.chart ?? [];

        //  translate chart cells
        const chart = localizeLagnaChart(chartRaw, L);

        //  OPTIONAL: translate name (if keys exist)
        // if you don't want, just use: const name = nameRaw;
        const nameKey = nameRaw ? `chart_name.${chartNameToKey(nameRaw)}` : null;
        const name = (L === "hi" && nameKey) ? t(nameKey, L) : nameRaw;

        return { ...item, name, chart };
    });
}

module.exports = { localizeDivisionalCharts };
