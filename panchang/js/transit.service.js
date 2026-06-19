const { execFile } = require("child_process");
const path = require("path");

/* -----------------------------
  MAIN SERVICE
------------------------------ */
module.exports = function getTransit(payload) {
    return new Promise((resolve, reject) => {
        const script = path.join(__dirname, "../python/transit_chart.py");
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
