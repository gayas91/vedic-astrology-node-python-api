const { julian, planetposition } = require("astronomia");
const { DateTime } = require("luxon");

// Load VSOP87 datasets
const earth = require("astronomia/data/vsop87Bearth");
const mercury = require("astronomia/data/vsop87Bmercury");
const venus = require("astronomia/data/vsop87Bvenus");
const mars = require("astronomia/data/vsop87Bmars");
const jupiter = require("astronomia/data/vsop87Bjupiter");
const saturn = require("astronomia/data/vsop87Bsaturn");

const planetsData = {
    Sun: earth,      // Sun's apparent position is opposite of Earth
    Mercury: mercury,
    Venus: venus,
    Mars: mars,
    Jupiter: jupiter,
    Saturn: saturn
};

async function toJD(testDate = null) {
    // const d = DateTime.utc();
    const d = testDate ? DateTime.fromISO(testDate, { zone: "utc" }) : DateTime.utc();
    console.log("Ephemeris Date:", d.toISODate());

    return julian.CalendarGregorianToJD(
        d.year,
        d.month,
        d.day + d.hour / 24
    );
}

async function getLongitude(dataset, jd) {
    const p = new planetposition.Planet(dataset.default);
    const pos = p.position(jd);
    return ((pos.lon * 180) / Math.PI + 360) % 360;
}

async function getPlanets(testDate = null) {
    const jd = await toJD(testDate);
    const res = {};

    for (const p in planetsData) {
        res[p] = await getLongitude(planetsData[p], jd);
    }

    // Convert Earth → Sun longitude
    res.Sun = (res.Sun + 180) % 360;

    // Moon (fast synodic approximation – enough for daily horoscope)
    res.Moon = (res.Sun + 13.176396 * (jd % 27.321582)) % 360;

    return res;
}

module.exports = { getPlanets };
