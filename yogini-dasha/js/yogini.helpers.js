function toNumber(value, fieldName) {
    const n = Number(value);
    if (Number.isNaN(n)) {
        throw new Error(`${fieldName} must be a valid number`);
    }
    return n;
}

function toInt(value, fieldName, defaultValue) {
    if (value === undefined || value === null || value === "") {
        return defaultValue;
    }
    const n = parseInt(value, 10);
    if (Number.isNaN(n)) {
        throw new Error(`${fieldName} must be a valid integer`);
    }
    return n;
}

function validateDate(dateStr) {
    if (!dateStr || !/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        throw new Error("dob must be in YYYY-MM-DD format");
    }
    return dateStr;
}

function validateTime(timeStr) {
    if (!timeStr || !/^\d{2}:\d{2}(:\d{2})?$/.test(timeStr)) {
        throw new Error("time must be in HH:mm or HH:mm:ss format");
    }
    return timeStr.length === 5 ? `${timeStr}:00` : timeStr;
}

function validateYoginiQuery(query) {
    const dob = validateDate(query.dob);
    const time = validateTime(query.time);
    const lat = toNumber(query.lat, "lat");
    const lon = toNumber(query.lon, "lon");
    const timezone = toNumber(query.timezone, "timezone");
    const years = toInt(query.years, "years", 120);

    if (lat < -90 || lat > 90) {
        throw new Error("lat must be between -90 and 90");
    }

    if (lon < -180 || lon > 180) {
        throw new Error("lon must be between -180 and 180");
    }

    if (years < 1 || years > 200) {
        throw new Error("years must be between 1 and 200");
    }

    return {
        dob,
        time,
        lat,
        lon,
        timezone,
        years
    };
}

module.exports = {
    validateYoginiQuery
};