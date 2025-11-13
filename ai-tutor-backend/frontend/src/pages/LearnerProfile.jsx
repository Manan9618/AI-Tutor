// // src/pages/LearnerProfile.jsx
// import React, { useState, useEffect } from "react";
// import { getLearnerProfile, updateLearnerProfile, getLearnerProgress } from "../api/api";
// import "./LearnerProfile.css";

// const LearnerProfile = () => {
//   const [profile, setProfile] = useState(null);
//   const [progress, setProgress] = useState(null);
//   const [isLoading, setIsLoading] = useState(true);
//   const [error, setError] = useState("");
//   const [activeTab, setActiveTab] = useState("achievements"); // achievements, preferences, settings
//   const [isEditingProfile, setIsEditingProfile] = useState(false); // 👈 NEW STATE

//   useEffect(() => {
//     loadProfile();
//   }, []);

//   const loadProfile = async () => {
//     setIsLoading(true);
//     try {
//       const res = await getLearnerProfile(); // hits /api/learner/profile
//       const { profile, progress, achievements } = res.data;

//       setProfile(profile);
//       setProgress(progress);
//     } catch (err) {
//       setError("Failed to load learner profile");
//       console.error("Profile error:", err);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleUpdatePreferences = async () => {
//     try {
//       await updateLearnerProfile(profile);
//       alert("Preferences saved successfully!");
//     } catch (err) {
//       console.error("Preferences update error:", err);
//       setError("Failed to save preferences");
//     }
//   };

//   const handleSaveProfile = async () => {
//     try {
//       await updateLearnerProfile(profile); // Send updated profile
//       setIsEditingProfile(false); // Exit edit mode
//       alert("Profile updated successfully!");
//     } catch (err) {
//       console.error("Profile update error:", err);
//       setError("Failed to update profile");
//     }
//   };

//   const handleCancelEdit = () => {
//     // Optionally reload profile to revert changes
//     loadProfile();
//     setIsEditingProfile(false);
//   };

//   if (isLoading) {
//     return (
//       <div className="learner-profile-page">
//         <div className="page-header">
//           <h1>👤 Learner Profile</h1>
//           <p className="subtitle">Manage your learning preferences and progress</p>
//         </div>
//         <div className="loading-state">
//           <div className="spinner"></div>
//           <p>Loading your profile...</p>
//         </div>
//       </div>
//     );
//   }

//   if (!profile) {
//     return (
//       <div className="learner-profile-page">
//         <div className="page-header">
//           <h1>👤 Learner Profile</h1>
//           <p className="subtitle">Manage your learning preferences and progress</p>
//         </div>
//         <div className="empty-state">
//           <p>No profile data found. Please contact support.</p>
//         </div>
//       </div>
//     );
//   }

//   // Generate initials for avatar
//   const getInitials = (name) => {
//     if (!name) return "A";
//     const parts = name.split(" ");
//     return parts.length > 1 ? `${parts[0][0]}${parts[1][0]}` : parts[0][0];
//   };

//   return (
//     <div className="learner-profile-page">
//       {/* Page Header */}
//       <div className="page-header">
//         <h1>👤 Learner Profile</h1>
//         <p className="subtitle">Manage your learning preferences and progress</p>
//       </div>

//       {error && <div className="error-message">{error}</div>}

//       {/* Profile Card */}
//       <div className="profile-card">
//         <div className="profile-header">
//           <div className="avatar-circle">
//             <span>{getInitials(profile.name)}</span>
//           </div>
//           <div className="profile-info">
//             {isEditingProfile ? (
//               // ✏️ Edit Mode: Show inputs
//               <>
//                 <div className="edit-fields">
//                   <input
//                     type="text"
//                     value={profile.name || ""}
//                     onChange={(e) => setProfile({ ...profile, name: e.target.value })}
//                     placeholder="Enter your full name"
//                     className="edit-input"
//                   />
//                   <input
//                     type="email"
//                     value={profile.email || ""}
//                     onChange={(e) => setProfile({ ...profile, email: e.target.value })}
//                     placeholder="Enter your email address"
//                     className="edit-input"
//                   />
//                 </div>
//               </>
//             ) : (
//               // 👁️ View Mode: Show static text
//               <>
//                 <h2>{profile.name || "Learner"}</h2>
//                 <div className="profile-meta">
//                   <span><i className="icon-email">✉️</i> {profile.email || "N/A"}</span>
//                   <span><i className="icon-location">📍</i> {profile.location || "Unknown"}</span>
//                   <span><i className="icon-calendar">📅</i> Joined {profile.joinedDate || "N/A"}</span>
//                 </div>
//                 <div className="level-badge">
//                   {profile.level || "Beginner"} Learner
//                 </div>
//               </>
//             )}
//           </div>
//           <div className="profile-actions">
//             {isEditingProfile ? (
//               <>
//                 <button onClick={handleSaveProfile} className="save-btn">
//                   <i className="icon-check">✅</i> Save
//                 </button>
//                 <button onClick={handleCancelEdit} className="cancel-btn">
//                   <i className="icon-cancel">❌</i> Cancel
//                 </button>
//               </>
//             ) : (
//               <button
//                 onClick={() => setIsEditingProfile(true)}
//                 className="edit-btn"
//               >
//                 <i className="icon-edit">✏️</i> Edit Profile
//               </button>
//             )}
//           </div>
//         </div>

//         {/* XP Progress Bar */}
//         <div className="xp-section">
//           <div className="xp-label">Level Progress</div>
//           <div className="xp-bar-container">
//             <div
//               className="xp-bar-fill"
//               style={{ width: `${(profile.xp / profile.nextLevelXp) * 100}%` }}
//             ></div>
//           </div>
//           <div className="xp-stats">
//             <span>{profile.xp || 0} / {profile.nextLevelXp || 4000} XP</span>
//             <span>{profile.nextLevelXp - profile.xp || 750} XP to next level</span>
//           </div>
//         </div>
//       </div>

//       {/* Stats Cards */}
//       <div className="stats-grid">
//         <div className="stat-card">
//           <div className="stat-icon"><i className="icon-clock">🕒</i></div>
//           <div className="stat-content">
//             <div className="stat-title">Total Study Time</div>
//             <div className="stat-value">{progress?.totalStudyTime || "0h 0m"}</div>
//           </div>
//         </div>
//         <div className="stat-card">
//           <div className="stat-icon"><i className="icon-target">🎯</i></div>
//           <div className="stat-content">
//             <div className="stat-title">Topics Mastered</div>
//             <div className="stat-value">{progress?.topicsMastered || 0}</div>
//           </div>
//         </div>
//         <div className="stat-card">
//           <div className="stat-icon"><i className="icon-trophy">🏆</i></div>
//           <div className="stat-content">
//             <div className="stat-title">Quiz Average</div>
//             <div className="stat-value">{progress?.quizAverage || 0}%</div>
//           </div>
//         </div>
//         <div className="stat-card">
//           <div className="stat-icon"><i className="icon-fire">🔥</i></div>
//           <div className="stat-content">
//             <div className="stat-title">Current Streak</div>
//             <div className="stat-value">{progress?.currentStreak || 0} days</div>
//           </div>
//         </div>
//       </div>

//       {/* Tabs */}
//       <div className="tabs">
//         <button
//           className={`tab ${activeTab === 'achievements' ? 'active' : ''}`}
//           onClick={() => setActiveTab('achievements')}
//         >
//           Achievements
//         </button>
//         <button
//           className={`tab ${activeTab === 'preferences' ? 'active' : ''}`}
//           onClick={() => setActiveTab('preferences')}
//         >
//           Preferences
//         </button>
//         <button
//           className={`tab ${activeTab === 'settings' ? 'active' : ''}`}
//           onClick={() => setActiveTab('settings')}
//         >
//           Settings
//         </button>
//       </div>

//       {/* Tab Content */}
//       {activeTab === "achievements" && (
//         <div className="tab-content">
//           <div className="section-header">
//             <h3><i className="icon-badge">🏅</i> Achievements & Badges</h3>
//             <p>Track your learning milestones and accomplishments</p>
//           </div>
//           {/* Achievements Grid */}
// <div className="achievements-grid">
//   {[
//     { 
//       title: "First Steps", 
//       description: "Complete your first learning session", 
//       date: "Jan 15, 2024", 
//       earned: true, 
//       icon: "🎯",
//       // No progress — it's earned
//     },
//     { 
//       title: "Week Warrior", 
//       description: "Study for 7 consecutive days", 
//       date: "Feb 3, 2024", 
//       earned: true, 
//       icon: "🔥",
//     },
//     { 
//       title: "Quiz Master", 
//       description: "Score 100% on 5 quizzes", 
//       date: "Feb 28, 2024", 
//       earned: true, 
//       icon: "🏆",
//     },
//     { 
//       title: "Knowledge Seeker", 
//       description: "Explore 50 different topics", 
//       progress: 68, 
//       icon: "📚",
//       // Not earned — show progress bar
//     },
//     { 
//       title: "Chat Champion", 
//       description: "Complete 100 chat sessions", 
//       progress: 45, 
//       icon: "💬",
//     },
//     { 
//       title: "Perfect Month", 
//       description: "Study every day for a month", 
//       progress: 23, 
//       icon: "⭐",
//     },
//   ].map((ach, idx) => (
//     <div key={idx} className={`achievement-card ${ach.earned ? 'earned' : 'in-progress'}`}>
//       <div className="achievement-icon">{ach.icon}</div>
//       <div className="achievement-content">
//         <h4>{ach.title}</h4>
//         <p>{ach.description}</p>

//         {/* Show date if earned */}
//         {ach.date && <span className="achievement-date">{ach.date}</span>}

//         {/* Show progress bar if not earned */}
//         {ach.progress !== undefined && (
//   <div className="progress-bar-container">
//     <div className="progress-bar">
//       <div 
//         className="progress-fill" 
//         style={{ width: `${ach.progress}%` }}
//       ></div>
//     </div>
//     <span className="progress-text">{ach.progress}% complete</span>
//   </div>
// )}
//       </div>

//       {/* Show "Earned" badge if earned */}
//       {ach.earned && <div className="earned-badge">Earned</div>}
//     </div>
//   ))}
// </div>
//         </div>
//       )}

//       {activeTab === "preferences" && (
//         <div className="tab-content">
//           <div className="section-header">
//             <h3><i className="icon-settings">⚙️</i> Learning Preferences</h3>
//             <p>Customize your learning experience</p>
//           </div>
//           <div className="preferences-form">
//             <div className="form-row">
//               <div className="form-group">
//                 <label>Preferred Learning Style</label>
//                 <select
//                   value={profile.learningStyle || "Visual"}
//                   onChange={(e) => setProfile({...profile, learningStyle: e.target.value})}
//                 >
//                   <option value="Visual">Visual</option>
//                   <option value="Auditory">Auditory</option>
//                   <option value="Reading/Writing">Reading/Writing</option>
//                   <option value="Kinesthetic">Kinesthetic</option>
//                 </select>
//               </div>
//               <div className="form-group">
//                 <label>Default Difficulty Level</label>
//                 <select
//                   value={profile.difficultyLevel || "Intermediate"}
//                   onChange={(e) => setProfile({...profile, difficultyLevel: e.target.value})}
//                 >
//                   <option value="Beginner">Beginner</option>
//                   <option value="Intermediate">Intermediate</option>
//                   <option value="Advanced">Advanced</option>
//                 </select>
//               </div>
//             </div>
//             <div className="form-row">
//               <div className="form-group">
//                 <label>Daily Learning Goal (minutes)</label>
//                 <select
//                   value={profile.dailyGoal || "30 minutes"}
//                   onChange={(e) => setProfile({...profile, dailyGoal: e.target.value})}
//                 >
//                   <option value="15 minutes">15 minutes</option>
//                   <option value="30 minutes">30 minutes</option>
//                   <option value="45 minutes">45 minutes</option>
//                   <option value="60 minutes">60 minutes</option>
//                 </select>
//               </div>
//               <div className="form-group">
//                 <label>Language</label>
//                 <select
//                   value={profile.language || "English"}
//                   onChange={(e) => setProfile({...profile, language: e.target.value})}
//                 >
//                   <option value="English">English</option>
//                   <option value="Spanish">Spanish</option>
//                   <option value="French">French</option>
//                   <option value="German">German</option>
//                 </select>
//               </div>
//             </div>
//             <div className="form-group full-width">
//               <label>Bio</label>
//               <textarea
//                 value={profile.bio || ""}
//                 onChange={(e) => setProfile({...profile, bio: e.target.value})}
//                 placeholder="Tell us about yourself..."
//               />
//             </div>
//             <div className="form-actions">
//               <button
//                 onClick={handleUpdatePreferences}
//                 className="save-btn"
//               >
//                 Save Preferences
//               </button>
//             </div>
//           </div>
//         </div>
//       )}

//       {activeTab === "settings" && (
//         <div className="tab-content">
//           <div className="section-header">
//             <h3><i className="icon-bell">🔔</i> Notification Settings</h3>
//             <p>Manage how you receive updates and alerts</p>
//           </div>
//           <div className="settings-section">
//             <div className="setting-item">
//               <div className="setting-info">
//                 <strong>Email Notifications</strong>
//                 <p>Receive learning updates via email</p>
//               </div>
//               <label className="toggle-switch">
//                 <input
//                   type="checkbox"
//                   checked={profile.emailNotifications !== false}
//                   onChange={(e) => setProfile({...profile, emailNotifications: e.target.checked})}
//                 />
//                 <span className="slider"></span>
//               </label>
//             </div>
//             <div className="setting-item">
//               <div className="setting-info">
//                 <strong>Push Notifications</strong>
//                 <p>Get push notifications for study reminders</p>
//               </div>
//               <label className="toggle-switch">
//                 <input
//                   type="checkbox"
//                   checked={profile.pushNotifications !== false}
//                   onChange={(e) => setProfile({...profile, pushNotifications: e.target.checked})}
//                 />
//                 <span className="slider"></span>
//               </label>
//             </div>
//             <div className="setting-item">
//               <div className="setting-info">
//                 <strong>Weekly Progress Reports</strong>
//                 <p>Receive weekly summaries of your learning</p>
//               </div>
//               <label className="toggle-switch">
//                 <input
//                   type="checkbox"
//                   checked={profile.weeklyReports !== false}
//                   onChange={(e) => setProfile({...profile, weeklyReports: e.target.checked})}
//                 />
//                 <span className="slider"></span>
//               </label>
//             </div>
//             <div className="setting-item">
//               <div className="setting-info">
//                 <strong>Achievement Alerts</strong>
//                 <p>Get notified when you earn new achievements</p>
//               </div>
//               <label className="toggle-switch">
//                 <input
//                   type="checkbox"
//                   checked={profile.achievementAlerts !== false}
//                   onChange={(e) => setProfile({...profile, achievementAlerts: e.target.checked})}
//                 />
//                 <span className="slider"></span>
//               </label>
//             </div>
//           </div>

//           <div className="section-header">
//             <h3><i className="icon-palette">🎨</i> Appearance</h3>
//             <p>Customize the look and feel of your interface</p>
//           </div>
//           <div className="settings-section">
//             <div className="setting-item">
//               <div className="setting-info">
//                 <strong>Theme</strong>
//               </div>
//               <select
//                 value={profile.theme || "System"}
//                 onChange={(e) => setProfile({...profile, theme: e.target.value})}
//               >
//                 <option value="System">System</option>
//                 <option value="Light">Light</option>
//                 <option value="Dark">Dark</option>
//               </select>
//             </div>
//           </div>

//           <div className="section-header">
//             <h3><i className="icon-shield">🛡️</i> Privacy & Security</h3>
//             <p>Manage your account security and data privacy</p>
//           </div>
//           <div className="settings-section">
//             <div className="setting-item">
//               <button className="security-btn">
//                 <i className="icon-lock">🔒</i> Change Password
//               </button>
//             </div>
//             <div className="setting-item">
//               <button className="security-btn">
//                 <i className="icon-gear">⚙️</i> Privacy Settings
//               </button>
//             </div>
//             <div className="setting-item">
//               <button className="delete-btn">
//                 <i className="icon-delete">❌</i> Delete Account
//               </button>
//             </div>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default LearnerProfile; 

// src/pages/LearnerProfile.jsx
import React, { useState, useEffect } from "react";
import {
  getLearnerProfile,
  updateLearnerProfile,
} from "../api/api";
import {
  getLearningPath,
  getQuizHistory,
  getProfileStats, // ✅ NEW: fetches study time & streak
} from "../api/api";
import "./LearnerProfile.css";

const LearnerProfile = () => {
  const [profile, setProfile] = useState(null);
  const [progress, setProgress] = useState({
    totalStudyTime: "0h 0m",
    topicsMastered: 0,
    quizAverage: 0,
    currentStreak: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("achievements");
  const [isEditingProfile, setIsEditingProfile] = useState(false);

  useEffect(() => {
    loadProfileAndProgress();
  }, []);

  const loadProfileAndProgress = async () => {
    setIsLoading(true);
    try {
      // 1. Load profile
      const profileRes = await getLearnerProfile();
      setProfile(profileRes.data.profile);

      // 2. Load learning path → topics mastered
      const learningPathRes = await getLearningPath();
      const completedTopics = learningPathRes.data.completed_topics || [];
      const topicsMastered = completedTopics.length;

      // 3. Load quiz history → average score
      const quizHistoryRes = await getQuizHistory();
      const quizzes = quizHistoryRes.data.quizzes || [];
      const quizCount = quizzes.length;
      const totalScore = quizzes.reduce((sum, q) => sum + (q.score || 0), 0);
      const quizAverage = quizCount > 0 ? totalScore / quizCount : 0;

      // 4. ✅ Load study time & streak
      const statsRes = await getProfileStats();
      const { total_study_time_seconds, current_streak_days } = statsRes.data;

      // Format study time as "Xh Ym"
      const hours = Math.floor(total_study_time_seconds / 3600);
      const minutes = Math.floor((total_study_time_seconds % 3600) / 60);
      const studyTimeText = `${hours}h ${minutes}m`;

      setProgress({
        totalStudyTime: studyTimeText,
        topicsMastered,
        quizAverage,
        currentStreak: current_streak_days,
      });

    } catch (err) {
      console.error("Failed to load profile/progress:", err);
      setError("Failed to load profile data. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdatePreferences = async () => {
    try {
      await updateLearnerProfile(profile);
      alert("Preferences saved successfully!");
    } catch (err) {
      console.error("Preferences update error:", err);
      setError("Failed to save preferences");
    }
  };

  const handleSaveProfile = async () => {
    try {
      await updateLearnerProfile(profile);
      setIsEditingProfile(false);
      alert("Profile updated successfully!");
    } catch (err) {
      console.error("Profile update error:", err);
      setError("Failed to update profile");
    }
  };

  const handleCancelEdit = () => {
    loadProfileAndProgress();
    setIsEditingProfile(false);
  };

  if (isLoading) {
    return (
      <div className="learner-profile-page">
        <div className="page-header">
          <h1>👤 Learner Profile</h1>
          <p className="subtitle">Manage your learning preferences and progress</p>
        </div>
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="learner-profile-page">
        <div className="page-header">
          <h1>👤 Learner Profile</h1>
          <p className="subtitle">Manage your learning preferences and progress</p>
        </div>
        <div className="empty-state">
          <p>No profile data found. Please contact support.</p>
        </div>
      </div>
    );
  }

  const getInitials = (name) => {
    if (!name) return "A";
    const parts = name.split(" ");
    return parts.length > 1 ? `${parts[0][0]}${parts[1][0]}` : parts[0][0];
  };

  return (
    <div className="learner-profile-page">
      <div className="page-header">
        <h1>👤 Learner Profile</h1>
        <p className="subtitle">Manage your learning preferences and progress</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Profile Card */}
      <div className="profile-card">
        <div className="profile-header">
          <div className="avatar-circle">
            <span>{getInitials(profile.name)}</span>
          </div>
          <div className="profile-info">
            {isEditingProfile ? (
              <>
                <div className="edit-fields">
                  <input
                    type="text"
                    value={profile.name || ""}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    placeholder="Enter your full name"
                    className="edit-input"
                  />
                  <input
                    type="email"
                    value={profile.email || ""}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    placeholder="Enter your email address"
                    className="edit-input"
                  />
                </div>
              </>
            ) : (
              <>
                <h2>{profile.name || "Learner"}</h2>
                <div className="profile-meta">
                  <span><i className="icon-email">✉️</i> {profile.email || "N/A"}</span>
                  <span><i className="icon-location">📍</i> {profile.location || "Unknown"}</span>
                  <span><i className="icon-calendar">📅</i> Joined {profile.joinedDate || "N/A"}</span>
                </div>
                <div className="level-badge">
                  {profile.level || "Beginner"} Learner
                </div>
              </>
            )}
          </div>
          <div className="profile-actions">
            {isEditingProfile ? (
              <>
                <button onClick={handleSaveProfile} className="save-btn">
                  <i className="icon-check">✅</i> Save
                </button>
                <button onClick={handleCancelEdit} className="cancel-btn">
                  <i className="icon-cancel">❌</i> Cancel
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditingProfile(true)}
                className="edit-btn"
              >
                <i className="icon-edit">✏️</i> Edit Profile
              </button>
            )}
          </div>
        </div>

        <div className="xp-section">
          <div className="xp-label">Level Progress</div>
          <div className="xp-bar-container">
            <div
              className="xp-bar-fill"
              style={{ width: `${(profile.xp / (profile.nextLevelXp || 1)) * 100}%` }}
            ></div>
          </div>
          <div className="xp-stats">
            <span>{profile.xp || 0} / {profile.nextLevelXp || 4000} XP</span>
            <span>{(profile.nextLevelXp || 4000) - (profile.xp || 0)} XP to next level</span>
          </div>
        </div>
      </div>

      {/* ✅ DYNAMIC STATS CARDS */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon"><i className="icon-clock">🕒</i></div>
          <div className="stat-content">
            <div className="stat-title">Total Study Time</div>
            <div className="stat-value">{progress.totalStudyTime}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon"><i className="icon-target">🎯</i></div>
          <div className="stat-content">
            <div className="stat-title">Topics Mastered</div>
            <div className="stat-value">{progress.topicsMastered}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon"><i className="icon-trophy">🏆</i></div>
          <div className="stat-content">
            <div className="stat-title">Quiz Average</div>
            <div className="stat-value">{progress.quizAverage.toFixed(2)}%</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon"><i className="icon-fire">🔥</i></div>
          <div className="stat-content">
            <div className="stat-title">Current Streak</div>
            <div className="stat-value">
              {progress.currentStreak > 0 ? `${progress.currentStreak} days` : "0 days"}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs & Content (unchanged below) */}
      {/* ... rest of your tabs code remains the same ... */}

      {activeTab === "achievements" && (
        <div className="tab-content">
          <div className="section-header">
            <h3><i className="icon-badge">🏅</i> Achievements & Badges</h3>
            <p>Track your learning milestones and accomplishments</p>
          </div>
          <div className="achievements-grid">
            {/* Your existing mock achievements */}
          </div>
        </div>
      )}

      {activeTab === "preferences" && (
        <div className="tab-content">
          {/* Your preferences form */}
        </div>
      )}

      {activeTab === "settings" && (
        <div className="tab-content">
          {/* Your settings */}
        </div>
      )}
    </div>
  );
};

export default LearnerProfile;