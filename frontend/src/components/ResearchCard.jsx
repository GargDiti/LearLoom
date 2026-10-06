import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./ResearchCard.css";

const CHIPS = [
  {
    icon: "⌖",
    title: "Page sections",
    subtitle: "Choose a topic or whole page",
  },
  {
    icon: "✦",
    title: "Source-grounded answers",
    subtitle: "Retrieved from your link",
  },
  {
    icon: "↺",
    title: "Saved conversations",
    subtitle: "Pick up where you left off",
  },
];

function ResearchCard() {
  const [url, setUrl] = useState("");
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    const query = url.trim();
    if (!query) return;
    navigate(isAuthenticated ? "/research" : "/login", {
      state: isAuthenticated
        ? { draft: query }
        : { from: { pathname: "/research", state: { draft: query } } },
    });
  };

  return (
    <div className="research-card-wrap">
      <span className="research-card-badge">✦ AI Research Mode</span>

      <div className="research-card">
        <>
            <h3 className="research-card-title">
              Start your research <span>🦎</span>
            </h3>
              <p className="research-card-subtitle">
                Ask a question or bring a page to explore
            </p>

            <form className="research-card-form" onSubmit={handleSubmit}>
              <div className="research-card-input">
                <span className="research-card-input-icon">🔗</span>
                <input
                  type="text"
                  placeholder="Paste a link or ask a question..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>

              <button type="submit" className="research-card-cta">
                Start Exploring
                <span aria-hidden="true">→</span>
              </button>
            </form>

            <div className="research-card-chips">
              {CHIPS.map((chip) => (
                <div className="research-chip" key={chip.title}>
                  <span className="research-chip-icon">{chip.icon}</span>
                  <div>
                    <p className="research-chip-title">{chip.title}</p>
                    <p className="research-chip-subtitle">{chip.subtitle}</p>
                  </div>
                </div>
              ))}
            </div>
        </>
      </div>
    </div>
  );
}

export default ResearchCard;
