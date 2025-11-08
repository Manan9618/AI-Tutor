# app/agents/reflection_agent.py
from .base_agent import BaseAgent
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ReflectionAgent(BaseAgent):
    """
    Reviews session logs and suggests improvements.
    Works with both Gemini and Ollama backends.
    """

    def __init__(self, model_name: str = "gemini-2.5-pro"):
        super().__init__(model_name=model_name)

    async def analyze_session(self, session_log: List[Dict]) -> str:
        prompt = f"""
You are a reflective educational AI analyzing this tutoring session:
{session_log}

Provide structured insights:
### Strengths
- ...

### Weaknesses
- ...

### Improvement Plan
- Suggest what to revisit or adjust for next session.
"""

        reflection = await self.call_llm(prompt, system_message="You are an educational mentor.")
        if not reflection or "###" not in reflection:
            reflection = (
                "### Strengths\n- Not enough data.\n\n"
                "### Weaknesses\n- N/A\n\n"
                "### Improvement Plan\n- Collect more data next session."
            )
        return reflection

    async def suggest_improvements(self, performance_summary: Dict) -> str:
        prompt = f"""
Based on performance data:
{performance_summary}

Summarize key improvement actions:
### Adjustments
- ...
"""
        response = await self.call_llm(prompt, system_message="You are a reflective AI tutor.")
        return response or "No suggestions available."
