# app/agents/chat_agent.py
from .base_agent import BaseAgent
from typing import List, Dict
import re
import os
import logging

# Disable Chroma telemetry
os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """
    Smart, RAG-augmented conversational tutor for engineering students.
    Supports both Ollama and Gemini backends.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-pro",
        knowledge_base_path: str = "knowledge/",
        embedding_model: str = "nomic-embed-text",
    ):
        super().__init__(model_name=model_name)

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
            ).as_retriever(search_kwargs={"k": 3})

        except Exception as e:
            logger.warning(f"[ChatAgent] ⚠️ RAG retriever unavailable — {e}")
            self.retriever = None

    # ------------------------------------------------------
    def detect_engineering_context(self, query: str) -> Dict[str, str]:
        """Lightweight domain detector."""
        q = query.lower()
        q_clean = re.sub(r"[^a-z0-9\s]", " ", q)
        words = set(q_clean.split())

        if any(w in words for w in ["circuit", "voltage", "resistor", "capacitor", "inductor"]):
            return {"domain": "Electrical Engineering", "subject": "Electric Circuits"}
        if any(w in words for w in ["algorithm", "data", "python", "code", "recursion", "sorting"]):
            return {"domain": "Computer Engineering", "subject": "Programming & DSA"}
        if any(w in words for w in ["thermo", "heat", "entropy", "cycle", "efficiency"]):
            return {"domain": "Mechanical Engineering", "subject": "Thermodynamics"}
        if any(w in words for w in ["stress", "strain", "beam", "deflection", "moment"]):
            return {"domain": "Civil/Mechanical", "subject": "Mechanics of Materials"}
        return {"domain": "General Engineering", "subject": "STEM Concepts"}

    # ------------------------------------------------------
    async def retrieve_context(self, query: str) -> str:
        if not self.retriever:
            return ""
        try:
            docs = await self.retriever.ainvoke(query)
            return "\n\n".join([d.page_content for d in docs])
        except Exception as e:
            logger.error(f"[ChatAgent] Retrieval error: {e}")
            return ""

    # ------------------------------------------------------
    async def respond(self, user_query: str, conversation_history: List[Dict[str, str]] = None) -> str:
        conversation_history = conversation_history or []
        context = self.detect_engineering_context(user_query)
        retrieved_context = await self.retrieve_context(user_query)

        system_message = f"""
You are an expert AI tutor for {context['domain']} students. Subject: {context['subject']}.

Respond strictly in this structure:
### Key Points
- ...

- ...

### Example
...

### Takeaway
One-sentence practical insight.

Rules:
- NO long paragraphs — use bullet points.
- Keep examples short (2-3 lines).
- Use real units and real-world context.
- If uncertain, say “I don’t know”.
Context from knowledge base (use only if relevant):
{retrieved_context}
"""

        # Add structure reinforcement for Gemini
        if self.model_name.lower().startswith("gemini"):
            system_message = (
                "Respond in structured Markdown with ### headings. " + system_message
            )

        messages = conversation_history + [{"role": "user", "content": user_query}]
        prompt = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in messages)

        response = await self.call_llm(prompt, system_message=system_message, max_tokens=400)

        # Fallback structure enforcement
        if "###" not in response and len(response.split()) > 50:
            response = (
                "### Key Points\n- Response too verbose.\n\n"
                "### Example\nN/A\n\n"
                "### Takeaway\nKeep answers concise and structured."
            )

        return response
