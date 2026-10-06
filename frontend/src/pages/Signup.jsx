import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import logo from "../components/logo.png";
import heroLizard from "../assets/hero-lizard-cutout.png";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

function Signup() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setError("");

    if (!name || !email || !password) {
      setError("Please fill in your name, email, and password.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 8) {
      setError("Your password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      await register({ name, email, password });
      const destination = location.state?.from;
      navigate(destination?.pathname || "/", {
        replace: true,
        state: destination?.state,
      });
    } catch (err) {
      setError(err.message || "Sign up failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-topbar">
        <Link to="/" className="auth-topbar-logo">
          <img src={logo} alt="Reading Lizard" style={{ width: 140, height: "auto", borderRadius: 0 }} />
        </Link>
        <div className="auth-topbar-switch">
          Already have an account? <Link to="/login">Login</Link>
        </div>
      </div>

      <div className="auth-body">
        <div className="auth-visual">
          <span className="auth-visual-leaf one" aria-hidden="true" />
          <span className="auth-visual-leaf two" aria-hidden="true" />
          <div className="auth-visual-content">
            <h1>
              Join us!
              <br />
              Start your own <span className="accent">research journey.</span>
            </h1>
            <p>
              Create an account to save your research, explore new ideas, and
              uncover knowledge with AI.
            </p>
          </div>
          <img src={heroLizard} alt="" className="auth-visual-lizard" aria-hidden="true" />
        </div>

        <div className="auth-panel">
          <div className="auth-card">
            <div className="auth-card-icon" aria-hidden="true">🦎</div>
            <h2>
              Create your <span className="accent">account</span>
            </h2>
            <p className="auth-card-subtitle">
              Sign up to start exploring with Reading Lizard
            </p>

            <form className="auth-form" onSubmit={handleSubmit}>
              {error && <div className="auth-error">{error}</div>}

              <div className="auth-field">
                <label htmlFor="signup-name">Full name</label>
                <div className="auth-input">
                  <span className="auth-input-icon" aria-hidden="true">👤</span>
                  <input
                    id="signup-name"
                    type="text"
                    placeholder="Enter your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    autoComplete="name"
                    required
                  />
                </div>
              </div>

              <div className="auth-field">
                <label htmlFor="signup-email">Email address</label>
                <div className="auth-input">
                  <span className="auth-input-icon" aria-hidden="true">✉</span>
                  <input
                    id="signup-email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoComplete="email"
                    required
                  />
                </div>
              </div>

              <div className="auth-field">
                <label htmlFor="signup-password">Password</label>
                <div className="auth-input">
                  <span className="auth-input-icon" aria-hidden="true">🔒</span>
                  <input
                    id="signup-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="new-password"
                    minLength={8}
                    required
                  />
                  <button
                    type="button"
                    className="auth-input-toggle"
                    onClick={() => setShowPassword((s) => !s)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? "🙈" : "👁"}
                  </button>
                </div>
              </div>

              <div className="auth-field">
                <label htmlFor="signup-confirm">Confirm password</label>
                <div className="auth-input">
                  <span className="auth-input-icon" aria-hidden="true">🔒</span>
                  <input
                    id="signup-confirm"
                    type={showPassword ? "text" : "password"}
                    placeholder="Re-enter your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    autoComplete="new-password"
                    required
                  />
                </div>
              </div>

              <button type="submit" className="auth-submit" disabled={loading}>
                {loading ? "Creating account..." : "Sign Up"} <span aria-hidden="true">→</span>
              </button>
            </form>

            <div className="auth-footnote">
              <span aria-hidden="true">🛡</span> Your account is protected with a secure sign-in.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Signup;
