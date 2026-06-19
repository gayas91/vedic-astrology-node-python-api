const { getPlanets } = require("./ephemeris");
const { signs } = require("./zodiac");
const { generateHoroscope } = require("./horoscopeEngine");


function formatDateDDMYYYY(d = new Date()) {
    // sample wants: 11-2-2026 (no leading zero for month/day)
    const day = d.getDate();
    const month = d.getMonth() + 1;
    const year = d.getFullYear();
    return `${day}-${month}-${year}`;
}

function parseQueryDate(dateStr) {
    // Accept: YYYY-MM-DD
    if (!dateStr || typeof dateStr !== "string") return null;
    const m = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!m) return null;

    const y = Number(m[1]);
    const mo = Number(m[2]);
    const da = Number(m[3]);

    const dt = new Date(Date.UTC(y, mo - 1, da, 0, 0, 0));
    if (Number.isNaN(dt.getTime())) return null;
    return dt;
}

function toTitleCase(s) {
    if (!s) return s;
    return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

module.exports = async (req, res) => {
    try {
        const lang = req.query.lang === "hi" ? "hi" : "en";
        const period = req.query.period || "day";

        // Optional: allow date override: /daily-horoscope?date=2026-02-11
        const qDate = parseQueryDate(req.query.date);
        const predictionDate = qDate ? qDate : new Date();
        const dateStr = formatDateDDMYYYY(predictionDate);

        // If your ephemeris supports date: getPlanets("2026-02-11")
        const planets = await getPlanets(
            qDate ? qDate.toISOString().slice(0, 10) : undefined
        );

        const finalArr = [];

        for (const sign of signs) {
            // generateHoroscope returns localized category keys, so we must map them safely
            const h = generateHoroscope(sign, planets, lang, { period, date: req.query.date });

            // h.sign is localized display sign name (Cancer / कर्क etc.)
            // But for your required format:
            // moonsign = TitleCase English sign (Cancer)
            // sun_sign = lowercase english sign (cancer)
            const sunSignKey = String(sign).toLowerCase();
            const moonSignName = toTitleCase(sunSignKey);

            // In generateHoroscope(), keys are like:
            //   [names.categories.PersonalLife], ...
            // So we can't rely on fixed strings; instead extract by position/order.
            // Safer: just read all values and map them in the same order you generate.
            // But BEST: map using known categories if present in object.
            const keys = Object.keys(h).filter((k) => k !== "sign");

            // Try to pick by known order (based on your generateHoroscope order):
            const personalLife = h[keys[0]] || "";
            const profession = h[keys[1]] || "";
            const health = h[keys[2]] || "";
            const emotions = h[keys[3]] || "";
            const travel = h[keys[4]] || "";
            const luck = h[keys[5]] || "";

            finalArr.push({
                date: dateStr,
                moonsign: moonSignName,
                prediction_date: dateStr,
                sun_sign: sunSignKey,

                personal_life: personalLife,
                profession: profession,
                health: health,
                emotions: emotions,
                travel: travel,
                luck: luck,
            });
        }
        let data1 = {
            horoscopeDatails: finalArr
        }
        // return res.json({ status: true, data: data1 });
        return res.json({ status: true, data: finalArr });
    } catch (error) {
        return res.status(400).json({ status: false, message: error.message });
    }
};
