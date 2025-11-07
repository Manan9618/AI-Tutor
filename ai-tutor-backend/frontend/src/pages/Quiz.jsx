// // src/pages/Quiz.jsx
// import React, { useState, useEffect } from "react";
// import { getQuiz, submitQuizAnswer, updateAnalytics, getQuizHistory } from "../api/api"; // Added getQuizHistory
// import { useLocation } from "react-router-dom";
// import "./Quiz.css";

// const Quiz = () => {
//   const location = useLocation();
//   const [topic, setTopic] = useState("");
//   const [level, setLevel] = useState("beginner"); // New state for difficulty level
//   const [numQuestions, setNumQuestions] = useState("5"); // New state for number of questions
//   const [quiz, setQuiz] = useState(null);
//   const [answers, setAnswers] = useState({});
//   const [results, setResults] = useState(null);
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState("");
//   const [isComplete, setIsComplete] = useState(false);
//   const [history, setHistory] = useState([]); // New state for quiz history

//   // Auto-load quiz if navigated from Learning Path
//   useEffect(() => {
//     const stateTopic = location.state?.topic;
//     if (stateTopic) {
//       setTopic(stateTopic);
//       handleLoadQuiz(stateTopic, true);
//     }
//   }, [location.state]);

//   // Load quiz history on component mount
//   useEffect(() => {
//     loadHistory();
//   }, []);

//   const loadHistory = async () => {
//     try {
//       const res = await getQuizHistory(); // Assuming this API exists
//       const data = Array.isArray(res.data) ? res.data : [];
//       setHistory(data.map(item => ({
//         id: item.id,
//         topic: item.topic,
//         level: item.level,
//         score: item.score || 0,
//         total: item.total || 10, // Assuming total is 10 by default
//         duration: item.duration || "0 min",
//         date: item.date || new Date().toISOString(),
//       })));
//     } catch (err) {
//       console.error("Failed to load quiz history:", err);
//       // Optionally set an error message or just proceed silently
//     }
//   };

//   const handleLoadQuiz = async (customTopic, customLevel, customNumQuestions, auto = false) => {
//     const selectedTopic = customTopic || topic;
//     const selectedLevel = customLevel || level;
//     const selectedNumQuestions = customNumQuestions || numQuestions;

//     if (!selectedTopic.trim()) {
//       setError("Please enter a topic");
//       return;
//     }

//     setError("");
//     setIsLoading(true);
//     setQuiz(null);
//     setResults(null);

//     try {
//       const res = await getQuiz(selectedTopic, selectedLevel, selectedNumQuestions); // Updated API call
//       setQuiz(res.data);
//     } catch (err) {
//       setError("Failed to load quiz. Try another topic.");
//       console.error("Quiz error:", err);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleSubmit = async () => {
//     if (!quiz) return;
//     try {
//       setIsLoading(true);
//       const res = await submitQuizAnswer(topic, answers);
//       setResults(res.data);

//       // ✅ Automatically update analytics after quiz submission
//       await updateAnalytics({
//         type: "quiz",
//         topic,
//         status: "completed",
//         score: res.data.score || 0,
//       });
//       setIsComplete(true);
//     } catch (err) {
//       setError("Error submitting quiz. Please try again.");
//       console.error(err);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleAnswerChange = (questionId, value) => {
//     setAnswers((prev) => ({ ...prev, [questionId]: value }));
//   };

//   const handleMarkComplete = async () => {
//     try {
//       await updateAnalytics({
//         type: "quiz",
//         topic,
//         status: "completed",
//       });
//       setIsComplete(true);
//       alert("✅ Quiz marked complete and added to analytics!");
//     } catch (err) {
//       console.error("Failed to update analytics:", err);
//       alert("⚠️ Failed to update analytics.");
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === "Enter") handleLoadQuiz();
//   };

//   return (
//     <div className="page quiz-page">
//       {/* Module Header */}
//       <div className="module-header">
//         <div className="module-icon">📋</div>
//         <h1>Quiz Module</h1>
//         <p className="subtitle">Test your understanding of any topic</p>
//       </div>

//       {/* Feature Cards */}
//       <div className="feature-cards">
//         <div className="feature-card">
//           <div className="feature-icon">🎯</div>
//           <h3>Adaptive</h3>
//           <p>Questions adjust to your level</p>
//         </div>
//         <div className="feature-card">
//           <div className="feature-icon">⏱️</div>
//           <h3>Timed</h3>
//           <p>Track your speed</p>
//         </div>
//         <div className="feature-card">
//           <div className="feature-icon">🏆</div>
//           <h3>Scored</h3>
//           <p>Instant feedback</p>
//         </div>
//       </div>

//       {/* Quiz Input Card */}
//       <div className="quiz-card">
//         <div className="input-group">
//           <label htmlFor="quiz-topic-input">Topic</label>
//           <input
//             id="quiz-topic-input"
//             value={topic}
//             onChange={(e) => setTopic(e.target.value)}
//             onKeyPress={handleKeyPress}
//             placeholder="Enter a topic..."
//             disabled={isLoading}
//           />
//         </div>

//         <div className="input-row">
//           <div className="input-group">
//             <label htmlFor="difficulty-select">Difficulty Level</label>
//             <select
//               id="difficulty-select"
//               value={level}
//               onChange={(e) => setLevel(e.target.value)}
//               disabled={isLoading}
//             >
//               <option value="beginner">Beginner</option>
//               <option value="intermediate">Intermediate</option>
//               <option value="advanced">Advanced</option>
//             </select>
//           </div>

//           <div className="input-group">
//             <label htmlFor="questions-select">Number of Questions</label>
//             <select
//               id="questions-select"
//               value={numQuestions}
//               onChange={(e) => setNumQuestions(e.target.value)}
//               disabled={isLoading}
//             >
//               <option value="5">5 Questions</option>
//               <option value="10">10 Questions</option>
//               <option value="15">15 Questions</option>
//             </select>
//           </div>
//         </div>

//         <button
//           onClick={() => handleLoadQuiz(topic, level, numQuestions)}
//           disabled={isLoading || !topic.trim()}
//           className={`start-quiz-btn ${isLoading ? 'loading' : ''}`}
//         >
//           {isLoading ? "Starting..." : "▶️ Start Quiz"}
//         </button>
//       </div>

//       {error && <div className="error-message">{error}</div>}

//       {/* Quiz Container */}
//       {quiz?.questions && (
//         <div className="quiz-container">
//           <h2>{`Quiz on ${topic}`}</h2>
//           {quiz.questions.map((q, idx) => (
//             <div key={q.id || idx} className="quiz-question">
//               <p>
//                 <strong>{idx + 1}. {q.question}</strong>
//               </p>
//               <input
//                 type="text"
//                 placeholder="Type your answer..."
//                 value={answers[q.id] || ""}
//                 onChange={(e) => handleAnswerChange(q.id, e.target.value)}
//                 className="answer-input"
//               />
//             </div>
//           ))}

//           <button
//             onClick={handleSubmit}
//             className="submit-btn"
//             disabled={isLoading}
//           >
//             {isLoading ? "Submitting..." : "Submit Quiz"}
//           </button>
//         </div>
//       )}

//       {/* Results Section */}
//       {results && (
//         <div className="quiz-results">
//           <h2>🏆 Your Results</h2>
//           <div className="score-display">
//             <span className="score-text">
//               {results.score}/{results.total || 10}
//             </span>
//             <span className={`score-percentage ${results.score >= 70 ? 'good' : 'needs-improvement'}`}>
//               {results.score}% 
//             </span>
//           </div>

//           {results.feedback && (
//             <div className="quiz-feedback">
//               <h4>Feedback:</h4>
//               <p>{results.feedback}</p>
//             </div>
//           )}

//           {!isComplete && (
//             <button className="mark-complete-btn" onClick={handleMarkComplete}>
//               ✅ Mark Complete
//             </button>
//           )}
//           {isComplete && <p className="success-message">✅ Quiz marked complete</p>}
//         </div>
//       )}

//       {/* Quiz History Section */}
//       {history.length > 0 && (
//         <div className="quiz-history-section">
//           <h2 className="section-title">
//             <span>⏱️</span> Quiz History
//           </h2>
//           <div className="quiz-history-grid">
//             {history.map((item, idx) => (
//               <div key={idx} className="history-card">
//                 <div className="card-header">
//                   <h3>{item.topic}</h3>
//                   <span className={`level-badge ${item.level}`}>{item.level}</span>
//                 </div>
//                 <div className="score-row">
//                   <span className="score-display">
//                     <span className="trophy">🏆</span>
//                     <span className="score-text">{item.score}/{item.total}</span>
//                   </span>
//                   <span className={`score-percentage ${item.score >= 70 ? 'good' : 'needs-improvement'}`}>
//                     {item.score}%
//                   </span>
//                 </div>
//                 <div className="progress-bar">
//                   <div
//                     className="progress-fill"
//                     style={{ width: `${(item.score / item.total) * 100}%` }}
//                   ></div>
//                 </div>
//                 <div className="meta-row">
//                   <span className="date"><span>📅</span> {new Date(item.date).toLocaleDateString()}</span>
//                   <span className="duration"><span>⏱️</span> {item.duration}</span>
//                 </div>
//               </div>
//             ))}
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default Quiz;

// src/pages/Quiz.jsx
import React, { useState, useEffect } from "react";
import { getQuiz, submitQuizAnswer, updateAnalytics, getQuizHistory } from "../api/api";
import { useLocation } from "react-router-dom";
import "./Quiz.css";

const Quiz = () => {
  const location = useLocation();
  const [topic, setTopic] = useState("");
  const [level, setLevel] = useState("beginner");
  const [numQuestions, setNumQuestions] = useState("5");
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isComplete, setIsComplete] = useState(false);
  const [history, setHistory] = useState([]);

  // Auto-load quiz if navigated from Learning Path
  useEffect(() => {
    const stateTopic = location.state?.topic;
    if (stateTopic) {
      setTopic(stateTopic);
      handleLoadQuiz(stateTopic, true);
    }
  }, [location.state]);

  // Load quiz history on component mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await getQuizHistory();
      const data = Array.isArray(res.data) ? res.data : [];
      setHistory(data.map(item => ({
        id: item.id,
        topic: item.topic,
        level: item.level,
        score: item.score || 0,
        total: item.total || 10,
        duration: item.duration || "0 min",
        date: item.date || new Date().toISOString(),
      })));
    } catch (err) {
      console.error("Failed to load quiz history:", err);
    }
  };

  const handleLoadQuiz = async (customTopic, customLevel, customNumQuestions, auto = false) => {
    const selectedTopic = customTopic || topic;
    const selectedLevel = customLevel || level;
    const selectedNumQuestions = customNumQuestions || numQuestions;

    if (!selectedTopic.trim()) {
      setError("Please enter a topic");
      return;
    }

    setError("");
    setIsLoading(true);
    setQuiz(null);
    setResults(null);

    try {
      const res = await getQuiz(selectedTopic, selectedLevel, selectedNumQuestions);
      setQuiz(res.data);
    } catch (err) {
      setError("Failed to load quiz. Try another topic.");
      console.error("Quiz error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!quiz) return;
    try {
      setIsLoading(true);
      const res = await submitQuizAnswer(topic, answers);
      setResults(res.data);

      await updateAnalytics({
        type: "quiz",
        topic,
        status: "completed",
        score: res.data.score || 0,
      });
      setIsComplete(true);
    } catch (err) {
      setError("Error submitting quiz. Please try again.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  };

  const handleMarkComplete = async () => {
    try {
      await updateAnalytics({
        type: "quiz",
        topic,
        status: "completed",
      });
      setIsComplete(true);
      alert("✅ Quiz marked complete and added to analytics!");
    } catch (err) {
      console.error("Failed to update analytics:", err);
      alert("⚠️ Failed to update analytics.");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleLoadQuiz();
  };

  return (
    <div className="quiz-page">
      {/* Module Header */}
      <div className="module-header">
        <div className="module-icon">📋</div>
        <h1>Quiz Module</h1>
        <p className="subtitle">Test your understanding of any topic</p>
      </div>

      {/* Feature Cards */}
      <div className="feature-cards">
        <div className="feature-card">
          <div className="feature-icon">🎯</div>
          <h3>Adaptive</h3>
          <p>Questions adjust to your level</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">⏱️</div>
          <h3>Timed</h3>
          <p>Track your speed</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🏆</div>
          <h3>Scored</h3>
          <p>Instant feedback</p>
        </div>
      </div>

      {/* Quiz Input Card */}
      <div className="quiz-card">
        <div className="input-group">
          <label htmlFor="quiz-topic-input">Topic</label>
          <input
            id="quiz-topic-input"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter a topic..."
            disabled={isLoading}
          />
        </div>

        <div className="input-row">
          <div className="input-group">
            <label htmlFor="difficulty-select">Difficulty Level</label>
            <select
              id="difficulty-select"
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              disabled={isLoading}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          <div className="input-group">
            <label htmlFor="questions-select">Number of Questions</label>
            <select
              id="questions-select"
              value={numQuestions}
              onChange={(e) => setNumQuestions(e.target.value)}
              disabled={isLoading}
            >
              <option value="5">5 Questions</option>
              <option value="10">10 Questions</option>
              <option value="15">15 Questions</option>
            </select>
          </div>
        </div>

        <button
          onClick={() => handleLoadQuiz(topic, level, numQuestions)}
          disabled={isLoading || !topic.trim()}
          className={`start-quiz-btn ${isLoading ? 'loading' : ''}`}
        >
          {isLoading ? "Starting..." : "▶️ Start Quiz"}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Quiz Container */}
      {quiz?.questions && (
        <div className="quiz-container">
          <h2>{`Quiz on ${topic}`}</h2>
          {quiz.questions.map((q, idx) => (
            <div key={q.id || idx} className="quiz-question">
              <p>
                <strong>{idx + 1}. {q.question}</strong>
              </p>
              <input
                type="text"
                placeholder="Type your answer..."
                value={answers[q.id] || ""}
                onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                className="answer-input"
              />
            </div>
          ))}

          <button
            onClick={handleSubmit}
            className="submit-btn"
            disabled={isLoading}
          >
            {isLoading ? "Submitting..." : "Submit Quiz"}
          </button>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="quiz-results">
          <h2>🏆 Your Results</h2>
          <div className="score-display">
            <span className="score-text">
              {results.score}/{results.total || 10}
            </span>
            <span className={`score-percentage ${results.score >= 70 ? 'good' : 'needs-improvement'}`}>
              {results.score}% 
            </span>
          </div>

          {results.feedback && (
            <div className="quiz-feedback">
              <h4>Feedback:</h4>
              <p>{results.feedback}</p>
            </div>
          )}

          {!isComplete && (
            <button className="mark-complete-btn" onClick={handleMarkComplete}>
              ✅ Mark Complete
            </button>
          )}
          {isComplete && <p className="success-message">✅ Quiz marked complete</p>}
        </div>
      )}

      {/* Quiz History Section */}
      {history.length > 0 && (
        <div className="quiz-history-section">
          <h2 className="section-title">
            <span>⏱️</span> Quiz History
          </h2>
          <div className="quiz-history-grid">
            {history.slice(0, 8).map((item, idx) => (
              <div key={idx} className="history-card">
                <div className="card-header">
                  <h3>{item.topic}</h3>
                  <span className={`level-badge ${item.level}`}>{item.level}</span>
                </div>
                <div className="score-row">
                  <span className="score-display">
                    <span className="trophy">🏆</span>
                    <span className="score-text">{item.score}/{item.total}</span>
                  </span>
                  <span className={`score-percentage ${item.score >= 70 ? 'good' : 'needs-improvement'}`}>
                    {item.score}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${(item.score / item.total) * 100}%` }}
                  ></div>
                </div>
                <div className="meta-row">
                  <span className="date"><span>📅</span> {new Date(item.date).toLocaleDateString()}</span>
                  <span className="duration"><span>⏱️</span> {item.duration}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Quiz;