const kundliMatchService = require("./kundliMatch.service");
const translateMatchData = require("./kundliMatch.translate");
const moment = require("moment");

function requireStr(body, key) {
    const v = body?.[key];
    if (!v || typeof v !== "string" || !v.trim()) {
        throw new Error(`${key} is required`);
    }
    return v.trim();
}

function requireDateYMD(value, key) {
    const m = moment(value, "YYYY-MM-DD", true);
    if (!m.isValid()) throw new Error(`${key} must be YYYY-MM-DD`);
    return m.format("DD-MM-YYYY"); // for python
}

function requireTime24(value, key) {
    const m = moment(value, "HH:mm:ss", true);
    if (!m.isValid()) throw new Error(`${key} must be 24-hour HH:mm:ss (e.g. 21:14:00)`);
    return m.format("hh:mm A"); // for python (%I:%M %p)
}

module.exports = async (req, res) => {
    try {
        //  important: do NOT force only hi/en here if you want future languages
        // your i18n loader can fallback automatically
        const lang = typeof req.body.language === "string" ? req.body.language : "en";
        
        const male_dob = requireDateYMD(requireStr(req.body, "m_dob"), "m_dob");
        const male_birth_time = requireTime24(requireStr(req.body, "m_birth_time"), "m_birth_time");

        const female_dob = requireDateYMD(requireStr(req.body, "f_dob"), "f_dob");
        const female_birth_time = requireTime24(requireStr(req.body, "f_birth_time"), "f_birth_time");

        const payload = {
            // female
            f_name: requireStr(req.body, "f_name"),
            f_dob: female_dob,
            f_birth_time: female_birth_time,
            f_pob: requireStr(req.body, "f_pob"),
            f_lat: requireStr(req.body, "f_lat"),
            f_long: requireStr(req.body, "f_long"),
            f_timezone: requireStr(req.body, "f_timezone"),

            // male
            m_name: requireStr(req.body, "m_name"),
            m_dob: male_dob,
            m_birth_time: male_birth_time,
            m_pob: requireStr(req.body, "m_pob"),
            m_lat: requireStr(req.body, "m_lat"),
            m_long: requireStr(req.body, "m_long"),
            m_timezone: requireStr(req.body, "m_timezone"),

            language: lang,
        };

        // Service may return either:
        // A) { status:true, data: {...matchData...} }
        // B) {...matchData...}
        const serviceResp = await kundliMatchService(payload);

        const matchData = (serviceResp && serviceResp.data && typeof serviceResp.data === "object")
            ? serviceResp.data
            : serviceResp;

        const translated = translateMatchData(matchData, lang);

        return res.json({ status: true, data: translated });
    } catch (e) {
        return res.status(400).json({ status: false, message: e.message });
    }
};