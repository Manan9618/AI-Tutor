# app/agents/planner_agent.py
import json
from typing import List, Dict
from .base_agent import BaseAgent
import logging
import os

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """
    Adaptive, RAG-powered learning planner.
    Works with both Gemini and Ollama embeddings.
    """

    def __init__(self, model_name: str = "gemini-2.5-pro", knowledge_base_path: str = "knowledge/"):
        super().__init__(model_name=model_name)
        self.knowledge_base_path = knowledge_base_path

        # Conditional Embeddings
        try:
            if model_name.lower().startswith("gemini"):
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=os.getenv("GEMINI_API_KEY"),
                )
            else:
                from langchain_ollama import OllamaEmbeddings
                embeddings = OllamaEmbeddings(
                    model="nomic-embed-text",
                    base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                )

            from langchain_chroma import Chroma
            self.retriever = Chroma(
                persist_directory=knowledge_base_path,
                embedding_function=embeddings,
            )
        except Exception as e:
            logger.warning(f"[PlannerAgent] Knowledge base not available — {e}")
            self.retriever = None

    def retrieve_related_knowledge(self, goal: str, k: int = 5) -> str:
        if not self.retriever:
            return "Knowledge base unavailable."
        try:
            results = self.retriever.similarity_search(goal, k=k)
            if not results:
                return "No relevant context found."
            return "\n\n".join([r.page_content for r in results])
        except Exception as e:
            logger.error(f"[PlannerAgent] Retrieval error: {e}")
            return "Retrieval failed."

    async def create_learning_plan(self, goal: str, profile: dict) -> List[Dict]:
        retrieved_context = self.retrieve_related_knowledge(goal)

        system_prompt = f"""
You are an educational planner AI.
Goal: {goal}
Profile: {profile}

Context:
{retrieved_context}

Create a JSON plan with 3–5 steps.
Each step has: step, agent, topic, objective.
"""

        raw_response = await self.call_llm(system_prompt, system_message="You are a structured planner.")
        try:
            plan = json.loads(raw_response)
            if not isinstance(plan, list):
                raise ValueError("Invalid format")
        except Exception as e:
            logger.warning(f"[PlannerAgent] JSON parsing failed: {e}. Using fallback.")
            plan = [
                {"step": 1, "agent": "explanation", "topic": goal, "objective": "Introduce fundamentals"},
                {"step": 2, "agent": "quiz", "topic": goal, "objective": "Assess understanding"},
                {"step": 3, "agent": "analytics", "topic": goal, "objective": "Analyze performance"},
            ]

        for i, s in enumerate(plan, 1):
            s["step"] = i

        return plan
