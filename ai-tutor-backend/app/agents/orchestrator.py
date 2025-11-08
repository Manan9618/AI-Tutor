# app/agents/orchestrator.py
from .base_agent import BaseAgent
from .memory_agent import MemoryAgent
from .path_generator import PathGeneratorAgent
from .explanation_agent import ExplanationAgent
from .quiz_agent import QuizAgent
from .analytics_agent import AnalyticsAgent
from .chat_agent import ChatAgent


class OrchestratorAgent(BaseAgent):
    """
    Manages session flow across multiple agents.
    """

    def __init__(self, agents_dict: dict, model_name: str = "gemini-2.5-pro"):
        super().__init__(model_name=model_name)
        self.agents = agents_dict
        self.session_state = {}

    def start_session(self, user_id: str):
        profile = self.agents["memory"].get_profile(user_id)
        self.session_state["user_id"] = user_id
        self.session_state["profile"] = profile

        next_topic = self.agents["path_generator"].generate_next_topic(
            user_id, self.agents["memory"]
        )
        explanation = self.agents["explanation"].explain_concept(
            next_topic, profile["level"]
        )
        print(f"\n📘 Explanation for {next_topic}:\n{explanation}\n")

        quiz = self.agents["quiz"].generate_quiz(next_topic, profile["level"])
        user_answers = self.simulate_user_answers(quiz)
        score, feedback = self.agents["quiz"].score_quiz(quiz, user_answers)

        self.agents["memory"].update_performance(user_id, next_topic, score)
        recommendations = self.agents["analytics"].generate_recommendations(
            user_id, self.agents["memory"]
        )

        print(f"✅ Score: {score:.2f}")
        print(f"💬 Feedback:\n{feedback}\n")
        print(f"🎯 Recommendations:\n{recommendations}\n")

    def handle_chat(self, user_query: str) -> str:
        return self.agents["chat"].respond(user_query, self.session_state)

    def simulate_user_answers(self, quiz: list[dict]) -> dict:
        return {q["id"]: q["answer"] for q in quiz}  # assume all correct for testing