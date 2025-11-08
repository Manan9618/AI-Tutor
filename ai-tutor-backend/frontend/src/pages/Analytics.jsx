// src/pages/Analytics.jsx
import React, { useEffect, useState } from "react";
import { getAnalytics, getRecommendations, getPerformanceMetrics } from "../api/api";
import "./Analytics.css";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

import { PieChart, Pie, Cell} from "recharts";

import {
  BarChart,
  Bar
} from "recharts";



const Analytics = () => {
  const [activeTab, setActiveTab] = useState("activity");
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const [dashboardRes, recommendationsRes, performanceRes] = await Promise.all([
        getAnalytics(),
        getRecommendations(),
        getPerformanceMetrics().catch(() => ({ data: null }))
      ]);

      const dashboardData = dashboardRes?.data || {};
      const recommendationsData = recommendationsRes?.data || {};
      const performanceData = performanceRes?.data || {};

      const mergedAnalytics = {
        totalChats: dashboardData.totalChats || dashboardData.total_chats || 0,
        topicsExplored: dashboardData.topicsExplored || dashboardData.topics_explored || 0,
        quizzesCompleted: dashboardData.quizzesCompleted || dashboardData.quizzes_completed || 0,
        averageScore: dashboardData.averageScore || dashboardData.average_score || 0,
        studyTime: dashboardData.studyTime || dashboardData.study_time || 0,
        learningPathProgress: dashboardData.learning_path_progress || 0,
        completedTopics: dashboardData.completed_topics || 0,
        totalTopics: dashboardData.total_topics || 0,
        recommendations: recommendationsData.recommendations || "",
        weeklyActivity: dashboardData.weeklyActivity || [
          { day: "Mon", chats: 3, quizzes: 2, topics: 5 },
          { day: "Tue", chats: 5, quizzes: 4, topics: 6 },
          { day: "Wed", chats: 2, quizzes: 3, topics: 3 },
          { day: "Thu", chats: 7, quizzes: 5, topics: 8 },
          { day: "Fri", chats: 5, quizzes: 4, topics: 7 },
          { day: "Sat", chats: 6, quizzes: 4, topics: 7 },
          { day: "Sun", chats: 4, quizzes: 3, topics: 5 },
        ],
        topicDistribution: dashboardData.topicDistribution || [
          { subject: "Math", percentage: 35 },
          { subject: "Science", percentage: 25 },
          { subject: "English", percentage: 20 },
          { subject: "History", percentage: 20 },
        ],
        quizPerformance: dashboardData.quizPerformance || performanceData.quizPerformance || [
          { subject: "Math", score: 85 },
          { subject: "Science", score: 92 },
          { subject: "History", score: 78 },
          { subject: "English", score: 88 },
          { subject: "Geography", score: 95 },
        ],
        strengths: dashboardData.strengths || performanceData.strengths || ["Problem Solving", "Critical Thinking", "Mathematical Reasoning"],
        areasForImprovement: dashboardData.areasForImprovement || performanceData.areasForImprovement || ["Essay Writing", "Historical Analysis"],
        learningPaths: dashboardData.learningPaths || [
          { name: "Mathematics Mastery", completion: 75, icon: "📐" },
          { name: "Science Explorer", completion: 60, icon: "🔬" },
          { name: "Language Arts", completion: 45, icon: "📚" },
          { name: "History Journey", completion: 30, icon: "🏛️" },
        ],
        badgesEarned: dashboardData.badgesEarned || 15,
        dayStreak: dashboardData.dayStreak || 12,
        totalLearningTime: dashboardData.totalLearningTime || 124,
      };

      setAnalytics(mergedAnalytics);
      setError("");
    } catch (err) {
      console.error("Analytics error:", err);
      setError("Failed to load analytics. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to create smooth curve path
  const createSmoothPath = (points, height, maxValue) => {
    if (!points || points.length === 0) return "";
    
    const width = 600;
    const spacing = width / (points.length - 1);
    
    // Scale points
    const scaledPoints = points.map((value, index) => ({
      x: index * spacing,
      y: height - (value / maxValue) * (height - 40)
    }));
    
    // Create smooth curve using quadratic bezier curves
    let path = `M ${scaledPoints[0].x},${scaledPoints[0].y}`;
    
    for (let i = 0; i < scaledPoints.length - 1; i++) {
      const current = scaledPoints[i];
      const next = scaledPoints[i + 1];
      const controlX = (current.x + next.x) / 2;
      
      path += ` Q ${controlX},${current.y} ${controlX},${(current.y + next.y) / 2}`;
      path += ` Q ${controlX},${next.y} ${next.x},${next.y}`;
    }
    
    // Close the path to create filled area
    path += ` L ${scaledPoints[scaledPoints.length - 1].x},${height}`;
    path += ` L ${scaledPoints[0].x},${height} Z`;
    
    return path;
  };

  if (isLoading) {
    return (
      <div className="analytics-container">
        <div className="page-content">
          {/* Page Header */}
<div className="analytics-header">
  <div className="analytics-header-icon">
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
      <path
        d="M3 3V21H21"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M9 17V11M13 17V7M17 17V14"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  </div>
  <div>
    <h1 className="analytics-title">Analytics Dashboard</h1>
    <p className="analytics-subtitle">Track your learning progress and performance</p>
  </div>
</div>

          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading your analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-container">
        <div className="page-content">
          <div className="page-header">
            <div className="header-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect width="48" height="48" rx="12" fill="#EDE9FE"/>
                <path d="M16 30L20 26L24 30L32 22" stroke="#8B5CF6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div>
              <h1>Analytics Dashboard</h1>
              <p className="subtitle">Track your learning progress and performance</p>
            </div>
          </div>
          <div className="error-message">{error}</div>
        </div>
      </div>
    );
  }

  if (!analytics) return null;

  const maxActivityValue = Math.max(
    ...analytics.weeklyActivity.flatMap(day => [day.chats, day.quizzes, day.topics])
  );

  return (
    <div className="analytics-container">
      <div className="page-content">
        {/* Header */}
        <div className="page-header">
          <div className="header-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="#EDE9FE"/>
              <path d="M16 30L20 26L24 30L32 22" stroke="#8B5CF6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M32 22H28V26" stroke="#8B5CF6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <h1>Analytics Dashboard</h1>
            <p className="subtitle">Track your learning progress and performance</p>
          </div>
        </div>

        {/* Stats Cards */}
        {/* Stats Overview */}
<div className="stats-overview">
  {/* Total Chats */}
  <div className="overview-card">
    <div className="overview-content">
      <div>
        <p className="overview-label">Total Chats</p>
        <h2 className="overview-value">{analytics.totalChats}</h2>
        <p className="overview-trend">↗ +12% from last week</p>
      </div>
      <div className="overview-icon" style={{ backgroundColor: "#dbeafe", color: "#3b82f6" }}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path
            d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          />
        </svg>
      </div>
    </div>
  </div>

  {/* Topics Explored */}
  <div className="overview-card">
    <div className="overview-content">
      <div>
        <p className="overview-label">Topics Explored</p>
        <h2 className="overview-value">{analytics.topicsExplored}</h2>
        <p className="overview-trend">↗ +8% from last week</p>
      </div>
      <div className="overview-icon" style={{ backgroundColor: "#dcfce7", color: "#10b981" }}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path
            d="M4 19.5C4 18.837 4.26339 18.2011 4.73223 17.7322C5.20107 17.2634 5.83696 17 6.5 17H20"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          />
          <path
            d="M6.5 2H20V22H6.5C5.83696 22 5.20107 21.7366 4.73223 21.2678C4.26339 20.7989 4 20.163 4 19.5V4.5C4 3.83696 4.26339 3.20107 4.73223 2.73223C5.20107 2.26339 5.83696 2 6.5 2V2Z"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          />
        </svg>
      </div>
    </div>
  </div>

  {/* Quizzes Completed */}
  <div className="overview-card">
    <div className="overview-content">
      <div>
        <p className="overview-label">Quizzes Completed</p>
        <h2 className="overview-value">{analytics.quizzesCompleted}</h2>
        <p className="overview-trend">↗ +5 this week</p>
      </div>
      <div className="overview-icon" style={{ backgroundColor: "#ede9fe", color: "#8b5cf6" }}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path
            d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.709 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          />
          <path
            d="M22 4L12 14.01L9 11.01"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          />
        </svg>
      </div>
    </div>
  </div>

  {/* Average Score */}
  <div className="overview-card">
    <div className="overview-content">
      <div>
        <p className="overview-label">Average Score</p>
        <h2 className="overview-value">{analytics.averageScore}%</h2>
        <p className="overview-trend">↗ +3% improvement</p>
      </div>
      <div className="overview-icon" style={{ backgroundColor: "#ffedd5", color: "#f97316" }}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
          <circle cx="12" cy="12" r="6" stroke="currentColor" strokeWidth="2" />
          <circle cx="12" cy="12" r="2" fill="currentColor" />
        </svg>
      </div>
    </div>
  </div>
</div>


        {/* Tabs */}
        <div className="tabs-container">
          <div className="tabs-nav">
            <button
              className={`tab ${activeTab === "activity" ? "active" : ""}`}
              onClick={() => setActiveTab("activity")}
            >
              Activity
            </button>
            <button
              className={`tab ${activeTab === "performance" ? "active" : ""}`}
              onClick={() => setActiveTab("performance")}
            >
              Performance
            </button>
            <button
              className={`tab ${activeTab === "progress" ? "active" : ""}`}
              onClick={() => setActiveTab("progress")}
            >
              Progress
            </button>
          </div>

          {/* Activity Tab */}
          {activeTab === "activity" && (
  <div className="tab-content">
    <div className="activity-charts-row">
      {/* Weekly Activity Chart (Left - 65%) */}
      <div className="card weekly-activity-card">
  <div className="card-header">
    <h3>Weekly Activity</h3>
    <p>Your learning activity over the past week</p>
  </div>
  <div className="chart-wrapper">
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={analytics.weeklyActivity} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorChats" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#667eea" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#667eea" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorQuizzes" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#a78bfa" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorTopics" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#34d399" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#34d399" stopOpacity={0}/>
          </linearGradient>
        </defs>

        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="day" tick={{ fill: '#6b7280', fontSize: 12 }} />
        <YAxis
          domain={[0, 'dataMax + 1']}
          tick={{ fill: '#6b7280', fontSize: 12 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            borderRadius: "8px",
            border: "1px solid #e5e7eb",
            boxShadow: "0 4px 8px rgba(0,0,0,0.05)",
          }}
          labelStyle={{ fontWeight: 600, color: "#111827" }}
          formatter={(value, name) => [
            value,
            name.charAt(0).toUpperCase() + name.slice(1),
          ]}
        />
        <Area
          type="monotone"
          dataKey="topics"
          stroke="#34d399"
          fillOpacity={1}
          fill="url(#colorTopics)"
          strokeWidth={2}
        />
        <Area
          type="monotone"
          dataKey="chats"
          stroke="#667eea"
          fillOpacity={1}
          fill="url(#colorChats)"
          strokeWidth={2}
        />
        <Area
          type="monotone"
          dataKey="quizzes"
          stroke="#a78bfa"
          fillOpacity={1}
          fill="url(#colorQuizzes)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
    <div className="chart-legend">
      <div className="legend-item">
        <span className="legend-dot" style={{ backgroundColor: '#667eea' }}></span>
        <span>Chats</span>
      </div>
      <div className="legend-item">
        <span className="legend-dot" style={{ backgroundColor: '#a78bfa' }}></span>
        <span>Quizzes</span>
      </div>
      <div className="legend-item">
        <span className="legend-dot" style={{ backgroundColor: '#34d399' }}></span>
        <span>Topics</span>
      </div>
    </div>
  </div>
</div>

      {/* Topic Distribution Chart (Right - 35%) */}
      <div className="card topic-distribution-card">
  <div className="card-header">
    <h3>Topic Distribution</h3>
    <p>Time spent by subject</p>
  </div>

  <div className="pie-chart-wrapper">
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={analytics.topicDistribution}
          dataKey="percentage"
          nameKey="subject"
          cx="50%"
          cy="50%"
          outerRadius={80}
          labelLine={false}
          label={({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) => {
            const RADIAN = Math.PI / 180;
            const radius = outerRadius * 1.3;
            const x = cx + radius * Math.cos(-midAngle * RADIAN);
            const y = cy + radius * Math.sin(-midAngle * RADIAN);
            const color = ["#3b82f6", "#34d399", "#f59e0b", "#a78bfa"][index];
            const subject = analytics.topicDistribution[index].subject;
            const value = analytics.topicDistribution[index].percentage;
            return (
              <text
                x={x}
                y={y}
                fill={color}
                textAnchor={x > cx ? "start" : "end"}
                dominantBaseline="central"
                fontSize={13}
                fontWeight={600}
              >
                {`${subject} ${value}%`}
              </text>
            );
          }}
        >
          {analytics.topicDistribution.map((entry, index) => {
            const COLORS = ["#3b82f6", "#34d399", "#f59e0b", "#a78bfa"];
            return <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />;
          })}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            boxShadow: "0 4px 8px rgba(0,0,0,0.05)",
          }}
          formatter={(value, name) => [`${value}%`, name]}
        />
      </PieChart>
    </ResponsiveContainer>
  </div>
</div>
    </div>
              {/* Metrics Row */}
              <div className="metrics-row">
                <div className="metric-card">
                  <div className="metric-icon metric-icon-blue">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path d="M10 1L12.5 6.5L18.5 7.5L14.25 11.5L15.25 17.5L10 14.5L4.75 17.5L5.75 11.5L1.5 7.5L7.5 6.5L10 1Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div>
                    <p className="metric-label">Quiz Average</p>
                    <p className="metric-value">{analytics.averageScore}%</p>
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon metric-icon-purple">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2"/>
                      <path d="M10 5V10L13 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                  </div>
                  <div>
                    <p className="metric-label">Avg Response Time</p>
                    <p className="metric-value">2.3s</p>
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon metric-icon-green">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2"/>
                      <circle cx="10" cy="10" r="4" stroke="currentColor" strokeWidth="2"/>
                      <circle cx="10" cy="10" r="1" fill="currentColor"/>
                    </svg>
                  </div>
                  <div>
                    <p className="metric-label">Accuracy Rate</p>
                    <p className="metric-value">92.4%</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Performance Tab */}
          {activeTab === "performance" && (
  <div className="tab-content">
    <div className="card">
      <div className="card-header">
        <h3>Quiz Performance by Subject</h3>
        <p>Your average scores across different subjects</p>
      </div>

      {/* Interactive Bar Chart */}
      <div className="performance-chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={analytics.quizPerformance}
            margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="subject"
              tick={{ fill: "#6b7280", fontSize: 13 }}
              axisLine={false}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: "#6b7280", fontSize: 13 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={{ fill: "#f3f4f6" }}
              contentStyle={{
                backgroundColor: "#fff",
                borderRadius: "8px",
                border: "1px solid #e5e7eb",
                boxShadow: "0 4px 8px rgba(0,0,0,0.05)",
              }}
              labelStyle={{ fontWeight: 600, color: "#111827" }}
              formatter={(value) => [`score : ${value}`, ""]}
            />
            <Bar
              dataKey="score"
              radius={[8, 8, 0, 0]}
              fill="#a78bfa"
              barSize={50}
              animationDuration={800}
            >
              {analytics.quizPerformance.map((entry, index) => (
                <Cell key={`cell-${index}`} fill="#a78bfa" />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>

    {/* Keep your Strengths & Areas for Improvement cards below */}
    <div className="strength-grid">
      {/* existing strengths and areas cards */}
    </div>

    {analytics.recommendations && (
      <div className="card">
        <div className="card-header">
          <h3>Personalized Recommendations</h3>
          <p>AI-generated insights for your learning journey</p>
        </div>
        <div className="recommendations">
          {analytics.recommendations}
        </div>
      </div>
    )}
  </div>
)}

          {/* Progress Tab */}
          {activeTab === "progress" && (
            <div className="tab-content">
              {/* Learning Path Progress Section */}
<div className="card">
  <div className="card-header">
    <h3>Learning Path Progress</h3>
    <p>Track your progress across different learning paths</p>
  </div>

  <div className="learning-progress-container">
    {analytics.learningPaths.map((path, idx) => {
      const colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"];
      const icons = ["📘", "🧪", "🏛️", "📖"]; // Example icons
      return (
        <div key={idx} className="progress-item">
          <div className="progress-info">
            <div
              className="progress-icon"
              style={{
                backgroundColor: `${colors[idx]}15`,
                color: colors[idx],
              }}
            >
              {icons[idx]}
            </div>
            <div className="progress-text">
              <p className="progress-title">{path.name}</p>
              <p className="progress-subtitle">{path.completion}% Complete</p>
            </div>
          </div>

          <div className="progress-bar-wrapper">
            <div
              className="progress-bar-bg"
              style={{ backgroundColor: "#e5e7eb" }}
            >
              <div
                className="progress-bar-fill"
                style={{
                  width: `${path.completion}%`,
                  backgroundColor: "#111827",
                }}
              ></div>
            </div>
            <span className="progress-value">{path.completion}%</span>
          </div>
        </div>
      );
    })}
  </div>
</div>


              {/* Progress Summary Cards */}
<div className="progress-summary">
  <div className="summary-card">
    <div className="summary-icon" style={{ backgroundColor: "#dbeafe", color: "#3b82f6" }}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M12 2L15 8.5L22 9.5L17 14.5L18 21.5L12 18L6 21.5L7 14.5L2 9.5L9 8.5L12 2Z"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
    <h3 className="summary-value">{analytics.badgesEarned}</h3>
    <p className="summary-label">Badges Earned</p>
  </div>

  <div className="summary-card">
    <div className="summary-icon" style={{ backgroundColor: "#dcfce7", color: "#10b981" }}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
    <h3 className="summary-value">{analytics.dayStreak}</h3>
    <p className="summary-label">Day Streak</p>
  </div>

  <div className="summary-card">
    <div className="summary-icon" style={{ backgroundColor: "#ede9fe", color: "#8b5cf6" }}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
        <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    </div>
    <h3 className="summary-value">{analytics.totalLearningTime}h</h3>
    <p className="summary-label">Total Learning Time</p>
  </div>
</div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;