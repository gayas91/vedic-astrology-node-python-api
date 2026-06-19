const { execFile } = require("child_process");
const path = require("path");
const { DateTime } = require("luxon");

/* -----------------------------
  HELPERS
------------------------------ */
function pad2(n) {
    return String(n).padStart(2, "0");
}

function normalizeHHMMSS(t) {
    // "6:9:11" -> "06:09:11"
    if (!t || typeof t !== "string") return null;
    const parts = t.split(":").map((x) => x.trim());
    if (parts.length < 2) return t;
    const hh = pad2(Number(parts[0] || 0));
    const mm = pad2(Number(parts[1] || 0));
    const ss = pad2(Number(parts[2] || 0));
    return `${hh}:${mm}:${ss}`;
}

function jdToMillis(jd) {
    return (jd - 2440587.5) * 86400000;
}

function jdToHHMMSS_Local(jd, tz = "Asia/Kolkata") {
    const ms = jdToMillis(jd);
    return DateTime.fromMillis(ms, { zone: "utc" }).setZone(tz).toFormat("HH:mm:ss");
}

function safeNum(v) {
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
}

function formatEndTime(et) {
    // supports {hour, minute, second} or "HH:MM:SS"
    if (!et) return { hour: null, minute: null, second: null };

    if (typeof et === "string") {
        const t = normalizeHHMMSS(et);
        const [hh, mm, ss] = t.split(":").map((x) => safeNum(x));
        return { hour: hh, minute: mm, second: ss };
    }

    return {
        hour: et.hour ?? null,
        minute: et.minute ?? null,
        second: et.second ?? null,
    };
}

function getLocalDayName(datetimeStr, tz) {
    // datetimeStr: "YYYY-MM-DD HH:mm:ss" (local time of tz)
    try {
        return DateTime.fromFormat(datetimeStr, "yyyy-MM-dd HH:mm:ss", { zone: tz }).toFormat("cccc");
    } catch (e) {
        return null;
    }
}

/* -----------------------------
  BUILD EXACT SAMPLE SHAPE
------------------------------ */
function buildPanchangShape(p, ctx) {
    // p = python panchangObj
    const tz = ctx?.timezone || "Asia/Kolkata";

    return {
        day: p?.day || getLocalDayName(ctx?.datetime, tz),

        sunrise: normalizeHHMMSS(p?.sunrise),
        sunset: normalizeHHMMSS(p?.sunset),

        moonrise: normalizeHHMMSS(p?.moonrise),
        moonset: normalizeHHMMSS(p?.moonset),

        vedic_sunrise: normalizeHHMMSS(p?.vedic_sunrise),
        vedic_sunset: normalizeHHMMSS(p?.vedic_sunset),

        tithi: {
            details: {
                tithi_number: p?.tithi?.details?.tithi_number ?? p?.tithi_number ?? null,
                tithi_name: p?.tithi?.details?.tithi_name ?? p?.tithi_name ?? null,
                special: p?.tithi?.details?.special ?? null,
                summary: p?.tithi?.details?.summary ?? null,
                deity: p?.tithi?.details?.deity ?? null,
            },
            end_time: formatEndTime(p?.tithi?.end_time),
            end_time_ms: p?.tithi?.end_time_ms ?? null,
        },

        nakshatra: {
            details: {
                nak_number: p?.nakshatra?.details?.nak_number ?? p?.nak_number ?? null,
                nak_name: p?.nakshatra?.details?.nak_name ?? p?.nak_name ?? null,
                ruler: p?.nakshatra?.details?.ruler ?? null,
                deity: p?.nakshatra?.details?.deity ?? null,
                special: p?.nakshatra?.details?.special ?? null,
                summary: p?.nakshatra?.details?.summary ?? null,
                charan: p?.nakshatra?.details?.charan ?? p?.charan ?? null,
            },
            end_time: formatEndTime(p?.nakshatra?.end_time),
            end_time_ms: p?.nakshatra?.end_time_ms ?? null,
        },

        yog: {
            details: {
                yog_number: p?.yog?.details?.yog_number ?? p?.yog_number ?? null,
                yog_name: p?.yog?.details?.yog_name ?? p?.yog_name ?? null,
                special: p?.yog?.details?.special ?? null,
                meaning: p?.yog?.details?.meaning ?? null,
            },
            end_time: formatEndTime(p?.yog?.end_time),
            end_time_ms: p?.yog?.end_time_ms ?? null,
        },

        karan: {
            details: {
                karan_number: p?.karan?.details?.karan_number ?? p?.karan_number ?? null,
                karan_name: p?.karan?.details?.karan_name ?? p?.karan_name ?? null,
                special: p?.karan?.details?.special ?? null,
                deity: p?.karan?.details?.deity ?? null,
            },
            end_time: formatEndTime(p?.karan?.end_time),
            end_time_ms: p?.karan?.end_time_ms ?? null,
        },

        hindu_maah: {
            adhik_status: p?.hindu_maah?.adhik_status ?? null,
            purnimanta: p?.hindu_maah?.purnimanta ?? null,
            amanta: p?.hindu_maah?.amanta ?? null,
            amanta_id: p?.hindu_maah?.amanta_id ?? null,
            purnimanta_id: p?.hindu_maah?.purnimanta_id ?? null,
        },

        paksha: p?.paksha ?? null,
        ritu: p?.ritu ?? null,

        sun_sign: p?.sun_sign ?? null,
        moon_sign: p?.moon_sign ?? null,

        ayana: p?.ayana ?? null,
        panchang_yog: p?.panchang_yog ?? "",

        vikram_samvat: p?.vikram_samvat ?? null,
        shaka_samvat: p?.shaka_samvat ?? null,
        vkram_samvat_name: p?.vkram_samvat_name ?? null,
        shaka_samvat_name: p?.shaka_samvat_name ?? null,

        disha_shool: p?.disha_shool ?? null,
        disha_shool_remedies: p?.disha_shool_remedies ?? "-",

        nak_shool: {
            direction: p?.nak_shool?.direction ?? "none",
            remedies: p?.nak_shool?.remedies ?? "-",
        },

        moon_nivas: p?.moon_nivas ?? null,

        abhijit_muhurta: {
            start: p?.abhijit_muhurta?.start ?? null,
            end: p?.abhijit_muhurta?.end ?? null,
        },

        rahukaal: {
            start: normalizeHHMMSS(p?.rahukaal?.start),
            end: normalizeHHMMSS(p?.rahukaal?.end),
        },

        guliKaal: {
            start: normalizeHHMMSS(p?.guliKaal?.start),
            end: normalizeHHMMSS(p?.guliKaal?.end),
        },

        yamghant_kaal: {
            start: normalizeHHMMSS(p?.yamghant_kaal?.start),
            end: normalizeHHMMSS(p?.yamghant_kaal?.end),
        },
    };
}

/* -----------------------------
  MAIN SERVICE
------------------------------ */
module.exports = function getPanchang(payload) {
    return new Promise((resolve, reject) => {
        // console.log(path.join(__dirname, "../python/calc.py"));
        const script = path.join(__dirname, "../python/calc.py");
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

            if (!raw || !raw.panchangObj) {
                return reject(new Error("Python response missing panchangObj"));
            }

            const tz = payload.timezone || "Asia/Kolkata";

            // python panchangObj
            const pObj = { ...raw.panchangObj };

            //  Ensure sunrise/sunset are LOCAL, not UTC
            if (pObj.sunrise_jd) pObj.sunrise = jdToHHMMSS_Local(pObj.sunrise_jd, tz);
            if (pObj.sunset_jd) pObj.sunset = jdToHHMMSS_Local(pObj.sunset_jd, tz);

            // normalize if already present
            if (pObj.sunrise) pObj.sunrise = normalizeHHMMSS(pObj.sunrise);
            if (pObj.sunset) pObj.sunset = normalizeHHMMSS(pObj.sunset);

            //  Build final exact key format (NO panchangObj returned)
            const response = {
                moon_sign: raw.moon_sign,
                ascendant_sign: raw.ascendant_sign,

                //  what you want:
                panchang: buildPanchangShape(pObj, {
                    datetime: payload.datetime,
                    timezone: tz,
                }),
            };

            if (raw.Vershful) response.Vershful = raw.Vershful;

            resolve(response);
        });
    });
};
