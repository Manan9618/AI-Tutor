import React, { useEffect, useState } from "react";
import { getAnalytics, getProgressStats, getPerformanceMetrics } from "../api/api";

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [progressStats, setProgressStats] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics();
    // ✅ Auto-refresh every 10s to reflect updates after quiz/explanation/chat
    const interval = setInterval(fetchAnalytics, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      // Get all analytics data from backend (memory_agent + orchestrator)
      const [analyticsRes, progressRes, performanceRes] = await Promise.all([
        getAnalytics(),
        getProgressStats().catch(() => ({ data: null })),
        getPerformanceMetrics().catch(() => ({ data: null })),
      ]);

      const analyticsData = analyticsRes?.data || {};
      const progressData = progressRes?.data || {};
      const performanceData = performanceRes?.data || {};

      // ✅ Combine memory_agent fields and fallback computed metrics
      const mergedAnalytics = {
        totalChats:
          analyticsData.totalChats ||
          analyticsData.total_chats ||
          analyticsData.chats ||
          0,
        topicsExplored:
          analyticsData.topicsExplored ||
          analyticsData.topics_explored ||
          Object.keys(analyticsData.topics || {}).length ||
          0,
        quizzesCompleted:
          analyticsData.quizzesCompleted ||
          analyticsData.quizzes_completed ||
          Object.keys(analyticsData.performance || {}).length ||
          0,
        averageScore:
          analyticsData.averageScore ||
          analyticsData.average_score ||
          getAverageScore(analyticsData.performance) ||
          0,
        studyTime:
          analyticsData.studyTime ||
          analyticsData.study_time ||
          getTotalStudyTime(analyticsData.performance) ||
          0,
        learningPathProgress:
          analyticsData.learning_path_progress ||
          progressData.pathProgress ||
          0,
        completedTopics:
          analyticsData.completed_topics ||
          progressData.completedTopics ||
          0,
        totalTopics:
          analyticsData.total_topics ||
          progressData.totalTopics ||
          0,
        knowledgeGaps: analyticsData.knowledge_gaps || [],
        recentActivity: analyticsData.recentActivity || [],
      };

      const mergedProgress = {
        pathProgress:
          progressData.pathProgress ||
          analyticsData.learning_path_progress ||
          0,
        weeklyActivity:
          progressData.weeklyActivity ||
          analyticsData.weekly_activity ||
          0,
        currentStreak:
          progressData.currentStreak ||
          analyticsData.streak_days ||
          0,
      };

      const mergedPerformance = {
        quizAverage:
          performanceData.quizAverage ||
          ((analyticsData.average_score || 0) * 100).toFixed(1),
        avgResponseTime:
          performanceData.avgResponseTime ||
          getAvgResponseTime(analyticsData.performance),
        accuracyRate:
          performanceData.accuracyRate ||
          ((analyticsData.average_score || 0) * 100).toFixed(1),
      };

      setAnalytics(mergedAnalytics);
      setProgressStats(mergedProgress);
      setPerformanceMetrics(mergedPerformance);
    } catch (err) {
      console.error("Analytics error:", err);
      setError("Failed to load analytics");
    } finally {
      setIsLoading(false);
    }
  };

  // 🔹 Helpers to compute fallback values
  const getTotalStudyTime = (performance = {}) => {
    const times = Object.values(performance).map((p) => p.time || 0);
    const totalHours = times.reduce((a, b) => a + b, 0) / 3600;
    return totalHours.toFixed(1);
  };

  const getAverageScore = (performance = {}) => {
    const scores = Object.values(performance).map((p) => p.score || 0);
    if (scores.length === 0) return 0;
    return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);
  };

  const getAvgResponseTime = (performance = {}) => {
    const times = Object.values(performance).map((p) => p.time || 0);
    if (times.length === 0) return 0;
    return (times.reduce((a, b) => a + b, 0) / times.length).toFixed(1);
  };

  if (isLoading) {
    return (
      <div className="page">
        <h1>📊 Analytics</h1>
        <p className="loading">Loading your analytics...</p>
      </div>
    );
  }

  return (
    <div className="page analytics-page">
      <h1>📊 Analytics Dashboard</h1>
      <p className="subtitle">Track your learning progress and performance</p>

      {error && <div className="error-message">{error}</div>}

      {/* Overall Statistics */}
      {analytics && (
        <div className="analytics-section">
          <h2>📈 Overall Statistics</h2>
          <div className="stats-grid">
            <StatCard icon="💬" label="Total Chats" value={analytics.totalChats} />
            <StatCard icon="📘" label="Topics Explored" value={analytics.topicsExplored} />
            <StatCard icon="✅" label="Quizzes Completed" value={analytics.quizzesCompleted} />
            <StatCard icon="🎯" label="Average Score" value={`${analytics.averageScore}%`} />
          </div>
        </div>
      )}

      {/* Progress Overview */}
      {analytics && (
        <div className="analytics-section">
          <h2>📊 Learning Path Progress</h2>
          <div className="progress-card">
            <div className="progress-bar-container">
              <div
                className="progress-bar"
                style={{ width: `${analytics.learningPathProgress || 0}%` }}
              />
            </div>
            <p className="progress-text">
              {analytics.learningPathProgress || 0}% Complete (
              {analytics.completedTopics}/{analytics.totalTopics} topics)
            </p>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {performanceMetrics && (
        <div className="analytics-section">
          <h2>🎯 Performance Metrics</h2>
          <div className="metrics-grid">
            <MetricCard title="Quiz Average" value={`${performanceMetrics.quizAverage}%`} />
            <MetricCard title="Response Time" value={`${performanceMetrics.avgResponseTime}s`} />
            <MetricCard title="Accuracy Rate" value={`${performanceMetrics.accuracyRate}%`} />
          </div>
        </div>
      )}

      {/* Knowledge Gaps */}
      {analytics?.knowledgeGaps?.length > 0 && (
        <div className="analytics-section">
          <h2>⚠️ Knowledge Gaps</h2>
          <ul>
            {analytics.knowledgeGaps.map((gap, idx) => (
              <li key={idx}>{gap}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Recent Activity */}
      {analytics?.recentActivity?.length > 0 && (
        <div className="analytics-section">
          <h2>🕐 Recent Activity</h2>
          <div className="activity-list">
            {analytics.recentActivity.map((activity, idx) => (
              <div key={idx} className="activity-item">
                <span className="activity-icon">
                  {activity.type === "chat"
                    ? "💬"
                    : activity.type === "quiz"
                    ? "✅"
                    : "📘"}
                </span>
                <div className="activity-details">
                  <p className="activity-title">{activity.title}</p>
                  <p className="activity-time">{activity.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Debug Raw Data (Dev Only) */}
      {process.env.NODE_ENV === "development" && analytics && (
        <details className="debug-section">
          <summary>🔍 Raw Analytics Data</summary>
          <pre>{JSON.stringify(analytics, null, 2)}</pre>
        </details>
      )}
    </div>
  );
};

// ✅ Helper Components
const StatCard = ({ icon, label, value }) => (
  <div className="stat-card">
    <div className="stat-icon">{icon}</div>
    <div className="stat-info">
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  </div>
);

const MetricCard = ({ title, value }) => (
  <div className="metric-card">
    <h4>{title}</h4>
    <p className="metric-value">{value}</p>
  </div>
);

export default Analytics;
