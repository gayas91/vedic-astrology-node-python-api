function toNumber(value, fieldName) {
    const n = Number(value);
    if (Number.isNaN(n)) {
        throw new Error(`${fieldName} must be a valid number`);
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

function validateMahadasha(value) {
    if (!value) {
        throw new Error("mahadasha is required");
    }
    return value.trim();
}

function validateYoginiAntardashaQuery(query) {
    const dob = validateDate(query.dob);
    const time = validateTime(query.time);
    const lat = toNumber(query.lat, "lat");
    const lon = toNumber(query.lon, "lon");
    const timezone = toNumber(query.timezone, "timezone");
    const mahadasha = validateMahadasha(query.mahadasha);

    return {
        dob,
        time,
        lat,
        lon,
        timezone,
        mahadasha
    };
}

module.exports = {
    validateYoginiAntardashaQuery
};