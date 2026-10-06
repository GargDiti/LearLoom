import { API_BASE_URL } from "./config";

async function parseResponse(res) {
  const contentType = res.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await res.json().catch(() => ({}))
    : await res.text().catch(() => "");

  if (!res.ok) {
    const message =
      (data && (data.message || data.error || data.msg)) ||
      (typeof data === "string" && data) ||
      `Request failed (${res.status})`;
    throw new Error(message);
  }

  return data;
}

// POST /api/auth/login  { email, password }
export async function loginRequest({ email, password }) {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return parseResponse(res);
}

// POST /api/auth/register  { name, email, password }
export async function registerRequest({ name, email, password }) {
  const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  return parseResponse(res);
}

// GET /api/auth/profile  (uses stored token)
export async function fetchProfile(token) {
  const res = await fetch(`${API_BASE_URL}/api/auth/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return parseResponse(res);
}
