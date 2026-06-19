const { execFile } = require("child_process");
const path = require("path");

module.exports = function getKPChart(payload) {
    return new Promise((resolve, reject) => {
        const script = path.join(__dirname, "../python/kp_engine.py");
        const PYTHON = process.env.PYTHON_PATH || "python3";

        execFile(
            PYTHON,
            [script, JSON.stringify(payload)],
            {
                maxBuffer: 1024 * 1024 * 10
            },
            (error, stdout, stderr) => {
                if (error) {
                    return reject(new Error(stderr || error.message));
                }

                try {
                    const parsed = JSON.parse(stdout);
                    if (parsed.status === false) {
                        return reject(new Error(parsed.message || "KP engine failed"));
                    }
                    resolve(parsed.data);
                } catch (e) {
                    reject(new Error(`Invalid JSON from kp_engine.py: ${stdout || stderr || e.message}`));
                }
            }
        );
    });
};