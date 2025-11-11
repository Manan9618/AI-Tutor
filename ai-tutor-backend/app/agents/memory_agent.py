# app/agents/memory_agent.py
from .base_agent import BaseAgent

class MemoryAgent(BaseAgent):
    """
    Stores and retrieves user learning profiles and analytics.
    Now compatible with Gemini/Ollama BaseAgent interface.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-lite"):
        super().__init__(model_name=model_name)
        self.memory_store = {}

    # ================= PROFILE =================
    def get_profile(self, user_id: str) -> dict:
        if user_id not in self.memory_store:
            self.memory_store[user_id] = {
                "age": 12,
                "grade": 6,
                "style": "visual",
                "level": "beginner",
                "topics": {},
                "performance": {},
                "learning_path": [],
                "analytics": {
                    "total_chats": 0,
                    "topics_explored": 0,
                    "quizzes_completed": 0,
                    "average_score": 0.0,
                    "knowledge_gaps": [],
                },
            }
        return self.memory_store[user_id]

    def save_profile(self, user_id: str, profile: dict):
        self.memory_store[user_id] = profile

    def update_profile(self, user_id: str, key: str, value):
        profile = self.get_profile(user_id)
        profile[key] = value
        self.save_profile(user_id, profile)

    # ================= PERFORMANCE =================
    def update_performance(self, user_id: str, topic: str, score: float, mistakes=None, time_spent: float = 0):
        profile = self.get_profile(user_id)
        profile["performance"][topic] = {
            "score": score,
            "mistakes": mistakes or [],
            "time": time_spent,
        }
        self.save_profile(user_id, profile)

    # ================= LEARNING PATH =================
    def get_user_learning_path(self, user_id: str):
        return self.get_profile(user_id).get("learning_path", [])

    def save_learning_path(self, user_id: str, topics: list):
        profile = self.get_profile(user_id)
        profile["learning_path"] = topics
        self.save_profile(user_id, profile)

    # ================= ANALYTICS TRACKING =================
    def increment_chat(self, user_id: str):
        profile = self.get_profile(user_id)
        profile["analytics"]["total_chats"] += 1
        self.save_profile(user_id, profile)

    def increment_topic_explored(self, user_id: str, topic: str):
        profile = self.get_profile(user_id)
        profile["analytics"]["topics_explored"] += 1
        profile["topics"][topic] = True
        self.save_profile(user_id, profile)

    def increment_quiz_completed(self, user_id: str):
        profile = self.get_profile(user_id)
        profile["analytics"]["quizzes_completed"] += 1
        self.save_profile(user_id, profile)

    def save_analytics(self, user_id: str, analytics_data: dict):
        profile = self.get_profile(user_id)
        profile["analytics"].update(analytics_data)
        self.save_profile(user_id, profile)
