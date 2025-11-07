// // src/pages/LearningPath.jsx
// import React, { useState, useEffect } from "react";
// import { getLearningPath, updateLearningPath } from "../api/api";
// import { useNavigate } from "react-router-dom";
// import "./LearningPath.css"

// const LearningPath = () => {
//   const [topics, setTopics] = useState([]);
//   const [isLoading, setIsLoading] = useState(true);
//   const [error, setError] = useState("");
//   const navigate = useNavigate();

//   useEffect(() => {
//     fetchData();
//   }, []);

//   const fetchData = async () => {
//     setIsLoading(true);
//     try {
//       const pathRes = await getLearningPath();
      
//       // Handle different response formats
//       const topicsData = pathRes.data?.topics || pathRes.data || [];
//       setTopics(topicsData);
//     } catch (err) {
//       console.error("Learning path error:", err);
      
//       // More specific error handling
//       if (err.response?.status === 401) {
//         setError("Authentication required. Please log in again.");
//       } else if (err.response?.status === 404) {
//         setError("Learning path endpoint not found. Please check your backend.");
//       } else {
//         setError(err.response?.data?.detail || "Failed to load learning path");
//       }
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   // === Handle click on topic ===
//   const handleTopicClick = (topic) => {
//     const action = window.prompt(
//       `What would you like to do for "${topic.name}"?\n\nType:\n- "explanation" to view explanation\n- "quiz" to take quiz`
//     );

//     if (!action) return;

//     const choice = action.toLowerCase();
//     if (choice === "explanation") {
//       navigate("/explanation", { state: { topic: topic.name } });
//     } else if (choice === "quiz") {
//       navigate("/quiz", { state: { topic: topic.name } });
//     } else {
//       alert("Invalid choice. Please type 'explanation' or 'quiz'.");
//     }
//   };

//   // === Mark topic complete & update analytics ===
//   const markAsCompleted = async (topicId) => {
//     try {
//       const updatedTopics = topics.map(t => 
//         t.id === topicId ? { ...t, completed: true } : t
//       );
//       setTopics(updatedTopics);
      
//       await updateLearningPath({ topics: updatedTopics });

//       // Record completion to analytics
//       try {
//         await fetch("/api/analytics/update", {
//           method: "POST",
//           headers: { 
//             "Content-Type": "application/json",
//             "Authorization": `Bearer ${localStorage.getItem("authToken")}`
//           },
//           body: JSON.stringify({
//             type: "topic_completed",
//             topic_id: topicId
//           })
//         });
//       } catch (err) {
//         console.warn("Failed to log completion to analytics:", err);
//       }

//     } catch (err) {
//       console.error("Failed to update progress:", err);
//       setError("Failed to update progress. Please try again.");
//     }
//   };

//   if (isLoading) {
//     return (
//       <div className="learning-path-container">

//         {/* Page Content */}
//         <div className="page-content">
//           {/* Page Header */}
//           <div className="page-header">
//             <div className="header-icon">
//               <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
//                 <rect width="40" height="40" rx="10" fill="#FFEBCD"/>
//                 <path d="M20 10L12 15V20H28V15L20 10Z" fill="#FF6B00"/>
//                 <path d="M12 20L20 25L28 20" stroke="#FF6B00" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
//               </svg>
//             </div>
//             <div>
//               <h1>Learning Path</h1>
//               <p className="subtitle">Track your progress and plan your learning journey</p>
//             </div>
//           </div>

//           {/* Loading State */}
//           <div className="loading-state">
//             <div className="spinner"></div>
//             <p>Loading your learning path...</p>
//           </div>
//         </div>
//       </div>
//     );
//   }

//   const completedCount = topics.filter(t => t.completed).length;
//   const totalTopics = topics.length;
//   const progressPercentage = totalTopics > 0 ? Math.round((completedCount / totalTopics) * 100) : 0;

//   return (
//     <div className="learning-path-container">

//       {/* Page Content */}
//       <div className="page-content">
//         {/* Page Header */}
//         <div className="page-header">
//           <div className="header-icon">
//             <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
//               <rect width="40" height="40" rx="10" fill="#FFEBCD"/>
//               <path d="M20 10L12 15V20H28V15L20 10Z" fill="#FF6B00"/>
//               <path d="M12 20L20 25L28 20" stroke="#FF6B00" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
//             </svg>
//           </div>
//           <div>
//             <h1>Learning Path</h1>
//             <p className="subtitle">Track your progress and plan your learning journey</p>
//           </div>
//         </div>

//         {error && <div className="error-message">{error}</div>}

//         {/* Current Learning Path */}
//         <div className="path-section">
//           <h2 className="section-title">📚 Your Current Path</h2>
          
//           {topics.length === 0 ? (
//             <div className="empty-state">
//               <p>No topics in your learning path yet.</p>
//             </div>
//           ) : (
//             <div className="topics-list">
//               {topics.map((topic, idx) => (
//                 <div 
//                   key={topic.id || idx} 
//                   className={`topic-card ${topic.completed ? 'completed' : ''}`}
//                   onClick={() => handleTopicClick(topic)}
//                 >
//                   <div className="topic-number-circle">
//                     {idx + 1}
//                   </div>
//                   <div className="topic-content">
//                     <h3>{topic.name || topic}</h3>
//                     {topic.description && (
//                       <p className="topic-description">{topic.description}</p>
//                     )}
//                   </div>
//                   <button 
//                     onClick={(e) => {
//                       e.stopPropagation(); // prevent triggering handleTopicClick
//                       markAsCompleted(topic.id || idx);
//                     }}
//                     className={`complete-btn ${topic.completed ? 'completed' : ''}`}
//                   >
//                     {topic.completed ? (
//                       <>
//                         <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
//                           <path d="M9 12L11 14L15 10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
//                         </svg>
//                         Completed
//                       </>
//                     ) : (
//                       <>
//                         <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
//                           <path d="M9 12L11 14L15 10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
//                         </svg>
//                         Mark Complete
//                       </>
//                     )}
//                   </button>
//                 </div>
//               ))}
//             </div>
//           )}
//         </div>

//         {/* Progress Summary */}
//         {topics.length > 0 && (
//           <div className="progress-section">
//             <h2 className="section-title">Progress Summary</h2>
            
//             <div className="progress-stats">
//               <div className="stat-card">
//                 <div className="stat-value">{completedCount}</div>
//                 <div className="stat-label">Completed</div>
//               </div>
//               <div className="stat-card">
//                 <div className="stat-value">{totalTopics}</div>
//                 <div className="stat-label">Total Topics</div>
//               </div>
//               <div className="stat-card">
//                 <div className="stat-value">{progressPercentage}%</div>
//                 <div className="stat-label">Progress</div>
//               </div>
//             </div>

//             {/* Overall Progress Bar */}
//             <div className="overall-progress">
//               <h3>Overall Progress</h3>
//               <div className="progress-bar-container">
//                 <div 
//                   className="progress-bar-fill" 
//                   style={{ width: `${progressPercentage}%` }}
//                 ></div>
//               </div>
//               <div className="progress-text">
//                 <span>{completedCount} of {totalTopics} topics completed</span>
//                 <span>{progressPercentage}%</span>
//               </div>
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default LearningPath;

// src/pages/LearningPath.jsx
import React, { useState, useEffect } from "react";
import { getLearningPath, updateLearningPath } from "../api/api";
import { useNavigate } from "react-router-dom";
import "./LearningPath.css"

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
      
      // Handle different response formats
      const topicsData = pathRes.data?.topics || pathRes.data || [];
      setTopics(topicsData);
    } catch (err) {
      console.error("Learning path error:", err);
      
      // More specific error handling
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

  // === Handle click on topic ===
  const handleTopicClick = (topic) => {
    const action = window.prompt(
      `What would you like to do for "${topic.name}"?\n\nType:\n- "explanation" to view explanation\n- "quiz" to take quiz`
    );

    if (!action) return;

    const choice = action.toLowerCase();
    if (choice === "explanation") {
      navigate("/explanation", { state: { topic: topic.name } });
    } else if (choice === "quiz") {
      navigate("/quiz", { state: { topic: topic.name } });
    } else {
      alert("Invalid choice. Please type 'explanation' or 'quiz'.");
    }
  };

  // === Mark topic complete & update analytics ===
  const markAsCompleted = async (topicId) => {
    try {
      const updatedTopics = topics.map(t => 
        t.id === topicId ? { ...t, completed: true } : t
      );
      setTopics(updatedTopics);
      
      await updateLearningPath({ topics: updatedTopics });

      // Record completion to analytics
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
          {/* Page Header */}
          <div className="page-header">
            <div className="header-icon">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="40" height="40" rx="10" fill="#FFEBCD"/>
                <path d="M20 10L12 15V20H28V15L20 10Z" fill="#FF6B00"/>
                <path d="M12 20L20 25L28 20" stroke="#FF6B00" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div>
              <h1>Learning Path</h1>
              <p className="subtitle">Track your progress and plan your learning journey</p>
            </div>
          </div>

          {/* Loading State */}
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
        {/* Page Header */}
        <div className="page-header">
          <div className="header-icon">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="40" height="40" rx="10" fill="#FFEBCD"/>
              <path d="M20 10L12 15V20H28V15L20 10Z" fill="#FF6B00"/>
              <path d="M12 20L20 25L28 20" stroke="#FF6B00" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <h1>Learning Path</h1>
            <p className="subtitle">Track your progress and plan your learning journey</p>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        {/* Current Learning Path */}
        <div className="path-section">
          <h2 className="section-title">📚 Your Current Path</h2>
          
          {topics.length === 0 ? (
            <div className="empty-state">
              <p>No topics in your learning path yet.</p>
            </div>
          ) : (
            <div className="topics-list">
              {topics.map((topic, idx) => (
                <div 
                  key={topic.id || idx} 
                  className={`topic-card ${topic.completed ? 'completed' : ''}`}
                  onClick={() => handleTopicClick(topic)}
                >
                  <div className="topic-number-circle">
                    {idx + 1}
                  </div>
                  <div className="topic-content">
                    <h3>{topic.name || topic}</h3>
                    {topic.description && (
                      <p className="topic-description">{topic.description}</p>
                    )}
                  </div>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation(); // prevent triggering handleTopicClick
                      markAsCompleted(topic.id || idx);
                    }}
                    className={`complete-btn ${topic.completed ? 'completed' : ''}`}
                  >
                    {topic.completed ? (
                      <>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M9 12L11 14L15 10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        Completed
                      </>
                    ) : (
                      <>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M9 12L11 14L15 10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        Mark Complete
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Progress Summary */}
        {topics.length > 0 && (
          <div className="progress-section">
            <h2 className="section-title">Progress Summary</h2>
            
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

            {/* Overall Progress Bar */}
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