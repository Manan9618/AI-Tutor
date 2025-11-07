# app/services/llm_service.py
import os
import json
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from pydantic import BaseModel
from app.utils.logger import get_logger
from app.config import settings
from data.questions.question_utils import save_quiz  # ✅ integrate question saving

logger = get_logger("llm_service")


class LLMResponse(BaseModel):
    """Structured response from the LLM."""
    content: str
    usage: Optional[Dict[str, Any]] = None


class LLMService:
    """
    Handles all LLM-based operations including:
    - Explanations
    - Quiz generation
    - General text generation
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.temperature = temperature or settings.OPENAI_TEMPERATURE
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI tutor.",
        max_tokens: int = 500,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Generate a text response from the LLM."""
        try:
            logger.info("🧠 Generating response from LLM...")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature or self.temperature,
            )

            content = response.choices[0].message.content.strip()
            usage = response.usage.model_dump() if response.usage else {}

            logger.info("✅ LLM response generated successfully.")
            return LLMResponse(content=content, usage=usage)

        except Exception as e:
            logger.error(f"❌ Error generating LLM response: {e}")
            return LLMResponse(content="An error occurred while generating response.")

    async def generate_quiz(self, topic: str, level: str, num: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions in structured JSON format and save them."""
        prompt = f"""
        Generate {num} {level}-level multiple choice quiz questions on "{topic}".
        Return as a JSON array of objects with:
        - id (int)
        - question (str)
        - type ("mcq")
        - choices (list of str)
        - answer (correct choice index, 0-based)
        """
        logger.info(f"📝 Generating quiz for topic: {topic}, level: {level}")
        resp = await self.generate(
            prompt,
            system_prompt="You are a quiz generator.",
            max_tokens=1000
        )

        try:
            questions = json.loads(resp.content)
            if isinstance(questions, list):
                logger.info(f"✅ Generated {len(questions)} quiz questions.")

                # ✅ Automatically save quiz to /data/questions/history/
                save_quiz(topic=topic, level=level, questions=questions)
                logger.info(f"💾 Quiz saved to data/questions/history for topic: {topic}")

                return questions
            else:
                logger.warning("⚠️ LLM did not return a valid quiz format.")
                return []
        except json.JSONDecodeError:
            logger.warning("⚠️ LLM returned invalid JSON format for quiz.")
            return []

    async def explain(self, topic: str, level: str, style: str, base_content: str = "") -> str:
        """Generate an educational explanation using the LLM."""
        prompt = f"""
        Explain the concept "{topic}" at a {level} level in a {style} style.
        Use examples, analogies, and step-by-step reasoning.
        Base content (if any): {base_content}
        """
        logger.info(f"📘 Generating explanation for: {topic}")
        resp = await self.generate(
            prompt,
            system_prompt="You are an expert educator.",
            max_tokens=800
        )
        return resp.content


# ✅ Singleton instance for global use
llm_service = LLMService()
