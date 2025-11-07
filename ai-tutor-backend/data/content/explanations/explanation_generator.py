"""
Uses the AI agent (OpenAI) to generate topic explanations.
"""
from app.services.openai_service import OpenAIService
from app.config import settings

async def generate_explanation(topic: str, level: str = "beginner") -> str:
    """Generate an explanation for a given topic."""
    prompt = (
        f"Explain the topic '{topic}' in simple and clear language "
        f"suitable for a {level}-level learner. Include key examples."
    )
    
    openai_service = OpenAIService(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL
    )
    response = await openai_service.generate_text(prompt)
    return response
