import express from "express";
import { scrapeWebsiteController } from "../controllers/scraper.controller.js";

const router = express.Router();

router.get("/learning", (req, res) => {
    res.status(200).json({
        success: true,
        message: "Learning Lizard backend is running",
    });
});

router.post("/learning/scrape", scrapeWebsiteController);

export default router;