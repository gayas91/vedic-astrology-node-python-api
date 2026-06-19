const router = require("express").Router();
const { DateTime } = require("luxon");
const getPanchang = require("../panchang/js/panchang.service");
const getDailyPanchang = require("../panchang/js/dailyPanchang.service");
const planetsExplaination = require("../panchang/js/planetsExplaination.service.js");
const buildAvakhada = require("../avakhada/js/avakhada.service");
const getSubVdasha = require("../panchang/js/subVdasha.service");
const getPratyantarVdasha = require("../panchang/js/pratyantarVdasha.service");
const getSookshmaVdasha = require("../panchang/js/sookshmaVdasha.service");
const getPranVdasha = require("../panchang/js/pranVdasha.service");
const dailyHoroscope = require('../daily-horoscope/index.js');
const getDailyUpdateDasha = require("../daily-dasha/js/daily_update_dasha.js");
const getAiAstro = require("../daily-dasha/js/ai_astro.js")
const getKPChart = require("../kp/js/kp.service");
const { validateKPQuery } = require("../kp/js/kp.helpers");
const getAshtakavarga = require("../ashtakavarga/js/ashtakavarga.service");
const { validateAshtakavargaQuery } = require("../ashtakavarga/js/ashtakavarga.helpers");
const getSouthCharts = require("../south-chart/js/southChart.service");
const { validateSouthChartQuery } = require("../south-chart/js/southChart.helpers");
const getYoginiDasha = require("../yogini-dasha/js/yogini.service");
const { validateYoginiQuery } = require("../yogini-dasha/js/yogini.helpers");
const getYoginiAntardasha = require("../yogini-dasha/js/yogini.antardasha.service");
const { validateYoginiAntardashaQuery } = require("../yogini-dasha/js/yogini.antardasha.helpers");
const getYoginiPratyantardasha = require("../yogini-dasha/js/yogini_pratyantardasha");
const getYoginiSukshma = require("../yogini-dasha/js/yogini_sukshma");
const { getShadbala, getBhavbala } = require("../shadbala_bhavbala/js/shadbalaService");
const { getVarshphal } = require("../lal-kitab-varshphal/js/varshphalService");
const getVarshphalNew = require("../panchang/js/lalKitab.service.js");

const { getCalender } = require("../festival-calendar/js/calendarService");
const getTransit = require("../panchang/js/transit.service");
const getFiveElements = require("../five-elements/js/elements.js");


const ZONE = "Asia/Kolkata";
function isoDateIST(dt) {
    return dt.setZone(ZONE).toISODate(); // YYYY-MM-DD
}

function withFixedDate(getISODateFn) {
    return (req, res, next) => {
        // keep lang as-is, just set date
        req.query = { ...req.query, date: getISODateFn() };
        return dailyHoroscope(req, res, next);
    };
}

function startOfWeekMondayIST() {
    const now = DateTime.now().setZone(ZONE);
    // Luxon weekday: Monday=1 ... Sunday=7
    return now.minus({ days: now.weekday - 1 }).startOf("day");
}

function withFixedDateAndPeriod(getISODateFn, period) {
    return (req, res, next) => {
        req.query = { ...req.query, date: getISODateFn(), period };
        return dailyHoroscope(req, res, next);
    };
}

function requireStart(req, res) {
    const start = req.query.start;
    if (!start || typeof start !== "string" || !start.trim()) {
        res.status(400).json({
            status: false,
            message: "Query param 'start' is required. Example: ?start=25-05-2064 01:28",
        });
        return null;
    }
    return start.trim();
}

router.post("/kundli-details", async (req, res) => {
    try {
        const lang = req.query.lang === "hi" || req.body.lang === "hi" ? "hi" : "en";

        const { dob, time, lat, lon, timezone } = req.body;
        if (!dob || !time || lat == null || lon == null) {
            return res.status(400).json({
                status: false,
                message: "dob, time, lat, lon are required",
            });
        }
        const varshaphal_year = req.body.varshaphal_year ? Number(req.body.varshaphal_year) : new Date().getFullYear();

        const result = await getPanchang({
            datetime: `${dob} ${time}`,
            lat,
            lon,
            timezone: timezone || "Asia/Kolkata",
            varshaphal_year,
            avakhada_ref_offset_hours: req.body.avakhada_ref_offset_hours || 0,
            include_debug: !!req.body.include_debug,
            include_offset_sweep: !!req.body.include_offset_sweep,
            lang,
        });

        const basic_details = {
            name: req.body.name,
            gender: req.body.gender,
            dob,
            birth_time: time,
            birth_place: req.body.birth_place,
            lat: lat,
            long: lon,
            timezone: "Asia/Kolkata",
        };

        // Avakhada from result.panchang keys (no panchangObj usage)
        const avakhada = buildAvakhada({
            ascendant_sign: result.ascendant_sign,
            moon_sign: result.moon_sign,

            nak_name: result.panchang?.nakshatra?.details?.nak_name,
            nak_number: result.panchang?.nakshatra?.details?.nak_number,
            charan: result.panchang?.nakshatra?.details?.charan,

            tithi_name: result.panchang?.tithi?.details?.tithi_name,
            karan_name: result.panchang?.karan?.details?.karan_name,
            yog_name: result.panchang?.yog?.details?.yog_name,

            lang,
        });

        // result.basic_details = basic_details;
        result.astro_details = avakhada;

        //  result now contains panchang (in exact sample format)
        res.json({ status: true, data: result });
    } catch (e) {
        res.status(500).json({ status: false, message: e.message });
    }
});

router.post("/get-varshaphal", async (req, res) => {
    try {
        const lang = req.query.lang === "hi" || req.body.lang === "hi" ? "hi" : "en";
        const { dob, time, lat, lon, timezone } = req.body;
        if (!dob || !time || lat == null || lon == null) {
            return res.status(400).json({
                status: false,
                message: "dob, time, lat, lon are required",
            });
        }
        const varshaphal_year = req.body.varshaphal_year ? Number(req.body.varshaphal_year) : new Date().getFullYear();

        const result = await getPanchang({
            datetime: `${dob} ${time}`,
            lat,
            lon,
            timezone: timezone || "Asia/Kolkata",
            varshaphal_year,
            avakhada_ref_offset_hours: req.body.avakhada_ref_offset_hours || 0,
            include_debug: !!req.body.include_debug,
            include_offset_sweep: !!req.body.include_offset_sweep,
            lang,
        });

        res.json({ status: true, data: result.Vershful });
    } catch (e) {
        res.status(500).json({ status: false, message: e.message });
    }
});

// for anttardasha
router.get("/sub_vdasha/:planet", async (req, res) => {
    try {
        const start = requireStart(req, res);
        if (!start) return;

        const planet = req.params.planet;
        const lang = req.query.lang === "hi" ? "hi" : "en"
        const result = await getSubVdasha(planet, start, lang);
        res.json({ status: true, data: result });
    } catch (e) {
        res.status(400).json({ status: false, message: e.message });
    }
});

// for pratyantar dasha
router.get("/pratyantar_vdasha/:maha/:antar", async (req, res) => {
    try {
        const start = requireStart(req, res);
        if (!start) return;

        const { maha, antar } = req.params;
        const lang = req.query.lang === "hi" ? "hi" : "en";
        const result = await getPratyantarVdasha(maha, antar, start, lang);
        res.json({ status: true, data: result });
    } catch (e) {
        res.status(400).json({ status: false, message: e.message });
    }
});

// for sookshma dasha
router.get("/sookshma_vdasha/:maha/:antar/:pratyantar", async (req, res) => {
    try {
        const start = requireStart(req, res);
        if (!start) return;

        const { maha, antar, pratyantar } = req.params;
        const lang = req.query.lang === "hi" ? "hi" : "en";
        const result = await getSookshmaVdasha(maha, antar, pratyantar, start, lang);
        res.json({ status: true, data: result });
    } catch (e) {
        res.status(400).json({ status: false, message: e.message });
    }
});

// for pran dasha
router.get("/pran_vdasha/:maha/:antar/:pratyantar/:sookshma", async (req, res) => {
    try {
        const start = requireStart(req, res);
        if (!start) return;

        const { maha, antar, pratyantar, sookshma } = req.params;
        const lang = req.query.lang === "hi" ? "hi" : "en";
        const result = await getPranVdasha(maha, antar, pratyantar, sookshma, start, lang);
        res.json({ status: true, data: result });
    } catch (e) {
        res.status(400).json({ status: false, message: e.message });
    }
});

// for daily horoscope
router.get('/own-daily-horoscope', dailyHoroscope);
router.get(
    "/own-horoscope-today",
    withFixedDate(() => isoDateIST(DateTime.now()))
);
router.get(
    "/own-horoscope-tomorrow",
    withFixedDate(() => isoDateIST(DateTime.now().plus({ days: 1 })))
);

router.get(
    "/own-horoscope-yesterday",
    withFixedDate(() => isoDateIST(DateTime.now().minus({ days: 1 })))
);
router.get(
    "/own-horoscope-week",
    withFixedDateAndPeriod(() => isoDateIST(startOfWeekMondayIST()), "week")
);

router.get(
    "/own-horoscope-month",
    withFixedDateAndPeriod(() => isoDateIST(DateTime.now().setZone(ZONE).startOf("month")), "month")
);

router.get(
    "/own-horoscope-year",
    withFixedDateAndPeriod(() => isoDateIST(DateTime.now().setZone(ZONE).startOf("year")), "year")
);

// for kundli-matching
const kundliMatch = require("../kundli-match/js/kundliMatch.controller");
router.post("/kundli-matching", kundliMatch);

// For Get Panchang Details
router.post("/get-panchang-details", async (req, res) => {
    try {
        const lang = req.query.lang === "hi" || req.body.lang === "hi" ? "hi" : "en";

        const { dob, time, lat, lon, timezone } = req.body;
        if (lat == null || lon == null) {
            return res.status(400).json({
                status: false,
                message: "dob, time, lat, lon are required",
            });
        }
        const varshaphal_year = new Date().getFullYear();

        const result = await getDailyPanchang({
            datetime: `${dob} ${time}`,
            lat,
            lon,
            timezone: timezone || "Asia/Kolkata",
            varshaphal_year,
            lang,
        });

        //  result now contains panchang (in exact sample format)
        res.json({ status: true, data: result.panchang });
    } catch (e) {
        res.status(500).json({ status: false, message: e.message });
    }
});

router.post("/get-daily-dasha", async (req, res) => {
    try {
        const lang = req.query.lang === "hi" || req.body.lang === "hi" ? "hi" : "en";

        const { dob, birth_time, lat, lon } = req.body;
        if (!dob || !birth_time || lat == null || lon == null) {
            return res.status(400).json({
                status: false,
                message: "dob, birth_time, lat, lon are required",
            });
        }

        const result = await getDailyUpdateDasha({
            dob: dob,
            birth_time: birth_time,
            lat: lat,
            lon: lon,
            lang: "en",
        });

        res.json({ status: true, data: result });
    } catch (e) {
        res.status(500).json({ status: false, message: e.message });
    }
});

router.post("/get-ai-astro", async (req, res) => {
    try {
        const lang = req.query.lang === "hi" || req.body.lang === "hi" ? "hi" : "en";

        const { dob, birth_time, lat, lon } = req.body;
        if (!dob || !birth_time || lat == null || lon == null) {
            return res.status(400).json({
                status: false,
                message: "dob, birth_time, lat, lon are required",
            });
        }

        const result = await getAiAstro({
            dob: dob,
            birth_time: birth_time,
            lat: lat,
            lon: lon,
            lang: "en",
        });

        res.json({ status: true, data: result });
    } catch (e) {
        res.status(500).json({ status: false, message: e.message });
    }
});


// KP
router.get("/kp-details", async (req, res) => {
    try {
        const payload = validateKPQuery(req.query);
        const result = await getKPChart(payload);

        return res.json({
            status: true,
            data: result
        });
    } catch (error) {
        return res.status(500).json({
            status: false,
            message: error.message
        });
    }
});

// Ashtakavarga
router.get("/ashtakavarga-details", async (req, res) => {
    try {
        const payload = validateAshtakavargaQuery(req.query);
        const result = await getAshtakavarga(payload);

        return res.json({
            status: true,
            data: result
        });
    } catch (error) {
        return res.status(500).json({
            status: false,
            message: error.message
        });
    }
});

// South-Chart
router.get("/south-chart", async (req, res) => {
    try {
        const payload = validateSouthChartQuery(req.query);
        const result = await getSouthCharts(payload);

        return res.json({
            status: true,
            data: result
        });
    } catch (error) {
        return res.status(500).json({
            status: false,
            message: error.message
        });
    }
});

// Yogini-Dasha (Mahadasha)
router.get("/yogini-dasha", async (req, res) => {
    try {
        const payload = validateYoginiQuery(req.query);
        const result = await getYoginiDasha(payload);

        return res.json({
            status: true,
            data: result
        });
    } catch (error) {
        return res.status(500).json({
            status: false,
            message: error.message
        });
    }
});

// Yogini-Dasha -> Antardasha
router.get("/yogini-dasha/antardasha", async (req, res) => {
    try {
        const payload = validateYoginiAntardashaQuery(req.query);
        const result = await getYoginiAntardasha(payload);

        return res.json({
            status: true,
            data: result
        });
    } catch (error) {
        return res.status(500).json({
            status: false,
            message: error.message
        });
    }
});

// Yogini-Dasha -> Pratyantardasha
router.get("/yogini-dasha/pratyantardasha", async (req, res) => {
    try {
        const { dob, time, lat, lon, timezone, mahadasha, antardasha } = req.query;

        if (!dob || !time || !timezone || !mahadasha || !antardasha) {
            return res.status(400).json({
                status: false,
                message: "dob, time, timezone, mahadasha and antardasha are required"
            });
        }

        const result = await getYoginiPratyantardasha({
            dob,
            time,
            lat: lat ? Number(lat) : null,
            lon: lon ? Number(lon) : null,
            timezone: Number(timezone),
            mahadasha,
            antardasha
        });

        return res.json({
            status: true,
            data: result
        });
    } catch (e) {
        return res.status(500).json({
            status: false,
            message: e.message
        });
    }
});

// Yogini-Dasha -> Sukshmadasha
router.get("/yogini-dasha/sukshma", async (req, res) => {
    try {
        const { dob, time, lat, lon, timezone, mahadasha, antardasha, pratyantardasha } = req.query;

        if (!dob || !time || !timezone || !mahadasha || !antardasha || !pratyantardasha) {
            return res.status(400).json({
                status: false,
                message: "dob, time, timezone, mahadasha, antardasha and pratyantardasha are required"
            });
        }

        const result = await getYoginiSukshma({
            dob,
            time,
            lat: lat ? Number(lat) : null,
            lon: lon ? Number(lon) : null,
            timezone: Number(timezone),
            mahadasha,
            antardasha,
            pratyantardasha
        });

        return res.json({
            status: true,
            data: result
        });
    } catch (e) {
        return res.status(500).json({
            status: false,
            message: e.message
        });
    }
});

// Plantes Explaination
router.post("/plantes-explaination", async (req, res) => {
    try {
        const lang = req.query.lang === "hi" || req.body.lang === "hi" ? "hi" : "en";

        const { dob, time, lat, lon, timezone } = req.body;
        if (!dob || !time || lat == null || lon == null) {
            return res.status(400).json({
                status: false,
                message: "dob, time, lat, lon are required",
            });
        }
        const varshaphal_year = req.body.varshaphal_year ? Number(req.body.varshaphal_year) : new Date().getFullYear();

        const result = await planetsExplaination({
            datetime: `${dob} ${time}`,
            lat,
            lon,
            timezone: timezone || "Asia/Kolkata",
            varshaphal_year,
            avakhada_ref_offset_hours: req.body.avakhada_ref_offset_hours || 0,
            include_debug: !!req.body.include_debug,
            include_offset_sweep: !!req.body.include_offset_sweep,
            lang,
        });

        //  result now contains panchang (in exact sample format)
        res.json({ status: true, data: result });
    } catch (e) {
        res.status(500).json({ status: false, message: e.message });
    }
});

/* -----------------------------
  SHADBALA API
------------------------------ */
router.get("/shadbala", async (req, res) => {
    try {
        const { dob, time, lat, lon } = req.query;

        if (!dob || !time || !lat || !lon) {
            return res.status(400).json({
                status: false,
                message: "dob, time, lat and lon are required"
            });
        }

        const result = await getShadbala({
            dob,
            time,
            lat: Number(lat),
            lon: Number(lon)
        });

        return res.json({
            status: true,
            data: result
        });

    } catch (e) {
        return res.status(500).json({
            status: false,
            message: e.message
        });
    }
});


/* -----------------------------
  BHAVBALA API
------------------------------ */
router.get("/bhavbala", async (req, res) => {
    try {
        const { dob, time, lat, lon } = req.query;

        if (!dob || !time || !lat || !lon) {
            return res.status(400).json({
                status: false,
                message: "dob, time, lat and lon are required"
            });
        }

        const result = await getBhavbala({
            dob,
            time,
            lat: Number(lat),
            lon: Number(lon)
        });

        return res.json({
            status: true,
            data: result
        });

    } catch (e) {
        return res.status(500).json({
            status: false,
            message: e.message
        });
    }
});

/* -----------------------------
  Laal Kitab Varshphal
------------------------------ */
router.post("/lal-kitab-varshphal-old", async (req, res) => {
    try {
        const result = await getVarshphal(req.body);

        if(result.status == true) {
            res.json({
                status: true,
                data: result
            });
        } else {
            res.json({
                status: false,
                message: result.message
            });
        }
        
    } catch (err) {
        res.json({
            status: false,
            message: err.message
        });
    }
});

router.post("/lal-kitab-varshphal", async(req,res)=>{

        try{
            let params = req.body;
            params.datetime = `${req.body.dob} ${req.body.time}`;
            const result = await getVarshphalNew(req.body);

            res.json(result);
        } catch(err){
            res.json({status:false, message:err.message });
        }

    }
);
/* -----------------------------
  Festival Calender
------------------------------ */
router.post("/get-festival-calender", async (req, res) => {
    try {
        const result = await getCalender(req.body);
        if(result.status == "success") {
            res.json({
                status: true,
                data: result.data
            });
        } else {
            res.json({
                status: false,
                message: "Error, Please contact to developr"
            });
        }
        
    } catch (err) {
        res.json({
            status: false,
            message: err.message
        });
    }
});

/* -----------------------------
  Transit Chart 
------------------------------ */
router.post("/transit-chart", async (req, res) => {
    try {
        const lang = req.query.lang === "hi" || req.body.lang === "hi" ? "hi" : "en";

        const { dob, time, lat, lon, timezone } = req.body;
        if (!dob || !time || lat == null || lon == null) {
            return res.status(400).json({
                status: false,
                message: "dob, time, lat, lon are required",
            });
        }
        const result = await getTransit({
            datetime: `${dob} ${time}`,
            lat,
            lon,
            timezone: timezone || "Asia/Kolkata",
            lang,
        });

        res.json({ status: true, data: result });
    } catch (e) {
        res.status(500).json({ status: false, message: e.message });
    }
});

/* -----------------------------
  5 Elements 
------------------------------ */
router.post("/four-elements", async (req, res) => {
    try {
        const lang = req.query.lang === "hi" || req.body.lang === "hi" ? "hi" : "en";

        const { dob, time, lat, lon, timezone } = req.body;
        if (!dob || !time || lat == null || lon == null) {
            return res.status(400).json({
                status: false,
                message: "dob, time, lat, lon are required",
            });
        }

        const result = await getFiveElements({
            dob: dob,
            time: time.slice(0, 5), // "19:00"
            lat,
            lon,
            timezone: timezone || "Asia/Kolkata"
        });

        res.json({ status: true, data: result });
    } catch (e) {
        res.status(500).json({ status: false, message: e.message });
    }
});


module.exports = router;


