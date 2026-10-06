// Base URL of the backend API.
// Change this (or set VITE_API_URL in a .env file) if your backend
// runs somewhere other than http://localhost:3000
export const API_BASE_URL =
  (import.meta.env.VITE_API_URL || "http://localhost:3000").replace(/\/$/, "");
