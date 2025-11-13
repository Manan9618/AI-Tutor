# app/agents/path_generator.py
from .base_agent import BaseAgent
import logging
import re

logger = logging.getLogger(__name__)

class PathGeneratorAgent(BaseAgent):
    """
    Generates personalized learning paths and next topics.
    Auto-switches between Ollama and Gemini.
    """

    def __init__(self, topics_graph: dict | None = None, model_name: str = "gemini-2.0-flash"):
        super().__init__(model_name=model_name)
        self.topics_graph = topics_graph or {
            "addition": {"prereq": [], "difficulty": 1},
            "subtraction": {"prereq": ["addition"], "difficulty": 2},
            "multiplication": {"prereq": ["addition", "subtraction"], "difficulty": 3},
        }

    async def generate_next_topic(self, user_id: str, memory_agent) -> str:
        profile = memory_agent.get_profile(user_id)
        covered = list(profile["performance"].keys())
        candidates = [
            t for t in self.topics_graph
            if all(p in covered for p in self.topics_graph[t]["prereq"])
        ]

        if not candidates:
            return "Basics"

        prompt = (
            f"User has covered {covered} with performances {profile['performance']}."
            f" Suggest the next suitable topic from {candidates}."
        )

        next_topic = await self.call_llm(prompt, system_message="You are a learning path planner.")
        return next_topic.strip() if next_topic and next_topic.strip() in candidates else candidates[0]

    async def generate_roadmap(self, user_id: str, memory_agent) -> list[str]:
        profile = memory_agent.get_profile(user_id)
    
        prompt = f"""
        You are a professional curriculum designer.
        Generate a clean, ordered learning roadmap for the user below.
    
        RULES:
            - Return ONLY 5 to 7 topic names.
            - One topic per line.
            - NO explanations, introductions, or comments.
            - NO numbers, bullets, markdown (**, ###, -), or symbols.
            - Just the raw topic name (e.g., "Neural Networks", not "1. Neural Networks").

            User profile: {profile}
        """
    
        response = await self.call_llm(prompt,system_message="You are a curriculum designer. Return ONLY topic names, one per line. No other text.")

        # Split into lines and clean aggressively
        lines = [line.strip() for line in response.split("\n") if line.strip()]
    
        # Remove any remaining numbering, bullets, or markdown
        cleaned = []
        for line in lines:
            # Remove leading numbers, bullets, dashes, hashes
            clean_line = re.sub(r'^[\s\d\.\)\-\*#]+', '', line)
            # Remove bold/italic markers
            clean_line = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', clean_line)
            clean_line = clean_line.strip()
            if clean_line and len(clean_line) > 2:  # skip very short or empty
                cleaned.append(clean_line)
    
        # Safety fallback
        if not cleaned:
            return ["Introduction to AI", "Neural Networks", "Machine Learning Basics"]
        
        return cleaned[:7]  # enforce max 7 topics

