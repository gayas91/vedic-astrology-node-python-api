const { execFile } = require("child_process");
const path = require("path");

function getYearRange(dob, year) {

    const birthDate = new Date(dob);

    const month = birthDate.toLocaleString(
        "en-US",
        {
            month: "short",
            timeZone: "UTC"
        }
    );

    return `${month} ${year} - ${month} ${year + 1}`;
}

function formatHouses(varshphalChart) {
    const houses = {};

    varshphalChart.forEach((house, index) => {

        houses[String(index + 1)] =
            (house.planet_small || []).map(p =>
                p.trim()
            );

    });

    return houses;
}
/* -----------------------------
  MAIN SERVICE
------------------------------ */
module.exports = function getVarshphalNew(payload) {
    return new Promise((resolve, reject) => {
        const script = path.join(__dirname, "../python/lal-kitab.py");
        const pythonBin = process.env.PYTHON_PATH;

        if (!pythonBin) {
            return reject(new Error("PYTHON_PATH env is missing. Example: export PYTHON_PATH=/usr/bin/python3"));
        }

        payload.mode = process.env.MODE;
        
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

            let rsl = {
                status: true,
                data: {
                    status: true,
                    year: Number(payload.year),
                    year_range: getYearRange(
                        payload.dob,
                        Number(payload.year)
                    ),
                    houses: formatHouses(
                        raw.varshphal_chart
                    )
                }
            };

            resolve(rsl);
        });
    });
};
