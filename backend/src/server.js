import express from "express";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();

const app = express();

const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Health-check endpoint
app.get("/health", (req, res) => {
  res.status(200).json({
    success: true,
    message: "Reading Lizard backend is running",
    service: "node-backend"
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Node.js server running on port ${PORT}`);
});