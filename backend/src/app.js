import express from "express";
import cors from "cors";
import mongoose from "mongoose";

const app = express();

app.use(cors());
app.use(express.json());

app.get("/api/health", (req, res) => {
  res.json({
    success: true,
    status: "ok",
    message: "LearnLoom backend is running",
  });
});

app.get("/api/health/ready", (req, res) => {
  const mongoStates = ["disconnected", "connected", "connecting", "disconnecting"];
  const mongoStatus = mongoStates[mongoose.connection.readyState] ?? "unknown";
  const ready = mongoStatus === "connected";

  res.status(ready ? 200 : 503).json({
    success: ready,
    status: ready ? "ready" : "not_ready",
    checks: { mongodb: mongoStatus },
  });
});

import authRoutes from "./routes/authRoutes.js";
app.use("/api/auth", authRoutes);
export default app;