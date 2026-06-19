const signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

const signDegree = {
    Aries: 0,
    Taurus: 30,
    Gemini: 60,
    Cancer: 90,
    Leo: 120,
    Virgo: 150,
    Libra: 180,
    Scorpio: 210,
    Sagittarius: 240,
    Capricorn: 270,
    Aquarius: 300,
    Pisces: 330
};

const rulers = {
    Aries: "Mars",
    Taurus: "Venus",
    Gemini: "Mercury",
    Cancer: "Moon",
    Leo: "Sun",
    Virgo: "Mercury",
    Libra: "Venus",
    Scorpio: "Mars",
    Sagittarius: "Jupiter",
    Capricorn: "Saturn",
    Aquarius: "Saturn",
    Pisces: "Jupiter"
};

module.exports = { signs, signDegree, rulers };
