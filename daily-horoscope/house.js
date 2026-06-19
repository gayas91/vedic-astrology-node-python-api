const { signDegree } = require("./zodiac");

function getHouse(planetDeg, sign) {
    const base = signDegree[sign];     // Aries = 0, Taurus = 30 ...
    let diff = planetDeg - base;

    if (diff < 0) diff += 360;

    return Math.floor(diff / 30) + 1;   // 1–12
}

module.exports = { getHouse };
