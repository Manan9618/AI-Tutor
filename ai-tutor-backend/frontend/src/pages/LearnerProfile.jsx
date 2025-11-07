import React, { useEffect, useState } from "react";
import { getLearnerProfile, updateLearnerProfile, getLearnerProgress } from "../api/api";

const LearnerProfile = () => {
  const [profile, setProfile] = useState(null);
  const [progress, setProgress] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setIsLoading(true);
    try {
      const [profileRes, progressRes] = await Promise.all([
        getLearnerProfile(),
        getLearnerProgress().catch(() => ({ data: null }))
      ]);
      setProfile(profileRes.data);
      setProgress(progressRes.data);
    } catch (err) {
      setError("Failed to load learner profile");
      console.error("Profile error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async () => {
    try {
      await updateLearnerProfile(profile);
      setIsEditing(false);
      alert("Profile updated successfully!");
    } catch (err) {
      console.error("Profile update error:", err);
      setError("Failed to update profile");
    }
  };

  if (isLoading) {
    return (
      <div className="page">
        <h1>👤 Learner Profile</h1>
        <p className="loading">Loading your profile...</p>
      </div>
    );
  }

  return (
    <div className="page learner-profile-page">
      <h1>👤 Learner Profile</h1>
      <p className="subtitle">Manage your learning preferences and progress</p>

      {error && <div className="error-message">{error}</div>}

      {profile && (
        <div className="profile-section">
          <div className="profile-info">
            <label>Name</label>
            <input
              type="text"
              value={profile.name || ""}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              disabled={!isEditing}
            />

            <label>Email</label>
            <input
              type="email"
              value={profile.email || ""}
              onChange={(e) => setProfile({ ...profile, email: e.target.value })}
              disabled={!isEditing}
            />

            <label>Learning Level</label>
            <select
              value={profile.level || "beginner"}
              onChange={(e) => setProfile({ ...profile, level: e.target.value })}
              disabled={!isEditing}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>

            <div className="profile-actions">
              {isEditing ? (
                <>
                  <button onClick={handleUpdate} className="primary-btn">Save</button>
                  <button onClick={() => setIsEditing(false)} className="secondary-btn">Cancel</button>
                </>
              ) : (
                <button onClick={() => setIsEditing(true)} className="primary-btn">Edit Profile</button>
              )}
            </div>
          </div>
        </div>
      )}

      {progress && (
        <div className="progress-section">
          <h2>📈 Learning Progress</h2>
          <div className="progress-grid">
            <div className="progress-card">
              <h3>Courses Completed</h3>
              <p className="stat-value">{progress.coursesCompleted || 0}</p>
            </div>
            <div className="progress-card">
              <h3>Topics Learned</h3>
              <p className="stat-value">{progress.topicsLearned || 0}</p>
            </div>
            <div className="progress-card">
              <h3>Quizzes Attempted</h3>
              <p className="stat-value">{progress.quizzesAttempted || 0}</p>
            </div>
            <div className="progress-card">
              <h3>Overall Accuracy</h3>
              <p className="stat-value">{progress.accuracy || 0}%</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LearnerProfile;
