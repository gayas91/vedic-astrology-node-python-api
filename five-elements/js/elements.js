const { execFile } = require("child_process");
const path = require("path");

/* Process */
// 5 elements (Pancha Tatva):

// Fire → Aries, Leo, Sagittarius
// Earth → Taurus, Virgo, Capricorn
// Air → Gemini, Libra, Aquarius
// Water → Cancer, Scorpio, Pisces

// Calculated the longitude of all planets // Sab planets ki longitude nikali
// Determined the zodiac sign (rashi) for each planet // Har planet ka rashi determine kiya
// Mapped each zodiac sign to its corresponding element // Har rashi ko element map kiya
// Assigned counts/weights based on planetary influence // Count / weight assign kiya
// Calculated the final percentage distribution of elements // Percentage calculate kiya
/* Process */

/* -----------------------------
  MAIN SERVICE
------------------------------ */
module.exports = function getFiveElements(payload) {
    return new Promise((resolve, reject) => {
        const script = path.join(__dirname, "../python/elements_calc.py");
        const pythonBin = process.env.PYTHON_PATH;

        if (!pythonBin) {
            return reject(new Error("PYTHON_PATH env is missing. Example: export PYTHON_PATH=/usr/bin/python3"));
        }

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

            if (!raw) {
                return reject(new Error("Python response missing panchangObj"));
            }
            resolve(raw);
        });
    });
};
