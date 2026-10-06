import { API_BASE_URL } from "./config";

async function request(path, { token, method = "GET", body } = {}) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new Error("Could not reach the LearnLoom backend. Check that it is running.");
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.message || `Request failed (${response.status})`);
  }
  return data;
}

export function listConversations(token) {
  return request("/api/conversations", { token });
}

export function createConversation(token, title) {
  return request("/api/conversations", {
    token,
    method: "POST",
    body: { title },
  });
}

export function getConversation(token, conversationId) {
  return request(`/api/conversations/${conversationId}`, { token });
}

export function deleteConversation(token, conversationId) {
  return request(`/api/conversations/${conversationId}`, {
    token,
    method: "DELETE",
  });
}

export function sendConversationMessage(token, conversationId, message, selectedTopic) {
  const body = { message };
  if (selectedTopic !== undefined && selectedTopic !== null) {
    body.selectedTopic = selectedTopic;
  }
  return request(`/api/conversations/${conversationId}/messages`, {
    token,
    method: "POST",
    body,
  });
}