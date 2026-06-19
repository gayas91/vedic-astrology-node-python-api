const { execFile } = require("child_process");
const path = require("path");

/* -----------------------------
  HELPERS
------------------------------ */

function validatePayload(payload) {
    const { dob, time, lat, lon, year } = payload || {};

    if (!dob || !time || lat === undefined || lon === undefined || !year) {
        throw new Error("Missing required fields: dob, time, lat, lon, year");
    }
}

/* -----------------------------
  VARSHPHAL SERVICE
------------------------------ */

function getVarshphal(payload) {
    return new Promise((resolve, reject) => {
        try {
            validatePayload(payload);
        } catch (err) {
            return reject(err);
        }

        const script = path.resolve(
            __dirname,
            "../python/varshphal/varshphal_engine.py"
        );

        const pythonBin = process.env.PYTHON_PATH;

        // console.log("Running Python file:", script);
        // console.log("Payload:", payload);

        if (!pythonBin) {
            return reject(
                new Error("PYTHON_PATH env is missing")
            );
        }

        execFile(
            pythonBin,
            [
                "-u",   //VERY IMPORTANT (no buffering, fresh execution)
                script,
                JSON.stringify(payload)
            ],
            (err, stdout, stderr) => {
                
                // console.log("STDERR:", stderr);
                // console.log("STDOUT:", stdout);
                if (err) {
                    return reject(new Error(stderr || err.message));
                }

                try {
                    const parsed = JSON.parse(stdout);
                    resolve(parsed);
                } catch (e) {
                    reject(
                        new Error(
                            `Invalid JSON from python. stdout=${stdout}`
                        )
                    );
                }
            }
        );
    });
}

module.exports = {
    getVarshphal
};