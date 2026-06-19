const { execFile } = require("child_process");
const path = require("path");
const { t } = require("../../i18n");

// Normalize planet input so user can pass MARS / mars / मंगल / etc.
function normalizePlanet(planet = "") {
    const raw = String(planet).trim();
    const p = raw.toLowerCase();

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
    if (hiMap[raw]) return hiMap[raw];

    return p || raw;
}

function toCamelCasePlanet(name) {
    if (typeof name !== "string") return name;
    const lower = name.trim().toLowerCase();
    return lower ? lower.charAt(0).toUpperCase() + lower.slice(1) : name;
}

// Translate a planet depending on lang:
// - hi => planet.<x> translation if available
// - en => CamelCase (Ketu, Mars, Rahu...)
function formatPlanet(value, lang) {
    if (typeof value !== "string") return value;

    const v = value.trim().toLowerCase();
    const key = `planet.${v}`;

    if (lang === "hi") {
        const tr = t(key, "hi");
        if (tr !== key) return tr;
    }

    return toCamelCasePlanet(v);
}

// Deep-walk: translate any planet-ish fields in python response
function translatePranResponse(data, lang) {
    if (!data || typeof data !== "object") return data;

    const planetFields = new Set([
        "planet",
        "planet_name",
        "lord",
        "maha",
        "antar",
        "pratyantar",
        "sookshma",
        "pran",

        // sometimes used naming
        "mahadasha",
        "antardasha",
        "pratyantardasha",
        "sookshmadasha",
        "prandasha",
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

module.exports = function getPranVdasha(maha, antar, pratyantar, sookshma, start, lang = "en") {
    return new Promise((resolve, reject) => {
        const script = path.join(__dirname, "../python/pran_vdasha.py");
        const PYTHON = process.env.PYTHON_PATH || "python3";
        const safeLang = lang === "hi" ? "hi" : "en";

        const payload = {
            maha: normalizePlanet(maha),
            antar: normalizePlanet(antar),
            pratyantar: normalizePlanet(pratyantar),
            sookshma: normalizePlanet(sookshma),
            start,
            language: safeLang, // safe even if python ignores
        };

        execFile(PYTHON, [script, JSON.stringify(payload)], (err, stdout, stderr) => {
            if (err) return reject(new Error(stderr || err.message));

            try {
                const parsed = JSON.parse(stdout);
                const finalData = translatePranResponse(parsed, safeLang);
                resolve(finalData);
            } catch (e) {
                reject(new Error("Invalid Python output"));
            }
        });
    });
};