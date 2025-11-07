# app/services/content_retrieval.py
from typing import List, Optional
from .vector_store import VectorStoreService
from .llm_service import LLMService


class ContentRetrievalService:
    """Handles retrieval-augmented generation (RAG) for explanations and quizzes."""

    def __init__(self):
        self.vector_store = VectorStoreService()
        self.llm = LLMService()

    async def retrieve(
        self,
        query: str,
        topic: Optional[str] = None,
        level: Optional[str] = None,
        top_k: int = 3,
    ) -> List[dict]:
        """Retrieve semantically similar content from the vector store."""
        filter_dict = {}
        if topic:
            filter_dict["topic"] = topic
        if level:
            filter_dict["level"] = level

        results = await self.vector_store.query(
            query_text=query, top_k=top_k, filter=filter_dict or None
        )
        return results

    async def rag_explain(
        self,
        topic: str,
        user_query: str,
        level: str = "beginner",
        style: str = "visual",
    ) -> str:
        """Retrieve content and generate an AI explanation."""
        retrieved = await self.retrieve(user_query, topic=topic, level=level, top_k=3)
        context = "\n\n".join([r["text"] for r in retrieved if r.get("text")])

        prompt = f"""
        Topic: {topic}
        User Question: {user_query}
        Retrieved Context:
        {context}

        Explain in {style} style at {level} level.
        Include examples and maintain factual accuracy.
        """
        response = await self.llm.generate(
            prompt, system_prompt="You are a knowledgeable tutor."
        )
        return response.content

    async def rag_quiz(self, topic: str, level: str, num: int = 5) -> List[dict]:
        """Generate quiz questions using RAG pipeline."""
        retrieved = await self.retrieve(
            f"quiz questions on {topic}", topic=topic, level=level, top_k=5
        )
        _ = "\n".join([r["text"] for r in retrieved if "question" in r["text"].lower()])
        return await self.llm.generate_quiz(topic, level, num)
