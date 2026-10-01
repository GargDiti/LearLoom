import dotenv from "dotenv";
import { fileURLToPath } from "node:url";

import app from "./app.js";
import connectDB from "./config/db.js";

dotenv.config({ path: fileURLToPath(new URL("./.env", import.meta.url)) });

const PORT = process.env.PORT || 3000;

function startServer() {
  const server = app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);

    connectDB().catch((error) => {
      console.error("MongoDB startup connection failed:", error.message);
    });
  });

  server.on("error", (error) => {
    console.error("Server startup failed:", error.message);
    process.exit(1);
  });
}

startServer();