// // src/pages/Home.jsx
// import React, { useState, useEffect } from "react";
// import { Link } from "react-router-dom";
// import { getAnalytics, getRecommendedTopics } from "../api/api";
// import "./Home.css";

// const Home = () => {
//   const [stats, setStats] = useState({
//     topicsLearned: 0,
//     quizzesCompleted: 0,
//     averageScore: 0,
//   });

//   const [continueLearning, setContinueLearning] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");

//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         // Fetch analytics dashboard
//         const analyticsRes = await getAnalytics();
//         const metrics = analyticsRes.data;

//         // Map backend fields to UI
//         setStats({
//           topicsLearned: metrics.completed_topics || 0,
//           quizzesCompleted: metrics.quizzes_completed || 0,
//           averageScore: metrics.average_score || 0,
//         });

//         // Fetch next topic
//         const nextTopicRes = await getRecommendedTopics();
//         const nextTopic = nextTopicRes.data?.next_topic;

//         if (nextTopic) {
//           setContinueLearning({
//             topic: nextTopic,
//             lastStudied: "Just now",
//             route: `/explanation?topic=${encodeURIComponent(nextTopic)}`,
//           });
//         }

//         setLoading(false);
//       } catch (err) {
//         console.error("Failed to load dashboard ", err);
//         setError("Failed to load dashboard. Please refresh.");
//         setLoading(false);
//       }
//     };

//     fetchData();
//   }, []);

//   if (loading) {
//     return (
//       <div className="home-page">
//         <div className="loading">Loading dashboard...</div>
//       </div>
//     );
//   }

//   if (error) {
//     return (
//       <div className="home-page">
//         <div className="error-message">{error}</div>
//       </div>
//     );
//   }

//   return (
//     <div className="home-page">
//   <div className="welcome-banner">
//   <span className="welcome-icon">🤖🎓</span>
//   <span className="welcome-text">Welcome to <strong>AI Tutor</strong></span>
// </div>


//       {/* Main Title */}
//       <h1 className="page-title">AI Tutor Dashboard</h1>
//       <p className="page-subtitle">Choose a module to get started</p>

//       {/* Module Cards */}
//       <div className="module-cards-grid">
//         <Link to="/chat" className="module-card chat-card">
//           <div className="card-icon-wrapper">
//             <span className="card-icon">💬</span>
//           </div>
//           <h3>Chat</h3>
//           <p>Ask interactive questions</p>
//           <div className="get-started">Get started →</div>
//         </Link>

//         <Link to="/explanation" className="module-card explanation-card">
//           <div className="card-icon-wrapper">
//             <span className="card-icon">📘</span>
//           </div>
//           <h3>Explanation</h3>
//           <p>Get topic explanations</p>
//           <div className="get-started">Get started →</div>
//         </Link>

//         <Link to="/learning-path" className="module-card learning-path-card">
//           <div className="card-icon-wrapper">
//             <span className="card-icon">🧭</span>
//           </div>
//           <h3>Learning Path</h3>
//           <p>Your customized learning</p>
//           <div className="get-started">Get started →</div>
//         </Link>

//         <Link to="/analytics" className="module-card analytics-card">
//           <div className="card-icon-wrapper">
//             <span className="card-icon">📊</span>
//           </div>
//           <h3>Analytics</h3>
//           <p>Track your performance</p>
//           <div className="get-started">Get started →</div>
//         </Link>
//       </div>

//       {/* Stats Cards */}
//       <div className="stats-cards-grid">
//         <div className="stat-card">
//           <h2>{stats.topicsLearned}</h2>
//           <p>Topics Learned</p>
//         </div>
//         <div className="stat-card">
//           <h2>{stats.quizzesCompleted}</h2>
//           <p>Quizzes Completed</p>
//         </div>
//         <div className="stat-card">
//           <h2>{Math.round(stats.averageScore)}%</h2>
//           <p>Average Score</p>
//         </div>
//       </div>

//       {/* Continue Learning Section */}
//       {continueLearning && (
//         <div className="continue-learning-section">
//           <h2>Continue Learning</h2>
//           <div className="continue-card">
//             <div className="continue-icon">📘</div>
//             <div className="continue-content">
//               <h3>{continueLearning.topic}</h3>
//               <p>Last studied {continueLearning.lastStudied}</p>
//             </div>
//             <Link to={continueLearning.route} className="continue-btn">
//               Continue →
//             </Link>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default Home;

// src/pages/Home.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getAnalytics, getRecommendedTopics } from "../api/api";
import "./Home.css";

const Home = () => {
  const [stats, setStats] = useState({
    topicsLearned: 0,
    quizzesCompleted: 0,
    averageScore: 0,
  });

  const [continueLearning, setContinueLearning] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch analytics dashboard
        const analyticsRes = await getAnalytics();
        const metrics = analyticsRes.data;

        // Map backend fields to UI
        setStats({
          topicsLearned: metrics.completed_topics || 0,
          quizzesCompleted: metrics.quizzes_completed || 0,
          averageScore: metrics.average_score || 0,
        });

        // Fetch next topic
        const nextTopicRes = await getRecommendedTopics();
        const nextTopic = nextTopicRes.data?.next_topic;

        if (nextTopic) {
          setContinueLearning({
            topic: nextTopic,
            lastStudied: "Just now",
            route: `/explanation?topic=${encodeURIComponent(nextTopic)}`,
          });
        }

        setLoading(false);
      } catch (err) {
        console.error("Failed to load dashboard ", err);
        setError("Failed to load dashboard. Please refresh.");
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="home-page">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="home-page">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="home-page">
      <div className="welcome-banner">
        <span className="welcome-icon">🤖🎓</span>
        <span className="welcome-text">Welcome to <strong>AI Tutor</strong></span>
      </div>

      {/* Main Title */}
      <h1 className="page-title">AI Tutor Dashboard</h1>
      <p className="page-subtitle">Choose a module to get started</p>

      {/* Module Cards */}
      <div className="module-cards-grid">
        <Link to="/chat" className="module-card chat-card">
          <div className="card-icon-wrapper">
            <span className="card-icon">💬</span>
          </div>
          <h3>Chat</h3>
          <p>Ask interactive questions</p>
          <div className="get-started">Get started →</div>
        </Link>

        <Link to="/explanation" className="module-card explanation-card">
          <div className="card-icon-wrapper">
            <span className="card-icon">📘</span>
          </div>
          <h3>Explanation</h3>
          <p>Get topic explanations</p>
          <div className="get-started">Get started →</div>
        </Link>

        <Link to="/learning-path" className="module-card learning-path-card">
          <div className="card-icon-wrapper">
            <span className="card-icon">🧭</span>
          </div>
          <h3>Learning Path</h3>
          <p>Your customized learning</p>
          <div className="get-started">Get started →</div>
        </Link>

        <Link to="/analytics" className="module-card analytics-card">
          <div className="card-icon-wrapper">
            <span className="card-icon">📊</span>
          </div>
          <h3>Analytics</h3>
          <p>Track your performance</p>
          <div className="get-started">Get started →</div>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="stats-cards-grid">
        <div className="stat-card">
          <h2>{stats.topicsLearned}</h2>
          <p>Topics Learned</p>
        </div>
        <div className="stat-card">
          <h2>{stats.quizzesCompleted}</h2>
          <p>Quizzes Completed</p>
        </div>
        <div className="stat-card">
          <h2>{Math.round(stats.averageScore)}%</h2>
          <p>Average Score</p>
        </div>
      </div>

      {/* Continue Learning Section */}
      {continueLearning && (
        <div className="continue-learning-section">
          <h2>Continue Learning</h2>
          <div className="continue-card">
            <div className="continue-icon">📘</div>
            <div className="continue-content">
              <h3>{continueLearning.topic}</h3>
              <p>Last studied {continueLearning.lastStudied}</p>
            </div>
            <Link to={continueLearning.route} className="continue-btn">
              Continue →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;