const DEFAULT_AI_SERVICE_URL = "http://127.0.0.1:8000/analyze-query";

function getAIServiceUrl() {
  const serviceUrl = new URL(
    process.env.AI_SERVICE_URL || DEFAULT_AI_SERVICE_URL,
  );
  const path = serviceUrl.pathname.replace(/\/+$/, "");

  if (!path.endsWith("/analyze-query")) {
    serviceUrl.pathname = `${path}/analyze-query`;
  }

  return serviceUrl.toString();
}

async function generateAnswer({ query, conversationHistory, sourceUrl }) {
  const serviceUrl = getAIServiceUrl();
  const response = await fetch(serviceUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      conversation_history: conversationHistory,
      source_url: sourceUrl || null,
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