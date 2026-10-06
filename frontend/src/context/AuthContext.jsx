import { createContext, useContext, useEffect, useState } from "react";
import { loginRequest, registerRequest } from "../api/authApi";

const AuthContext = createContext(null);

const TOKEN_KEY = "rl_token";
const USER_KEY = "rl_user";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  });

  useEffect(() => {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  }, [token]);

  useEffect(() => {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
    else localStorage.removeItem(USER_KEY);
  }, [user]);

  const applyAuthResponse = (data) => {
    // Backend response shape can vary a bit, so we check a few common keys.
    const nextToken = data?.token || data?.accessToken || data?.jwt || null;
    const nextUser = data?.user || data?.profile || null;
    if (nextToken) setToken(nextToken);
    if (nextUser) setUser(nextUser);
    return { token: nextToken, user: nextUser };
  };

  const login = async ({ email, password }) => {
    const data = await loginRequest({ email, password });
    return applyAuthResponse(data);
  };

  const register = async ({ name, email, password }) => {
    await registerRequest({ name, email, password });
    const session = await loginRequest({ email, password });
    return applyAuthResponse(session);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  const value = {
    token,
    user,
    isAuthenticated: Boolean(token),
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside an AuthProvider");
  return ctx;
}
