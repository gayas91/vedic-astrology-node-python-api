// function getAspect(a, b) {
//     let d = Math.abs(a - b);
//     if (d > 180) d = 360 - d;

//     if (d < 8) return "conjunction";
//     if (d > 52 && d < 68) return "sextile";
//     if (d > 82 && d < 98) return "square";
//     if (d > 112 && d < 128) return "trine";
//     if (d > 172 && d < 188) return "opposition";

//     return "none";
// }

// module.exports = { getAspect };

const aspects = [
    { name: "conjunction", angle: 0, orb: 8 },
    { name: "sextile", angle: 60, orb: 6 },
    { name: "square", angle: 90, orb: 8 },
    { name: "trine", angle: 120, orb: 8 },
    { name: "opposition", angle: 180, orb: 8 }
];

function getAspect(a, b) {
    let d = Math.abs(a - b);
    if (d > 180) d = 360 - d;

    for (const aspect of aspects) {
        if (Math.abs(d - aspect.angle) <= aspect.orb) return aspect.name;
    }

    return "none";
}

module.exports = { getAspect };