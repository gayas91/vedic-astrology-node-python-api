// panchang/js/subVdasha.service.js
const { execFile } = require("child_process");
const path = require("path");
const { t } = require("../../i18n");

// Normalize planet input so user can pass MARS / mars / मंगल / etc.
function normalizePlanet(planet = "") {
    const p = String(planet).trim().toLowerCase();

    const map = {
        sun: "sun",
        moon: "moon",
        mars: "mars",
        mercury: "mercury",
        jupiter: "jupiter",
        venus: "venus",
        saturn: "saturn",
        rahu: "rahu",
        ketu: "ketu",
    };
    if (map[p]) return map[p];

    const hiMap = {
        सूर्य: "sun",
        चंद्र: "moon",
        चन्द्र: "moon",
        मंगल: "mars",
        बुध: "mercury",
        गुरु: "jupiter",
        बृहस्पति: "jupiter",
        शुक्र: "venus",
        शनि: "saturn",
        राहु: "rahu",
        केतु: "ketu",
    };
    if (hiMap[planet]) return hiMap[planet];

    return p || planet;
}

function toCamelCasePlanet(name) {
    if (typeof name !== "string") return name;
    const lower = name.trim().toLowerCase();
    return lower ? lower.charAt(0).toUpperCase() + lower.slice(1) : name;
}

// Translate a planet value depending on lang
function formatPlanet(value, lang) {
    if (typeof value !== "string") return value;

    const v = value.trim().toLowerCase(); // handles "KETU", "ketu", "Ketu"
    const key = `planet.${v}`;

    // If lang is hi and key exists, return Hindi planet name
    if (lang === "hi") {
        const tr = t(key, "hi");
        if (tr !== key) return tr;
    }

    // Otherwise return CamelCase in English
    // (even if python gave "KETU" or "ketu")
    return toCamelCasePlanet(v);
}

// Deep-walk: translate any planet-ish fields if they appear
function translateSubVdashaResponse(data, lang) {
    if (!data || typeof data !== "object") return data;

    const planetFields = new Set([
        "planet",
        "lord",
        "mahadasha",
        "antar",
        "sub",
        "sub_lord",
        "pratyantar",
    ]);

    const walk = (obj) => {
        if (Array.isArray(obj)) return obj.map(walk);
        if (!obj || typeof obj !== "object") return obj;

        const out = { ...obj };

        for (const k of Object.keys(out)) {
            const val = out[k];

            if (planetFields.has(k)) {
                out[k] = formatPlanet(val, lang);
            } else {
                out[k] = walk(val);
            }
        }
        return out;
    };

    return walk(data);
}

module.exports = function getSubVdasha(planet, start, lang = "en") {
    return new Promise((resolve, reject) => {
        const script = path.join(__dirname, "../python/sub_vdasha.py");
        const PYTHON = process.env.PYTHON_PATH || "python3";

        const safeLang = lang === "hi" ? "hi" : "en";

        const payload = {
            planet: normalizePlanet(planet),
            start: start,
            language: safeLang,
        };

        execFile(PYTHON, [script, JSON.stringify(payload)], (err, stdout, stderr) => {
            if (err) return reject(new Error(stderr || err.message));

            try {
                const parsed = JSON.parse(stdout);

                //  This will turn "KETU" -> "Ketu" for en
                //  and "KETU" -> "केतु" for hi (if key exists)
                const finalData = translateSubVdashaResponse(parsed, safeLang);

                resolve(finalData);
            } catch (e) {
                reject(new Error("Invalid Python output"));
            }
        });
    });
};