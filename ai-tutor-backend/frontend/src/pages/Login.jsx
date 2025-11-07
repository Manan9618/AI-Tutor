import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/api";
import "./Login.css";

const Login = ({ onLogin }) => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      // Send login request
      const res = await login({ username, password });
      const token = res.data?.access_token;

      if (token) {
        // ✅ Store token and notify parent (App.jsx)
        localStorage.setItem("authToken", token);
        if (onLogin) onLogin(token);

        // ✅ Redirect to home page
        navigate("/", { replace: true });
      } else {
        setError("Invalid server response. Please try again.");
      }
    } catch (err) {
      console.error("Login error:", err);
      // ❌ Show error returned by backend or generic message
      setError(
        err.response?.data?.detail || "Invalid username or password. Please try again."
      );
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h2 className="login-title">Login</h2>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="options">
            <label>
              <input type="checkbox" /> Remember me
            </label>
            <button
              type="button"
              onClick={() => navigate("/forgot-password")}
              className="forgot-link"
            >
              Forgot password?
            </button>
          </div>

          <button type="submit" className="btn-login">
            Login Now
          </button>
        </form>

        <p className="switch-link">
          Don't have an account?{" "}
          <span onClick={() => navigate("/register")}>Register here</span>
        </p>
      </div>
    </div>
  );
};

export default Login;
