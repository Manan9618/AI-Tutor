# app/agents/explanation_agent.py
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class ExplanationAgent(BaseAgent):
    """
    Explains educational concepts with examples.
    """

    def __init__(self, content_repo=None, model_name: str = "mistral"):
        logger.info("Initializing ExplanationAgent")
        super().__init__(model_name=model_name)
        self.content_repo = content_repo or {
            "addition": "Addition is combining two or more numbers to get their total.",
            "transformers": "Transformers are a neural network architecture that uses self-attention mechanisms.",
            "neural networks": "Neural networks are computing systems inspired by biological neural networks.",
        }
        logger.info("✅ ExplanationAgent initialized successfully")

    # ✅ Now async — matches async-safe BaseAgent
    async def explain_concept(self, topic: str, level: str = "beginner", style: str = "visual") -> str:
        """
        Generate an explanation for a given topic using the model asynchronously.
        
        Args:
            topic: The concept to explain
            level: Difficulty level (beginner, intermediate, advanced)
            style: Explanation style (visual, technical, storytelling)
            
        Returns:
            str: The generated explanation
        """
        try:
            logger.info(f"🎓 Generating explanation for: '{topic}' (level: {level}, style: {style})")

            # --- Base content or fallback ---
            base_content = self.content_repo.get(
                topic.lower(),
                f"{topic} is an important concept worth understanding.",
            )

            # --- Instruction templates ---
            level_instructions = {
                "beginner": "Explain in simple, easy-to-understand terms with everyday analogies. Avoid technical jargon.",
                "intermediate": "Provide a balanced explanation with moderate technical details and practical examples.",
                "advanced": "Give an in-depth technical explanation with advanced concepts, applications, and nuances.",
            }

            style_instructions = {
                "visual": "Use vivid descriptions and visual metaphors. Make it easy to visualize and imagine.",
                "technical": "Focus on technical accuracy, precision, and formal terminology.",
                "storytelling": "Present the information as an engaging narrative or story.",
            }

            # --- Build dynamic prompt ---
            prompt = f"""Provide a comprehensive explanation of "{topic}" suitable for a {level} learner.

Background: {base_content}

Guidelines:
- {level_instructions.get(level, level_instructions['beginner'])}
- {style_instructions.get(style, style_instructions['visual'])}

Please include:
1. A clear, concise definition
2. Key concepts and how they work
3. 2-3 practical, real-world examples
4. Why this topic is important or useful

Keep the explanation focused, informative, and engaging. Aim for 300-500 words."""

            system_message = (
                "You are an expert educator who explains complex topics clearly and effectively."
            )

            # --- Call LLM asynchronously ---
            logger.info("🚀 Calling LLM for explanation generation...")
            explanation = await self.call_llm(
                prompt, system_message=system_message, max_tokens=600
            )

            # --- Validate response ---
            if not explanation or explanation.startswith("[LLM Error]"):
                logger.error(f"❌ LLM returned error or empty response: {explanation}")
                raise Exception("Failed to generate valid explanation")

            if len(explanation.strip()) < 50:
                logger.warning(f"⚠️ Generated explanation is too short: {len(explanation)} chars")
                raise Exception("Generated explanation is too brief")

            logger.info(f"✅ Successfully generated explanation ({len(explanation)} characters)")
            return explanation

        except Exception as e:
            logger.error(f"💥 Error in explain_concept: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate explanation for '{topic}': {str(e)}")
