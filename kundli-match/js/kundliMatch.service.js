const { execFile } = require("child_process");
const path = require("path");

module.exports = function kundliMatchService(payload) {
    return new Promise((resolve, reject) => {
        const pythonBin = process.env.PYTHON_PATH;
        if (!pythonBin) return reject(new Error("PYTHON_PATH env is missing"));

        const script = path.join(__dirname, "../python/match.py");

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

            resolve(raw);
        });
    });
};
