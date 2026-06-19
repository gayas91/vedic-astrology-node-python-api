// i18n/index.js
const path = require("path");
const fs = require("fs");

const cache = {};

function load(lang = "en") {
    const safe = lang === "hi" ? "hi" : "en";
    const filePath = path.join(__dirname, `${safe}.json`);

    // check file exists
    if (!fs.existsSync(filePath)) {
        console.error(`[i18n] ERROR: file not found: ${filePath}`);
        // return empty object to let the system fallback to key
        return {};
    }

    // In development, always reload so you see edits without a full server restart
    const devReload = process.env.NODE_ENV !== "production";

    if (!cache[safe] || devReload) {
        // clear require cache for that file so require() reads updated JSON
        try {
            if (devReload) {
                const resolved = require.resolve(filePath);
                if (require.cache[resolved]) {
                    delete require.cache[resolved];
                }
            }
        } catch (err) {
            // ignore
        }

        try {
            const loaded = require(filePath);
            cache[safe] = loaded || {};
            // debug info
            const keys = Object.keys(cache[safe] || {});
            // console.log(`[i18n] loaded ${filePath} — keys: ${keys.length}`);
            // console.log("[i18n] sample keys:", keys.slice(0, 12));
        } catch (err) {
            console.error(`[i18n] failed require ${filePath}:`, err.message);
            cache[safe] = {};
        }
    }

    return cache[safe];
}

// supports {var} replacement
function t(key, lang = "en", vars = {}) {
    const dict = load(lang);
    const en = load("en");

    let str = dict[key] ?? en[key] ?? key;

    // replace {x}
    str = String(str).replace(/\{(\w+)\}/g, (_, v) =>
        vars[v] !== undefined ? String(vars[v]) : `{${v}}`
    );

    return str;
}

module.exports = { t, load };