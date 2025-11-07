# app/agents/path_generator.py
from .base_agent import BaseAgent


class PathGeneratorAgent(BaseAgent):
    """
    Generates personalized learning paths and next topics.
    """

    def __init__(self, topics_graph: dict | None = None, model_name: str = "mistral"):
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
            t
            for t in self.topics_graph
            if all(p in covered for p in self.topics_graph[t]["prereq"])
        ]

        if not candidates:
            return "Basics"

        prompt = (
            f"User has covered {covered} with performances {profile['performance']}."
            f" Suggest the next suitable topic from {candidates}."
        )
        next_topic = self.call_llm(prompt, system_message="You are a learning path planner.")
        return next_topic if next_topic in candidates else candidates[0]

    async def generate_roadmap(self, user_id: str, memory_agent) -> list[str]:
        prompt = f"Generate an ordered list of topics for the user based on their profile: {memory_agent.get_profile(user_id)}"
        response = await self.call_llm(prompt)
        return [line.strip("- ").strip() for line in response.split("\n") if line.strip()]