const { t } = require("../../i18n");
const { localizeLagnaChart } = require("./lagnaChart.localizer"); // same one used for lagna/navamsa

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

function localizeVershful(obj, lang = "en") {
    const L = safeLang(lang);
    if (!obj || typeof obj !== "object") return obj;

    const yearLordRaw = obj.year_lord ?? null;
    const year_lord = yearLordRaw ? t(`planet.${toKey(yearLordRaw)}`, L) : yearLordRaw;

    const chartRaw = Array.isArray(obj.chart) ? obj.chart : [];
    const chart = localizeLagnaChart(chartRaw, L);

    //  keep exact keys only
    return {
        year_lord,
        varshaphal_date: obj.varshaphal_date ?? null,
        chart,
    };
}

module.exports = { localizeVershful };
