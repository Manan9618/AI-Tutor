# # app/agents/path_generator.py
# from .base_agent import BaseAgent
# import logging
# import re

# logger = logging.getLogger(__name__)

# class PathGeneratorAgent(BaseAgent):
#     """
#     Generates personalized learning paths and next topics.
#     Auto-switches between Ollama and Gemini.
#     """

#     def __init__(self, topics_graph: dict | None = None, model_name: str = "gemini-2.0-flash"):
#         super().__init__(model_name=model_name)
#         self.topics_graph = topics_graph or {
#             "addition": {"prereq": [], "difficulty": 1},
#             "subtraction": {"prereq": ["addition"], "difficulty": 2},
#             "multiplication": {"prereq": ["addition", "subtraction"], "difficulty": 3},
#         }

#     async def generate_next_topic(self, user_id: str, memory_agent) -> str:
#         profile = memory_agent.get_profile(user_id)
#         covered = list(profile["performance"].keys())
#         candidates = [
#             t for t in self.topics_graph
#             if all(p in covered for p in self.topics_graph[t]["prereq"])
#         ]

#         if not candidates:
#             return "Basics"

#         prompt = (
#             f"User has covered {covered} with performances {profile['performance']}."
#             f" Suggest the next suitable topic from {candidates}."
#         )

#         next_topic = await self.call_llm(prompt, system_message="You are a learning path planner.")
#         return next_topic.strip() if next_topic and next_topic.strip() in candidates else candidates[0]

#     async def generate_roadmap(self, user_id: str, memory_agent) -> list[str]:
#         profile = memory_agent.get_profile(user_id)
    
#         prompt = f"""
#         You are a professional curriculum designer.
#         Generate a clean, ordered learning roadmap for the user below.
    
#         RULES:
#             - Return ONLY 5 to 7 topic names.
#             - One topic per line.
#             - NO explanations, introductions, or comments.
#             - NO numbers, bullets, markdown (**, ###, -), or symbols.
#             - Just the raw topic name (e.g., "Neural Networks", not "1. Neural Networks").

#             User profile: {profile}
#         """
    
#         response = await self.call_llm(prompt,system_message="You are a curriculum designer. Return ONLY topic names, one per line. No other text.")

#         # Split into lines and clean aggressively
#         lines = [line.strip() for line in response.split("\n") if line.strip()]
    
#         # Remove any remaining numbering, bullets, or markdown
#         cleaned = []
#         for line in lines:
#             # Remove leading numbers, bullets, dashes, hashes
#             clean_line = re.sub(r'^[\s\d\.\)\-\*#]+', '', line)
#             # Remove bold/italic markers
#             clean_line = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', clean_line)
#             clean_line = clean_line.strip()
#             if clean_line and len(clean_line) > 2:  # skip very short or empty
#                 cleaned.append(clean_line)
    
#         # Safety fallback
#         if not cleaned:
#             return ["Introduction to AI", "Neural Networks", "Machine Learning Basics"]
        
#         return cleaned[:7]  # enforce max 7 topics



# app/agents/path_generator.py
from .base_agent import BaseAgent
import logging
import re
import json

logger = logging.getLogger(__name__)

class PathGeneratorAgent(BaseAgent):
    """
    Generates a two-tier learning path:
      1. Common Core (for all CS students)
      2. Specialized Track (based on user's chosen focus)
    Auto-switches between Ollama and Gemini.
    """

    COMMON_CORE = [
        "Programming Fundamentals (Variables, Loops, Functions)",
        "Data Structures (Arrays, Linked Lists, Stacks, Queues)",
        "Algorithms (Sorting, Searching, Time Complexity)",
        "Object-Oriented Programming (OOP)",
        "Computer Architecture & OS Basics",
        "Databases & SQL",
        "Networking Fundamentals",
        "Software Engineering Principles",
        "Version Control with Git",
        "Math for CS (Discrete Math, Linear Algebra)"
    ]

    def __init__(self, topics_graph: dict | None = None, model_name: str = "gemini-2.0-flash"):
        super().__init__(model_name=model_name)
        self.topics_graph = topics_graph or {}

    async def generate_next_topic(self, user_id: str, memory_agent) -> str:
        profile = memory_agent.get_profile(user_id)
        covered = list(profile.get("performance", {}).keys())
        candidates = [
            t for t in self.COMMON_CORE
            if t not in covered
        ]
        if not candidates:
            return "Review Core Concepts"
        return candidates[0]

    async def generate_roadmap(self, user_id: str, memory_agent) -> list[dict]:
        profile = memory_agent.get_profile(user_id)
        specialization = profile.get("specialization", "").strip()

        roadmap = [
            {
                "name": "📚 Core Computer Engineering",
                "topics": self.COMMON_CORE
            }
        ]

        if not specialization:
            roadmap.append({
                "name": "🎯 Choose Your Specialization",
                "topics": ["Pick a track to unlock personalized advanced content!"]
            })
            return roadmap

        # Generate specialized track
        prompt = f"""
You are a senior Computer Engineering curriculum designer.
Generate a focused, practical learning path for a student specializing in **{specialization}**.

RULES:
- Return ONLY 4 to 6 topic names.
- One topic per line.
- NO explanations, intros, numbers, bullets, or markdown.
- Prioritize industry-relevant, hands-on topics (e.g., 'RAG with LLMs', 'Docker & Kubernetes').

User background: {profile.get('background', 'Undergraduate CS student')}
        """.strip()

        response = await self.call_llm(
            prompt,
            system_message="You are an expert in Computer Engineering education. Return ONLY topic names, one per line. No other text."
        )

        specialized_topics = self._clean_topic_list(response)

        if not specialized_topics:
            # Fallback for safety
            specialized_topics = [
                f"Introduction to {specialization}",
                f"Core Concepts in {specialization}",
                f"Hands-on Projects in {specialization}"
            ]

        roadmap.append({
            "name": f"🚀 {specialization}",
            "topics": specialized_topics
        })

        return roadmap

    def _clean_topic_list(self, text: str) -> list[str]:
        lines = [line.strip() for line in (text or "").split("\n") if line.strip()]
        cleaned = []
        for line in lines:
            # Remove leading numbers, bullets, dashes, hashes
            clean_line = re.sub(r'^[\s\d\.\)\-\*#]+', '', line)
            # Remove bold/italic markers (**text** or *text*)
            clean_line = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', clean_line)
            clean_line = clean_line.strip()
            if clean_line and len(clean_line) > 3:
                cleaned.append(clean_line)
        return cleaned[:6]