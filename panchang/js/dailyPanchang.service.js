const { execFile } = require("child_process");
const path = require("path");
const { DateTime } = require("luxon");
const { localizeLagnaChart } = require("./lagnaChart.localizer");
const { localizePlanets } = require("./planets.localizer");
const { localizeMhadasha } = require("./mhadasha.localizer");
const { localizeDivisionalCharts } = require("./divisionalCharts.localizer");
const { localizeVershful } = require("./vershful.localizer");
const { localizeSign } = require("./sign.localizer");


//  i18n (root/i18n). From panchang/js -> ../../i18n
const { t } = require("../../i18n");

/* -----------------------------
  HELPERS
------------------------------ */
function pad2(n) {
    return String(n).padStart(2, "0");
}

function normalizeHHMMSS(tVal) {
    // "6:9:11" -> "06:09:11"
    if (!tVal || typeof tVal !== "string") return null;
    const parts = tVal.split(":").map((x) => x.trim());
    if (parts.length < 2) return tVal;
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
        const tVal = normalizeHHMMSS(et);
        const [hh, mm, ss] = tVal.split(":").map((x) => safeNum(x));
        return { hour: hh, minute: mm, second: ss };
    }

    return {
        hour: et.hour ?? null,
        minute: et.minute ?? null,
        second: et.second ?? null,
    };
}

//  key helper: "Krishna-Chaturdashi" -> "krishna_chaturdashi"
function toKey(str = "") {
    return String(str)
        .trim()
        .toLowerCase()
        .replace(/&/g, "and")
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "");
}

function safeLang(lang) {
    return lang === "hi" ? "hi" : "en";
}

function normalizePaksha(pakshaRaw) {
    if (!pakshaRaw) return null;
    return String(pakshaRaw)
        .trim()
        .replace(/_/g, "-")
        .replace(/\s+/g, "-")
        .replace(/-+/g, "-");
}

function getLocalDayName(datetimeStr, tz, lang = "en") {
    try {
        const dayEn = DateTime.fromFormat(datetimeStr, "yyyy-MM-dd HH:mm:ss", { zone: tz }).toFormat("cccc");
        // translate day without adding new keys in response
        return t(`day.${toKey(dayEn)}`, lang);
    } catch (e) {
        return null;
    }
}

function safeTranslate(key, fallback, lang) {
    const value = t(key, lang);
    return value === key ? fallback : value;
}

/* -----------------------------
  BUILD EXACT SAMPLE SHAPE
   NO EXTRA KEYS ADDED
------------------------------ */
function buildPanchangShape(p, ctx) {
    const tz = ctx?.timezone || "Asia/Kolkata";
    const lang = safeLang(ctx?.lang);

    // raw values from python
    const tithiNameRaw = p?.tithi?.details?.tithi_name ?? p?.tithi_name ?? null;
    const nakNameRaw = p?.nakshatra?.details?.nak_name ?? p?.nak_name ?? null;
    const yogNameRaw = p?.yog?.details?.yog_name ?? p?.yog_name ?? null;
    const karanNameRaw = p?.karan?.details?.karan_name ?? p?.karan_name ?? null;
    const nextKaranName = p?.karan?.details?.next_karana_name ?? p?.next_karana_name ?? null;

    const sunSignRaw = p?.sun_sign ?? null;
    const moonSignRaw = p?.moon_sign ?? null;

    const pakshaRaw = p?.paksha ?? null;

    // translate values (but DO NOT add any extra keys into JSON)
    const tithiName = tithiNameRaw ? safeTranslate(`tithi.${toKey(tithiNameRaw)}`, lang) : tithiNameRaw;
    const nakName = nakNameRaw ? safeTranslate(`nakshatra.${toKey(nakNameRaw)}`, lang) : nakNameRaw;
    const yogName = yogNameRaw ? safeTranslate(`yog.${toKey(yogNameRaw)}`, lang) : yogNameRaw;
    const karanName = karanNameRaw ? safeTranslate(`karan.${toKey(karanNameRaw)}`, lang) : karanNameRaw;

    const sunSign = sunSignRaw ? safeTranslate(`rashi.${toKey(sunSignRaw)}`, lang) : sunSignRaw;
    const moonSign = moonSignRaw ? safeTranslate(`rashi.${toKey(moonSignRaw)}`, lang) : moonSignRaw;

    const pakshaNorm = normalizePaksha(pakshaRaw); // Krishna Paksha / Krishna-Paksha -> Krishna-Paksha
    const paksha = pakshaNorm ? safeTranslate(`paksha.${toKey(pakshaNorm)}`, lang) : pakshaRaw;

    return {
        day: p?.day ? safeTranslate(`day.${toKey(p.day)}`, lang) : getLocalDayName(ctx?.datetime, tz, lang),

        sunrise: normalizeHHMMSS(p?.sunrise),
        sunset: normalizeHHMMSS(p?.sunset),

        moonrise: normalizeHHMMSS(p?.moonrise),
        moonset: normalizeHHMMSS(p?.moonset),

        vedic_sunrise: normalizeHHMMSS(p?.vedic_sunrise),
        vedic_sunset: normalizeHHMMSS(p?.vedic_sunset),

        tithi: {
            details: {
                tithi_number: p?.tithi?.details?.tithi_number ?? p?.tithi_number ?? null,
                tithi_name: tithiName,
                next_tithi_number: p?.tithi?.details?.next_tithi_number ?? p?.next_tithi_number ?? null,
                next_tithi_name: p?.tithi?.details?.next_tithi_name ?? p?.next_tithi_name ?? null,
                special: p?.tithi?.details?.special ?? null,
                summary: p?.tithi?.details?.summary ?? null,
                deity: p?.tithi?.details?.deity ?? null
            },
            end_time: formatEndTime(p?.tithi?.end_time),
            end_time_ms: p?.tithi?.end_time_ms ?? null
        },

        nakshatra: {
            details: {
                nak_number: p?.nakshatra?.details?.nak_number ?? p?.nak_number ?? null,
                nak_name: nakName,
                next_nak_number: p?.nakshatra?.details?.next_nak_number ?? p?.next_nak_number ?? null,
                ruler: p?.nakshatra?.details?.ruler ?? null,
                deity: p?.nakshatra?.details?.deity ?? null,
                special: p?.nakshatra?.details?.special ?? null,
                summary: p?.nakshatra?.details?.summary ?? null,
                charan: p?.nakshatra?.details?.charan ?? p?.charan ?? null
            },
            end_time: formatEndTime(p?.nakshatra?.end_time),
            end_time_ms: p?.nakshatra?.end_time_ms ?? null
        },

        yog: {
            details: {
                yog_number: p?.yog?.details?.yog_number ?? p?.yog_number ?? null,
                yog_name: yogName,
                next_yog_number: p?.yog?.details?.next_yog_number ?? p?.next_yog_number ?? null,
                next_yog_name: p?.yog?.details?.next_yog_name ?? p?.next_yog_name ?? null,
                special: p?.yog?.details?.special ?? null,
                meaning: p?.yog?.details?.meaning ?? null
            },
            end_time: formatEndTime(p?.yog?.end_time),
            end_time_ms: p?.yog?.end_time_ms ?? null
        },

        karan: {
            details: {
                karan_number: p?.karan?.details?.karan_number ?? p?.karan_number ?? null,
                karan_name: karanName,
                next_karana_name: nextKaranName,
                special: p?.karan?.details?.special ?? null,
                deity: p?.karan?.details?.deity ?? null
            },
            end_time: formatEndTime(p?.karan?.end_time),
            end_time_ms: p?.karan?.end_time_ms ?? null
        },

        hindu_maah: {
            adhik_status: p?.hindu_maah?.adhik_status ?? null,
            purnimanta: p?.hindu_maah?.purnimanta ?? null,
            amanta: p?.hindu_maah?.amanta ?? null,
            amanta_id: p?.hindu_maah?.amanta_id ?? null,
            purnimanta_id: p?.hindu_maah?.purnimanta_id ?? null
        },

        paksha: paksha,
        ritu: p?.ritu ?? null,

        sun_sign: sunSign,
        moon_sign: moonSign,

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
            remedies: p?.nak_shool?.remedies ?? "-"
        },

        moon_nivas: p?.moon_nivas ?? null,

        abhijit_muhurta: {
            start: p?.abhijit_muhurta?.start ?? null,
            end: p?.abhijit_muhurta?.end ?? null
        },

        rahukaal: {
            start: normalizeHHMMSS(p?.rahukaal?.start),
            end: normalizeHHMMSS(p?.rahukaal?.end)
        },

        guliKaal: {
            start: normalizeHHMMSS(p?.guliKaal?.start),
            end: normalizeHHMMSS(p?.guliKaal?.end)
        },

        yamghant_kaal: {
            start: normalizeHHMMSS(p?.yamghant_kaal?.start),
            end: normalizeHHMMSS(p?.yamghant_kaal?.end)
        }
    };
}

/* -----------------------------
  MAIN SERVICE
------------------------------ */
module.exports = function getDailyPanchang(payload) {
    return new Promise((resolve, reject) => {
        const script = path.join(__dirname, "../python/daily_calc.py");
        const pythonBin = process.env.PYTHON_PATH;

        if (!pythonBin) {
            return reject(new Error("PYTHON_PATH env is missing. Example: export PYTHON_PATH=/usr/bin/python3"));
        }

        const lang = safeLang(payload?.lang);
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
            const pObj = { ...raw.panchangObj };
            // console.log(raw.planets_detailed, " ,,,,,,,,");

            //  Ensure sunrise/sunset are LOCAL, not UTC
            if (pObj.sunrise_jd) pObj.sunrise = jdToHHMMSS_Local(pObj.sunrise_jd, tz);
            if (pObj.sunset_jd) pObj.sunset = jdToHHMMSS_Local(pObj.sunset_jd, tz);

            // normalize if already present
            if (pObj.sunrise) pObj.sunrise = normalizeHHMMSS(pObj.sunrise);
            if (pObj.sunset) pObj.sunset = normalizeHHMMSS(pObj.sunset);

            const response = {
                moon_sign: lang === "hi" ? localizeSign(raw.moon_sign, lang) : raw.moon_sign,
                ascendant_sign: lang === "hi" ? localizeSign(raw.ascendant_sign, lang) : raw.ascendant_sign,
                panchang: buildPanchangShape(pObj, {
                    datetime: payload.datetime,
                    timezone: tz,
                    lang
                }),
                dob_panchang: {
                    nakshatra_num: raw.dobNakshatra.nakshatra.details.nak_number,
                    dob_moon_sign: lang === "hi" ? localizeSign(raw.dob_moon_sign, lang) : raw.dob_moon_sign,
                    durmuhurta: raw.panchangObj.durmuhurta,
                    varjyam: raw.panchangObj.varjyam,
                    amrit_kaal: raw.panchangObj.amrit_kaal,
                    godhuli_muhurta: raw.panchangObj.godhuli_muhurta,
                    nishita_kaal: raw.panchangObj.nishita_kaal,
                    mhadasha: raw.mhadasha,
                    planets: raw.planets_detailed
                }
            };
            resolve(response);
        });
    });
};
