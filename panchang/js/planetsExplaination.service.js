const { execFile } = require("child_process");
const path = require("path");

/* -----------------------------
  HELPERS
------------------------------ */

function safeLang(lang) {
    return lang === "hi" ? "hi" : "en";
}

const uniquePlanets = (data) => {
    const seen = new Set();

    return data.filter(item => {
        if (seen.has(item.planet)) {
            return false; // duplicate → remove
        }
        seen.add(item.planet);
        return true; //  keep first
    });
};

/* -----------------------------
  MAIN SERVICE
------------------------------ */
module.exports = function planetsExplaination(payload) {
    return new Promise((resolve, reject) => {
        const script = path.join(__dirname, "../python/planets_calc_ex.py");
        const pythonBin = process.env.PYTHON_PATH;

        if (!pythonBin) {
            return reject(new Error("PYTHON_PATH env is missing. Example: export PYTHON_PATH=/usr/bin/python3"));
        }

        const lang = safeLang(payload?.lang);
        payload.groq_api_key = process.env.GROQ_API_KEY;

        execFile(pythonBin, [script, JSON.stringify(payload)], (err, stdout, stderr) => {
            if (err) return reject(new Error(stderr || err.message));

            let raw;
            try {
                raw = JSON.parse(stdout);
            } catch (e) {
                return reject(
                    new Error(`Invalid JSON from python. stderr=${stderr || ""} stdout=${String(stdout).slice(0, 200)}`)
                );
            }
            const cleanedData = uniquePlanets(raw);
            
            resolve(cleanedData);
        });
    });
};
