// // src/pages/Explanation.jsx
// import React, { useState, useEffect } from "react";
// import { getExplanation, getExplanationHistory, updateAnalytics } from "../api/api";
// import { useLocation } from "react-router-dom";
// import "./Explanation.css";

// const Explanation = () => {
//   const location = useLocation();
//   const [topic, setTopic] = useState("");
//   const [level, setLevel] = useState("beginner");
//   const [explanation, setExplanation] = useState("");
//   const [history, setHistory] = useState([]);
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState("");
//   const [isComplete, setIsComplete] = useState(false);

//   // 🔄 Parse topic from URL query params AND location.state
//   useEffect(() => {
//     const params = new URLSearchParams(location.search);
//     const urlTopic = params.get("topic");
//     const stateTopic = location.state?.topic;

//     const initialTopic = urlTopic || stateTopic;

//     if (initialTopic && initialTopic !== topic) {
//       setTopic(decodeURIComponent(initialTopic)); // decode %20 → space
//       handleGetExplanation(decodeURIComponent(initialTopic), level, true);
//     }
//   }, [location.search, location.state]);

//   // 🔁 Load history on mount (with deduplication)
//   useEffect(() => {
//     loadHistory();
//   }, []);

//   const loadHistory = async () => {
//     try {
//       const res = await getExplanationHistory();
//       const data = Array.isArray(res.data) ? res.data : [];

//       // ✅ Deduplicate by topic + level on load
//       const seen = new Set();
//       const uniqueData = data.filter((item) => {
//         const key = `${item.topic}-${item.level}`;
//         if (seen.has(key)) return false;
//         seen.add(key);
//         return true;
//       });

//       const formatted = uniqueData.map((item) => ({
//         id: item.id,
//         topic: item.topic,
//         level: item.level,
//         style: item.style,
//         explanation: item.content,
//       }));
//       setHistory(formatted);
//     } catch (err) {
//       console.error("Failed to load explanation history:", err);
//       // Silent fail for history
//     }
//   };

//   const handleGetExplanation = async (customTopic, customLevel, auto = false) => {
//     const selectedTopic = (customTopic || topic).trim();
//     const selectedLevel = customLevel || level;

//     if (!selectedTopic) {
//       setError("Please enter a topic");
//       return;
//     }

//     setError("");
//     setIsLoading(true);
//     setExplanation("");
//     setIsComplete(false);

//     try {
//       const res = await getExplanation(selectedTopic, selectedLevel);

//       const explanationText =
//         res.data.explanation || res.data.content || "No explanation available";

//       setExplanation(explanationText);
//       setTopic(selectedTopic);

//       const newEntry = {
//         id: res.data.id,
//         topic: selectedTopic,
//         level: selectedLevel,
//         style: res.data.style || "visual",
//         explanation: explanationText,
//         timestamp: new Date(),
//       };

//       // ✅ Add to history — but deduplicate by topic + level
//       setHistory((prev) => {
//         const filtered = prev.filter(
//           (item) => !(item.topic === newEntry.topic && item.level === newEntry.level)
//         );
//         return [newEntry, ...filtered].slice(0, 10);
//       });

//       // ✅ Update analytics
//       try {
//         await updateAnalytics({
//           type: "explanation",
//           topic: selectedTopic,
//           status: "completed",
//         });
//         setIsComplete(true);
//       } catch (analyticsErr) {
//         console.warn("Analytics update failed:", analyticsErr);
//       }
//     } catch (err) {
//       console.error("Explanation error:", err);
//       if (err.response) {
//         const status = err.response.status;
//         const detail = err.response.data?.detail || err.response.data?.message;
//         if (status === 500) {
//           setError(`Server error: ${detail || "The explanation service encountered an error. Please try again."}`);
//         } else if (status === 401) {
//           setError("Authentication required. Please log in again.");
//         } else if (status === 422) {
//           setError("Invalid request. Please check your input.");
//         } else {
//           setError(detail || "Failed to get explanation. Please try again.");
//         }
//       } else if (err.request) {
//         setError("Cannot connect to server. Please check your internet connection.");
//       } else {
//         setError("An unexpected error occurred. Please try again.");
//       }
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === "Enter" && !isLoading) {
//       handleGetExplanation();
//     }
//   };

//   const loadFromHistory = (item) => {
//     setTopic(item.topic);
//     setLevel(item.level);
//     setExplanation(item.explanation);
//     setIsComplete(false);
//     setError("");
//   };

//   return (
//     <div className="explanation-page">
//       {/* Module Header */}
//       <div className="module-header">
//         <div className="module-icon">📖</div>
//         <h1>Explanation Module</h1>
//         <p className="subtitle">Get detailed explanations on any topic</p>
//       </div>

//       {/* Explanation Input Card */}
//       <div className="explanation-card">
//         <div className="input-group">
//           <label htmlFor="topic-input">Topic</label>
//           <input
//             id="topic-input"
//             value={topic}
//             onChange={(e) => setTopic(e.target.value)}
//             onKeyPress={handleKeyPress}
//             placeholder="Enter a topic (e.g., Transformers, Neural Networks)..."
//             disabled={isLoading}
//           />
//         </div>

//         <div className="input-group">
//           <label htmlFor="level-select">Difficulty Level</label>
//           <div className="select-wrapper">
//             <select
//               id="level-select"
//               value={level}
//               onChange={(e) => setLevel(e.target.value)}
//               disabled={isLoading}
//             >
//               <option value="beginner">Beginner</option>
//               <option value="intermediate">Intermediate</option>
//               <option value="advanced">Advanced</option>
//             </select>
//           </div>
//         </div>

//         <button
//           onClick={() => handleGetExplanation()}
//           disabled={isLoading || !topic.trim()}
//           className={`get-explanation-btn ${isLoading ? "loading" : ""}`}
//         >
//           {isLoading ? "Getting Explanation..." : "✨ Get Explanation"}
//         </button>
//       </div>

//       {error && <div className="error-message">⚠️ {error}</div>}

//       {explanation && (
//         <div className="explanation-result">
//           <h3>📝 Explanation: {topic}</h3>
//           <div className="explanation-content">
//             <p style={{ whiteSpace: "pre-wrap" }}>{explanation}</p>
//           </div>
//           {isComplete && <p className="success-message">✅ Topic marked complete</p>}
//         </div>
//       )}

//       {/* Recent Topics Section */}
//       {history.length > 0 && (
//         <div className="recent-topics-section">
//           <h2 className="section-title">
//             <span>⏱️</span> Recent Topics
//           </h2>
//           <div className="recent-topics-grid">
//             {history.slice(0, window.innerWidth >= 1200 ? 9 : 8).map((item, idx) => (
//               <div
//                 key={`${item.topic}-${item.level}-${idx}`}
//                 className="topic-card"
//                 onClick={() => loadFromHistory(item)}
//               >
//                 <div className="card-header">
//                   <h3>{item.topic}</h3>
//                   <span className={`level-badge ${item.level}`}>{item.level}</span>
//                 </div>
//                 <p className="topic-preview">
//                   {item.explanation?.substring(0, 200)}...
//                 </p>
//               </div>
//             ))}
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default Explanation;

// src/pages/Explanation.jsx
import React, { useState, useEffect } from "react";
import {
  getExplanation,
  getExplanationHistory,
  updateAnalytics,
  getLearningPath,
  updateLearningPath,
} from "../api/api";
import { useLocation } from "react-router-dom";
import "./Explanation.css";

const Explanation = () => {
  const location = useLocation();
  const [topic, setTopic] = useState("");
  const [level, setLevel] = useState("beginner");
  const [explanation, setExplanation] = useState("");
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  // 🔄 Parse topic from URL query params AND location.state
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const urlTopic = params.get("topic");
    const stateTopic = location.state?.topic;

    const initialTopic = urlTopic || stateTopic;

    if (initialTopic && initialTopic !== topic) {
      const decoded = decodeURIComponent(initialTopic);
      setTopic(decoded);
      handleGetExplanation(decoded, level, true);
    }
  }, [location.search, location.state]);

  // 🔁 Load history on mount (with deduplication)
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await getExplanationHistory();
      const data = Array.isArray(res.data) ? res.data : [];

      const seen = new Set();
      const uniqueData = data.filter((item) => {
        const key = `${item.topic}-${item.level}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });

      const formatted = uniqueData.map((item) => ({
        id: item.id,
        topic: item.topic,
        level: item.level,
        style: item.style,
        explanation: item.content,
      }));
      setHistory(formatted);
    } catch (err) {
      console.error("Failed to load explanation history:", err);
    }
  };

  // 🔁 NEW: Sync topic completion with Learning Path
  const syncTopicWithLearningPath = async (topicName) => {
    try {
      const pathRes = await getLearningPath();
      let currentTopics = pathRes.data?.topics || pathRes.data || [];

      // Normalize topics to objects
      const normalized = currentTopics.map((t, idx) => {
        if (typeof t === 'string') {
          return { id: idx, name: t, completed: false, description: '' };
        }
        return {
          id: t.id ?? idx,
          name: t.name || t.topic || t,
          completed: t.completed ?? false,
          description: t.description || '',
        };
      });

      // Check if topic already completed
      const alreadyCompleted = normalized.some(t => t.name === topicName && t.completed);
      if (alreadyCompleted) return;

      // Mark as completed
      const updated = normalized.map(t =>
        t.name === topicName ? { ...t, completed: true } : t
      );

      await updateLearningPath({ topics: updated });
      console.log(`✅ Topic "${topicName}" marked complete in learning path`);
    } catch (err) {
      console.warn("Failed to sync with learning path:", err);
      // Non-blocking: analytics already updated
    }
  };

  const handleGetExplanation = async (customTopic, customLevel, auto = false) => {
    const selectedTopic = (customTopic || topic).trim();
    const selectedLevel = customLevel || level;

    if (!selectedTopic) {
      setError("Please enter a topic");
      return;
    }

    setError("");
    setIsLoading(true);
    setExplanation("");
    setIsComplete(false);

    try {
      const res = await getExplanation(selectedTopic, selectedLevel);

      const explanationText =
        res.data.explanation || res.data.content || "No explanation available";

      setExplanation(explanationText);
      setTopic(selectedTopic);

      const newEntry = {
        id: res.data.id,
        topic: selectedTopic,
        level: selectedLevel,
        style: res.data.style || "visual",
        explanation: explanationText,
        timestamp: new Date(),
      };

      setHistory((prev) => {
        const filtered = prev.filter(
          (item) => !(item.topic === newEntry.topic && item.level === newEntry.level)
        );
        return [newEntry, ...filtered].slice(0, 10);
      });

      // ✅ Update analytics
      try {
        await updateAnalytics({
          type: "explanation",
          topic: selectedTopic,
          status: "completed",
        });
      } catch (analyticsErr) {
        console.warn("Analytics update failed:", analyticsErr);
      }

      // ✅ ALSO sync with Learning Path
      await syncTopicWithLearningPath(selectedTopic);
      setIsComplete(true);
    } catch (err) {
      console.error("Explanation error:", err);
      if (err.response) {
        const status = err.response.status;
        const detail = err.response.data?.detail || err.response.data?.message;
        if (status === 500) {
          setError(`Server error: ${detail || "The explanation service encountered an error. Please try again."}`);
        } else if (status === 401) {
          setError("Authentication required. Please log in again.");
        } else if (status === 422) {
          setError("Invalid request. Please check your input.");
        } else {
          setError(detail || "Failed to get explanation. Please try again.");
        }
      } else if (err.request) {
        setError("Cannot connect to server. Please check your internet connection.");
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !isLoading) {
      handleGetExplanation();
    }
  };

  const loadFromHistory = (item) => {
    setTopic(item.topic);
    setLevel(item.level);
    setExplanation(item.explanation);
    setIsComplete(false);
    setError("");
  };

  return (
    <div className="explanation-page">
      <div className="module-header">
        <div className="module-icon">📖</div>
        <h1>Explanation Module</h1>
        <p className="subtitle">Get detailed explanations on any topic</p>
      </div>

      <div className="explanation-card">
        <div className="input-group">
          <label htmlFor="topic-input">Topic</label>
          <input
            id="topic-input"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter a topic (e.g., Transformers, Neural Networks)..."
            disabled={isLoading}
          />
        </div>

        <div className="input-group">
          <label htmlFor="level-select">Difficulty Level</label>
          <div className="select-wrapper">
            <select
              id="level-select"
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              disabled={isLoading}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        <button
          onClick={() => handleGetExplanation()}
          disabled={isLoading || !topic.trim()}
          className={`get-explanation-btn ${isLoading ? "loading" : ""}`}
        >
          {isLoading ? "Getting Explanation..." : "✨ Get Explanation"}
        </button>
      </div>

      {error && <div className="error-message">⚠️ {error}</div>}

      {explanation && (
        <div className="explanation-result">
          <h3>📝 Explanation: {topic}</h3>
          <div className="explanation-content">
            <p style={{ whiteSpace: "pre-wrap" }}>{explanation}</p>
          </div>
          {isComplete && <p className="success-message">✅ Topic marked complete</p>}
        </div>
      )}

      {history.length > 0 && (
        <div className="recent-topics-section">
          <h2 className="section-title">
            <span>⏱️</span> Recent Topics
          </h2>
          <div className="recent-topics-grid">
            {history.slice(0, 8).map((item, idx) => (
              <div
                key={`${item.topic}-${item.level}-${idx}`}
                className="topic-card"
                onClick={() => loadFromHistory(item)}
              >
                <div className="card-header">
                  <h3>{item.topic}</h3>
                  <span className={`level-badge ${item.level}`}>{item.level}</span>
                </div>
                <p className="topic-preview">
                  {item.explanation?.substring(0, 200)}...
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Explanation;