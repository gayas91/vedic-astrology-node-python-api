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

function localizeMhadasha(list = [], lang = "en") {
    const L = safeLang(lang);
    if (!Array.isArray(list)) return list;

    return list.map((row) => {
        const planetRaw = row?.planet ?? null;
        const planet = planetRaw ? t(`planet.${toKey(planetRaw)}`, L) : planetRaw;

        // Keep ALL keys same, only planet translated
        return { ...row, planet };
    });
}

module.exports = { localizeMhadasha };
