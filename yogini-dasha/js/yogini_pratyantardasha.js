const { execFile } = require("child_process");
const path = require("path");

module.exports = function getYoginiPratyantardasha(payload) {
    return new Promise((resolve, reject) => {
        try {
            const scriptPath = path.join(__dirname, "../python/yogini_pratyantardasha_engine.py");
            const PYTHON_PATH = process.env.PYTHON_PATH || "python3";

            execFile(
                PYTHON_PATH,
                [scriptPath, JSON.stringify(payload)],
                { maxBuffer: 1024 * 1024 * 10 },
                (error, stdout, stderr) => {
                    if (error) {
                        return reject(new Error(stderr || error.message));
                    }

                    try {
                        const parsed = JSON.parse(stdout.trim());

                        if (!parsed.status) {
                            return reject(new Error(parsed.message || "Python error"));
                        }

                        resolve(parsed.data);
                    } catch (e) {
                        reject(new Error("Invalid JSON from Python: " + stdout));
                    }
                }
            );
        } catch (err) {
            reject(err);
        }
    });
};