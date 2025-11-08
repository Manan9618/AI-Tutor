import axios from "axios";

// ================= BASE URL =================
const API_BASE_URL = "http://127.0.0.1:8000";

// ================= AXIOS INSTANCE =================
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ================= INTERCEPTORS =================
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("authToken");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ================= AUTH APIs =================

// ✅ FIXED: Matches FastAPI OAuth2PasswordRequestForm
export const login = async (credentials) => {
  const formData = new URLSearchParams();
  formData.append("username", credentials.username);
  formData.append("password", credentials.password);

  return api.post("/api/auth/token", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

// (Optional) Placeholder register/logout — implement if backend supports
export const register = (data) => api.post("/api/auth/register", data);
export const logout = () => {
  localStorage.removeItem("authToken");
  window.location.href = "/login";
};

// ================= CHAT APIs =================

// 🧠 Send a message to AI (supports session-based chats)
export const getChatResponse = (query, sessionId = null) =>
  api.post("/api/chat/message", {
    query,
    session_id: sessionId, // optional; backend creates new session if null
  });

// 📜 Get chat history for a specific session
export const getChatHistory = (sessionId) =>
  api.get(`/api/chat/history?session_id=${sessionId}`);

// 💬 Get all chat sessions for the logged-in user
export const getChatSessions = () => api.get("/api/chat/sessions");

// 🧹 Clear history for a specific session (optional backend endpoint)
export const clearChatHistory = (sessionId) =>
  api.delete(`/api/chat/clear?session_id=${sessionId}`);


// ================= EXPLANATION APIs =================
export const getExplanation = (topic, level = "beginner", style = "visual") =>
  api.post("/api/explanations/", { topic, level, style });

export const getExplanationHistory = () => api.get("/api/explanations/history");
export const clearExplanationHistory = () => api.delete("/api/explanations/clear");

// ================= LEARNING PATH APIs =================

// ✅ Fetch user’s current learning path (roadmap)
export const getLearningPath = () => api.get("/api/learning-path/roadmap");

// ✅ Get next recommended topic (optional enhancement)
export const getRecommendedTopics = () => api.get("/api/learning-path/next-topic");

// ✅ Update user’s progress — if you add this route later
export const updateLearningPath = (pathData) =>
  api.post("/api/learning-path/update", pathData);


// ================= ANALYTICS APIs =================

// ✅ Get dashboard metrics (progress, stats, performance)
export const getAnalytics = () => api.get("/api/analytics/dashboard");

// ✅ Get personalized recommendations (separate endpoint)
export const getRecommendations = () => api.get("/api/analytics/recommendations");

// ✅ For performance metrics, you can either:
// Option 1: Use the dashboard endpoint (recommended)
export const getPerformanceMetrics = () => api.get("/api/analytics/dashboard");

// ✅ NEW: Update analytics progress
export const updateAnalytics = (data) =>
  api.post("/api/analytics/update", data);



// ================= QUIZ APIs =================

// Generate quiz for a given topic
export const getQuiz = (topic) =>
  api.get("/api/quiz/generate", { params: { topic } });

// Submit quiz answers
export const submitQuizAnswer = (topic, answers) =>
  api.post("/api/quiz/submit", { answers }, { params: { topic } });

// ✅ NEW: Get user's quiz history
export const getQuizHistory = () => api.get("/api/quiz/history");

// The backend does not have a separate "results" endpoint,
// so remove this call or compute results from submit response
export const getQuizResults = async () => {
  console.warn("getQuizResults() is not used — results are returned by submitQuizAnswer.");
  return null;
};


// ================= CONTENT APIs =================
export const getContent = (contentId) => api.get(`/api/content/${contentId}`);
export const searchContent = (query) =>
  api.get("/api/content/search", { params: { query } });
export const getContentByTopic = (topic) =>
  api.get("/api/content/topic", { params: { topic } });

// ================= LEARNER APIs =================
export const getLearnerProfile = () => api.get("/api/learner/profile");
export const updateLearnerProfile = (profileData) =>
  api.put("/api/learner/profile", profileData);
export const getLearnerProgress = () => api.get("/api/learner/progress");

export default api;
