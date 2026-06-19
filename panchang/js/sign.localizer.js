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

function localizeSign(signName, lang = "en") {
    const L = safeLang(lang);
    if (!signName) return signName;
    return t(`rashi.${toKey(signName)}`, L);
}

module.exports = { localizeSign };
