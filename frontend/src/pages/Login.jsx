import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import logo from "../components/logo.png";
import heroLizard from "../assets/hero-lizard-cutout.png";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setError("");

    if (!email || !password) {
      setError("Please enter both your email and password.");
      return;
    }

    setLoading(true);
    try {
      await login({ email, password });
      const destination = location.state?.from;
      navigate(destination?.pathname || "/", {
        replace: true,
        state: destination?.state,
      });
    } catch (err) {
      setError(err.message || "Login failed. Please check your credentials.");
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
          Don't have an account? <Link to="/signup">Sign Up</Link>
        </div>
      </div>

      <div className="auth-body">
        <div className="auth-visual">
          <span className="auth-visual-leaf one" aria-hidden="true" />
          <span className="auth-visual-leaf two" aria-hidden="true" />
          <div className="auth-visual-content">
            <h1>
              Welcome back!
              <br />
              Login to continue your <span className="accent">research journey.</span>
            </h1>
            <p>
              Access your saved research, explore new ideas, and uncover
              knowledge with AI.
            </p>
          </div>
          <img src={heroLizard} alt="" className="auth-visual-lizard" aria-hidden="true" />
        </div>

        <div className="auth-panel">
          <div className="auth-card">
            <div className="auth-card-icon" aria-hidden="true">🔒</div>
            <h2>
              Login to <span className="accent">Reading Lizard</span>
            </h2>
            <p className="auth-card-subtitle">
              Enter your credentials to access your account
            </p>

            <form className="auth-form" onSubmit={handleSubmit}>
              {error && <div className="auth-error">{error}</div>}

              <div className="auth-field">
                <label htmlFor="login-email">Email address</label>
                <div className="auth-input">
                  <span className="auth-input-icon" aria-hidden="true">✉</span>
                  <input
                    id="login-email"
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
                <label htmlFor="login-password">Password</label>
                <div className="auth-input">
                  <span className="auth-input-icon" aria-hidden="true">🔒</span>
                  <input
                    id="login-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
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

              <button type="submit" className="auth-submit" disabled={loading}>
                {loading ? "Logging in..." : "Login"} <span aria-hidden="true">→</span>
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

export default Login;
