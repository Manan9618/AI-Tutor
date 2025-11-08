// src/pages/LearningPath.jsx
import React, { useState, useEffect } from "react";
import { getLearningPath, updateLearningPath } from "../api/api";
import { useNavigate } from "react-router-dom";
import "./LearningPath.css";

const LearningPath = () => {
  const [topics, setTopics] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const pathRes = await getLearningPath();
      const topicsData = pathRes.data?.topics || pathRes.data || [];
      setTopics(topicsData);
    } catch (err) {
      console.error("Learning path error:", err);
      if (err.response?.status === 401) {
        setError("Authentication required. Please log in again.");
      } else if (err.response?.status === 404) {
        setError("Learning path endpoint not found. Please check your backend.");
      } else {
        setError(err.response?.data?.detail || "Failed to load learning path");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleTopicClick = (topic) => {
    navigate("/explanation", { state: { topic: topic.name } });
  };

  const markAsCompleted = async (topicId) => {
    try {
      const updatedTopics = topics.map(t =>
        t.id === topicId ? { ...t, completed: true } : t
      );
      setTopics(updatedTopics);
      await updateLearningPath({ topics: updatedTopics });

      try {
        await fetch("/api/analytics/update", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("authToken")}`
          },
          body: JSON.stringify({
            type: "topic_completed",
            topic_id: topicId
          })
        });
      } catch (err) {
        console.warn("Failed to log completion to analytics:", err);
      }
    } catch (err) {
      console.error("Failed to update progress:", err);
      setError("Failed to update progress. Please try again.");
    }
  };

  if (isLoading) {
    return (
      <div className="learning-path-container">
        <div className="page-content">
          <div className="page-header">
            <div className="header-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="48" height="48" rx="12" fill="#FFE5CC"/>
                <path d="M24 14L16 19V24H32V19L24 14Z" fill="#FF6B00"/>
                <path d="M16 24L24 29L32 24" stroke="#FF6B00" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div>
              <h1>Learning Path</h1>
              <p className="subtitle">Track your progress and plan your learning journey</p>
            </div>
          </div>

          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading your learning path...</p>
          </div>
        </div>
      </div>
    );
  }

  const completedCount = topics.filter(t => t.completed).length;
  const totalTopics = topics.length;
  const progressPercentage = totalTopics > 0 ? Math.round((completedCount / totalTopics) * 100) : 0;

  return (
    <div className="learning-path-container">
      <div className="page-content">
        <div className="page-header">
          <div className="header-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="48" height="48" rx="12" fill="#FFE5CC"/>
              <path d="M24 14L16 19V24H32V19L24 14Z" fill="#FF6B00"/>
              <path d="M16 24L24 29L32 24" stroke="#FF6B00" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <h1>Learning Path</h1>
            <p className="subtitle">Track your progress and plan your learning journey</p>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="path-section">
          <h2 className="section-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 19.5C4 18.837 4.26339 18.2011 4.73223 17.7322C5.20107 17.2634 5.83696 17 6.5 17H20" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M6.5 2H20V22H6.5C5.83696 22 5.20107 21.7366 4.73223 21.2678C4.26339 20.7989 4 20.163 4 19.5V4.5C4 3.83696 4.26339 3.20107 4.73223 2.73223C5.20107 2.26339 5.83696 2 6.5 2Z" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Your Current Path
          </h2>
          
          {topics.length === 0 ? (
            <div className="empty-state">
              <p>No topics in your learning path yet.</p>
            </div>
          ) : (
            <div className="topics-list">
              {topics.map((topic, idx) => (
                <div 
                  key={topic.id || idx} 
                  className={`topic-item ${topic.completed ? 'completed' : ''}`}
                  onClick={() => handleTopicClick(topic)}
                >
                  <div className="topic-left">
                    <div className="topic-number-circle">
                      {idx + 1}
                    </div>
                    <div className="topic-content">
                      <h3 className="topic-title">
                        {idx + 1}. {topic.name || topic}
                      </h3>
                      {topic.description && (
                        <p className="topic-description">{topic.description}</p>
                      )}
                    </div>
                  </div>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      markAsCompleted(topic.id || idx);
                    }}
                    className={`complete-btn ${topic.completed ? 'completed' : ''}`}
                    disabled={topic.completed}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                      {topic.completed && (
                        <path d="M8 12L11 15L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      )}
                    </svg>
                    Mark Complete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {topics.length > 0 && (
          <div className="progress-section">
            <h2 className="section-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.7088 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M22 4L12 14.01L9 11.01" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Progress Summary
            </h2>
            
            <div className="progress-stats">
              <div className="stat-card">
                <div className="stat-value">{completedCount}</div>
                <div className="stat-label">Completed</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{totalTopics}</div>
                <div className="stat-label">Total Topics</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{progressPercentage}%</div>
                <div className="stat-label">Progress</div>
              </div>
            </div>

            <div className="overall-progress">
              <h3>Overall Progress</h3>
              <div className="progress-bar-container">
                <div 
                  className="progress-bar-fill" 
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
              <div className="progress-text">
                <span>{completedCount} of {totalTopics} topics completed</span>
                <span>{progressPercentage}%</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LearningPath;