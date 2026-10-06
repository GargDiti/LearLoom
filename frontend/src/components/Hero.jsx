import ResearchCard from "./ResearchCard";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import heroLizard from "../assets/hero-lizard-cutout.png";
import "./Hero.css";

function Hero() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const startResearch = () => {
    navigate(isAuthenticated ? "/research" : "/login", {
      state: isAuthenticated ? undefined : { from: { pathname: "/research" } },
    });
  };

  return (
    <section className="hero">
      <div className="hero-left">
        <h1 className="hero-heading">
          Explore. Read.
          <br />
          Understand <span className="hero-heading-accent">Everything.</span>
        </h1>

        <p className="hero-copy">
          Turn a webpage or a question into a guided research conversation.
          Explore page sections, get source-grounded answers, and follow up
          naturally.
        </p>

        <div className="hero-actions" id="how-it-works">
          <button className="hero-btn-primary" onClick={startResearch}>
            Start Researching <span aria-hidden="true">→</span>
          </button>
          <button className="hero-btn-secondary" onClick={() => document.getElementById("features")?.scrollIntoView({ behavior: "smooth" })}>
            <span aria-hidden="true">↓</span> Explore features
          </button>
        </div>

        <div className="hero-social-proof">
          <span className="hero-proof-mark" aria-hidden="true">✦</span>
          <p className="hero-social-text">General learning · Website research · Saved chats</p>
        </div>
      </div>

      <div className="hero-right">
        <div className="hero-blob" aria-hidden="true" />
        <ResearchCard />
        <img
          src={heroLizard}
          alt="Reading Lizard mascot reading a book"
          className="hero-lizard"
        />
      </div>
    </section>
  );
}

export default Hero;
