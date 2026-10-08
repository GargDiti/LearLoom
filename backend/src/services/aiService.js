function getAIServiceUrl() {
  const configuredUrl = process.env.AI_SERVICE_URL;
  const isProduction = process.env.NODE_ENV === "production";
  if (!configuredUrl) {
    throw new Error("AI_SERVICE_URL must be configured with the deployed AI service URL");
  }

  const serviceUrl = new URL(configuredUrl);
  if (
    isProduction
    && ["localhost", "127.0.0.1", "::1", "[::1]"].includes(serviceUrl.hostname)
  ) {
    throw new Error("AI_SERVICE_URL must not point to localhost in production");
  }

  const path = serviceUrl.pathname.replace(/\/+$/, "");

  if (!path.endsWith("/analyze-query")) {
    serviceUrl.pathname = `${path}/analyze-query`;
  }

  return serviceUrl.toString();
}

async function generateAnswer({ query, conversationHistory, sourceUrl, selectedTopic }) {
  const serviceUrl = getAIServiceUrl();
  const response = await fetch(serviceUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      conversation_history: conversationHistory,
      source_url: sourceUrl || null,
      selected_topic: selectedTopic ?? null,
    }),
    signal: AbortSignal.timeout(90000),
  });

  if (!response.ok) {
    throw new Error(`AI service returned HTTP ${response.status}`);
  }

  const result = await response.json();
  if (typeof result.result !== "string" || !result.result.trim()) {
    throw new Error("AI service returned an empty answer");
  }

  return result;
}

const aiService = { generateAnswer };

export { aiService, generateAnswer };
export default aiService;