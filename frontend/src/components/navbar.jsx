import { Link, useNavigate } from "react-router-dom";
import logo from "./logo.png";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="navbar">

      {/* Logo */}
      <Link to="/" className="logo-section">
        <img className="logo-icon" src={logo} alt="Reading Lizard logo" />
      </Link>

      {/* Links */}
      <div className="nav-links">
        <a href="/#features">Features</a>
        <a href="/#how-it-works">How it works</a>
        <a href="/#about">About</a>
      </div>

      {/* Buttons */}
      <div className="nav-buttons">
        {isAuthenticated ? (
          <>
            <button className="login-btn" onClick={() => navigate("/research")}>
              My research
            </button>
            <span className="navbar-username">
              Hi, {user?.name || user?.email || "there"}
            </span>
            <button className="login-btn" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <button className="login-btn" onClick={() => navigate("/login")}>
              Login
            </button>

            <button className="signup-btn" onClick={() => navigate("/signup")}>
              Sign Up
            </button>
          </>
        )}
      </div>

    </nav>
  );
}

export default Navbar;