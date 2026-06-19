const { execFile } = require("child_process");
const path = require("path");

/* -----------------------------
  VARSHPHAL SERVICE
------------------------------ */

function getCalender(payload) {
    return new Promise((resolve, reject) => {

        const script = path.resolve(
            __dirname,
            "../python/calendar_engine.py"
        );
        
        const pythonBin = process.env.PYTHON_PATH;

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
    getCalender
};