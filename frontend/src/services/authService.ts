import axios from "axios";

// Base URL for your API
const API_URL = import.meta.env.REACT_APP_API_URL || "http://localhost:8000";

// Create an axios instance
const api = axios.create({
  baseURL: API_URL,
});

// --- Auth Token Handling ---

const getToken = (): string | null => sessionStorage.getItem("access_token");

const isAuthenticated = (): boolean => {
  const token = getToken();
  const expiryStr = sessionStorage.getItem("token_expiry");
  if (!token || !expiryStr) return false;

  const expiry = parseInt(expiryStr);
  if (Date.now() > expiry) {
    console.log("🔴 Token expired");
    sessionStorage.clear();
    return false;
  }
  console.log("🟢 Valid Token:", token);
  return true;
};

const redirectToLogin = async (): Promise<void> => {
  console.log("🟡 redirectToLogin() triggered");
  try {
    const res = await api.get("/api/get-login-url");
    if (res.data?.authUrl) {
      window.location.href = res.data.authUrl; // redirect user
    } else {
      console.error("❌ authUrl missing from backend response");
    }
  } catch (err) {
    console.error("Login redirect failed", err);
  }
};

const handleAuthCallback = (): boolean => {
  const hash = window.location.hash.substring(1);
  const params = new URLSearchParams(hash);

  const token = params.get("access_token");
  const expiresIn = params.get("expires_in");

  if (token && expiresIn) {
    const expiryTime = Date.now() + parseInt(expiresIn) * 1000;
    sessionStorage.setItem("access_token", token);
    sessionStorage.setItem("token_expiry", expiryTime.toString());

    // Clean URL
    window.history.replaceState({}, document.title, window.location.pathname);
    return true;
  }
  return false;
};

// --- Axios interceptors ---

// Attach token to requests
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      console.log("🔴 401 Unauthorized - token invalid or expired");
      sessionStorage.clear();
      await redirectToLogin();
    }
    return Promise.reject(error);
  }
);

// --- Exported service object ---

const authService = {
  api,
  getToken,
  isAuthenticated,
  redirectToLogin,
  handleAuthCallback,
};

export default authService;
