# app/agents/explanation_agent.py
from .base_agent import BaseAgent
import logging
import re
import os

os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")
logger = logging.getLogger(__name__)


class ExplanationAgent(BaseAgent):
    """
    RAG-enhanced, structured concept explainer with optional animation hints.
    Supports both Ollama and Gemini backends.
    """

    def __init__(
        self,
        content_repo=None,
        model_name: str = "gemini-2.0-flash-lite",
        knowledge_base_path: str = "knowledge/",
        embedding_model: str = "nomic-embed-text",
    ):
        super().__init__(model_name=model_name)
        self.content_repo = content_repo or {}

        # ---------- Conditional Embedding Backend ----------
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
                    model=embedding_model,
                    base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                )

            from langchain_chroma import Chroma
            self.retriever = Chroma(
                persist_directory=knowledge_base_path,
                embedding_function=embeddings,
            ).as_retriever(search_kwargs={"k": 5})

        except Exception as e:
            logger.warning(f"[ExplanationAgent] ⚠️ Knowledge base unavailable — {e}")
            self.retriever = None

    # ------------------------------------------------------
    async def retrieve_context(self, topic: str) -> str:
        if not self.retriever:
            return ""
        try:
            docs = await self.retriever.ainvoke(topic)
            return "\n\n".join([d.page_content for d in docs])
        except Exception as e:
            logger.error(f"[ExplanationAgent] Retrieval failed: {e}")
            return ""

    # ------------------------------------------------------
    async def explain_concept(
        self,
        topic: str,
        level: str = "beginner",
        style: str = "visual",
        include_animation: bool = True,
    ) -> str:
        logger.info(f"🎓 Explaining '{topic}' for {level} learner.")
        retrieved_context = await self.retrieve_context(topic)

        tone_map = {
            "beginner": "Simple, analogy-based with everyday examples.",
            "intermediate": "Moderate technical depth with key equations.",
            "advanced": "Deep theoretical insight with real applications.",
        }
        style_map = {
            "visual": "Use vivid, spatial descriptions (as if drawing).",
            "technical": "Use precise terms, formulas, and units.",
            "storytelling": "Explain through a short real-world scenario.",
        }

        system_message = f"""
You are a structured AI educator.
Explain '{topic}' for a {level}-level student using {style_map.get(style)} style.
Respond strictly in this format:
### Definition
1–2 sentences.

### Key Points
- ...
- ...

### Example
1–2 sentence real-world case.

### Takeaway
One practical insight.

Rules:
- No paragraph longer than 2 lines.
- Use bullet points.
- Keep total < 300 words.
- Use units where relevant.
Context (only if helpful):
{retrieved_context}
"""

        # Add structure reinforcement for Gemini
        if self.model_name.lower().startswith("gemini"):
            system_message = (
                "Respond in structured Markdown with ### headings. " + system_message
            )

        prompt = f"Explain the concept of '{topic}' clearly and concisely."
        explanation = await self.call_llm(prompt, system_message=system_message, max_tokens=500)

        # Fallback structure enforcement
        if "###" not in explanation:
            explanation = (
                "### Definition\nUnavailable.\n\n"
                "### Key Points\n- Failed to structure content.\n\n"
                "### Example\nN/A\n\n"
                "### Takeaway\nTry rephrasing your question."
            )

        if include_animation:
            animation_hint = self.generate_animation_description(topic)
            explanation += f"\n\n🎬 **Animation Suggestion:** {animation_hint}"

        return explanation

    # ------------------------------------------------------
    def generate_animation_description(self, topic: str) -> str:
        topic_lower = topic.lower()
        if any(w in topic_lower for w in ["circuit", "voltage", "current", "resistor"]):
            return "Animated circuit showing flowing electrons and component labels (Ohm’s Law)."
        elif any(w in topic_lower for w in ["matrix", "vector", "linear", "transformation"]):
            return "Grid deformation animation showing vectors rotating and stretching."
        elif any(w in topic_lower for w in ["heat", "thermo", "entropy", "energy"]):
            return "Molecules vibrating faster as heat flows from hot to cold."
        elif any(w in topic_lower for w in ["algorithm", "sort", "search", "tree"]):
            return "Step-by-step animation of algorithm progression with color cues."
        else:
            return "Labeled diagram with motion arrows to visualize the concept."
