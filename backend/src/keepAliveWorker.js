import { setTimeout as delay } from "node:timers/promises";

const intervalMs = 30_000;
const requestTimeoutMs = 10_000;
const endpoints = [
  { name: "AI service", envName: "AI_SERVICE_HEALTH_URL" },
  { name: "Backend", envName: "BACKEND_HEALTH_URL" },
].map(({ name, envName }) => {
  const value = process.env[envName];
  if (!value) {
    throw new Error(`${envName} must be set to the public health endpoint URL`);
  }

  const url = new URL(value);
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error(`${envName} must use HTTP or HTTPS`);
  }

  return { name, url: url.toString() };
});

async function pingEndpoint({ name, url }) {
  try {
    const response = await fetch(url, {
      cache: "no-store",
      signal: AbortSignal.timeout(requestTimeoutMs),
    });
    const status = response.status;
    await response.body?.cancel();

    if (!response.ok) {
      throw new Error(`HTTP ${status}`);
    }

    console.log(`[keep-alive] ${name} responded with HTTP ${status}`);
  } catch (error) {
    console.error(`[keep-alive] ${name} health request failed: ${error.message}`);
  }
}

const shutdown = new AbortController();
for (const signal of ["SIGINT", "SIGTERM"]) {
  process.once(signal, () => shutdown.abort());
}

console.log("[keep-alive] Pinging configured services every 30 seconds");

while (!shutdown.signal.aborted) {
  const nextRunAt = Date.now() + intervalMs;
  await Promise.all(endpoints.map(pingEndpoint));

  if (shutdown.signal.aborted) break;

  try {
    await delay(Math.max(0, nextRunAt - Date.now()), undefined, {
      signal: shutdown.signal,
    });
  } catch (error) {
    if (error.name !== "AbortError") throw error;
  }
}

console.log("[keep-alive] Worker stopped");
