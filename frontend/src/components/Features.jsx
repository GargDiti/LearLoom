import "./Features.css";

const FEATURES = [
  {
    icon: "🌐",
    title: "Smart Web Crawling",
    text: "Bring a webpage into your research and get answers grounded in its content.",
  },
  {
    icon: "📄",
    title: "Ask Any Question",
    text: "Explore a topic directly, even when you do not have a website to share.",
  },
  {
    icon: "✦",
    title: "Choose a Topic",
    text: "Select a section from a scraped page and focus your next question.",
  },
  {
    icon: "💬",
    title: "Conversation Memory",
    text: "Ask follow-ups naturally; recent turns stay with your saved conversation.",
  },
  {
    icon: "🗂",
    title: "Saved Research",
    text: "Return to your conversations and continue where you left off.",
  },
  {
    icon: "🔐",
    title: "Private Workspace",
    text: "Your saved conversations are available only to your signed-in account.",
  },
];

function Features() {
  return (
    <section className="features" id="features">
      <h2>
        Powerful features for deep understanding
        <span className="features-underline" />
      </h2>

      <div className="features-grid">
        {FEATURES.map((f) => (
          <div className="feature-card" key={f.title}>
            <div className="feature-icon">{f.icon}</div>
            <h3>{f.title}</h3>
            <p>{f.text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Features;
