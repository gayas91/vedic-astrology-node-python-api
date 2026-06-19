const { execFile } = require("child_process");
const path = require("path");

/* -----------------------------
  HELPERS
------------------------------ */

function validatePayload(payload) {
    const { dob, time, lat, lon } = payload || {};

    if (!dob || !time || lat === undefined || lon === undefined) {
        throw new Error("Missing required fields: dob, time, lat, lon");
    }
}

/* -----------------------------
  SHADBALA SERVICE
------------------------------ */

function getShadbala(payload) {
    return new Promise((resolve, reject) => {
        try {
            validatePayload(payload);
        } catch (err) {
            return reject(err);
        }

        const script = path.join(__dirname, "../python/shadbala_engine.py");
        const pythonBin = process.env.PYTHON_PATH;

        if (!pythonBin) {
            return reject(
                new Error("PYTHON_PATH env is missing. Example: export PYTHON_PATH=/usr/bin/python3")
            );
        }

        execFile(
            pythonBin,
            [
                script,
                payload.dob,
                payload.time,
                String(payload.lat),
                String(payload.lon)
            ],
            (err, stdout, stderr) => {
                if (err) {
                    return reject(new Error(stderr || err.message));
                }

                let parsed;
                try {
                    parsed = JSON.parse(stdout);
                } catch (e) {
                    return reject(
                        new Error(
                            `Invalid JSON from python. stderr=${stderr || ""} stdout=${String(stdout).slice(0, 200)}`
                        )
                    );
                }

                resolve(parsed);
            }
        );
    });
}

/* -----------------------------
  BHAVBALA SERVICE
------------------------------ */

function getBhavbala(payload) {
    return new Promise((resolve, reject) => {
        try {
            validatePayload(payload);
        } catch (err) {
            return reject(err);
        }

        const script = path.join(__dirname, "../python/bhavbala_engine.py");
        const pythonBin = process.env.PYTHON_PATH;

        if (!pythonBin) {
            return reject(
                new Error("PYTHON_PATH env is missing. Example: export PYTHON_PATH=/usr/bin/python3")
            );
        }

        execFile(
            pythonBin,
            [
                script,
                payload.dob,
                payload.time,
                String(payload.lat),
                String(payload.lon)
            ],
            (err, stdout, stderr) => {
                if (err) {
                    return reject(new Error(stderr || err.message));
                }

                let parsed;
                try {
                    parsed = JSON.parse(stdout);
                } catch (e) {
                    return reject(
                        new Error(
                            `Invalid JSON from python. stderr=${stderr || ""} stdout=${String(stdout).slice(0, 200)}`
                        )
                    );
                }

                resolve(parsed);
            }
        );
    });
}

/* -----------------------------
  EXPORTS
------------------------------ */

module.exports = {
    getShadbala,
    getBhavbala
};