// app.js
const express = require("express");
const cors = require("cors");

const app = express();

/**
 * Global middlewares
 */
app.use(cors()); // allow all origins
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

/**
 * Health check (optional but useful)
 */
app.get("/", (req, res) => {
    res.json({
        status: true,
        message: "Server is running"
    });
});

/**
 * API routes
 */
app.use("/api", require("./routes"));

/**
 * 404 handler (important)
 */
app.use((req, res) => {
    res.status(404).json({
        status: false,
        message: "API endpoint not found"
    });
});

module.exports = app;
