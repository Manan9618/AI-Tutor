# app/agents/chat_agent.py
from .base_agent import BaseAgent
from typing import List, Dict

class ChatAgent(BaseAgent):
    def __init__(self, model_name: str = "mistral"):
        super().__init__(model_name=model_name)

    async def respond(self, user_query: str, conversation_history: List[Dict[str, str]] = None) -> str:
        if conversation_history is None:
            conversation_history = []

        # Build prompt from history + new query
        messages = conversation_history + [{"role": "user", "content": user_query}]
        
        prompt = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in messages]
        )

        system_message = """You are an intelligent AI tutor. Your role is to:
1. Answer questions directly when students ask for specific information or answers
2. Provide step-by-step explanations when students are learning new concepts
3. Guide students through problem-solving when they're working on exercises
4. Be friendly, clear, and concise in your responses

If a student explicitly asks for an answer (like "What is 10+20?" or "Give me the answer"), 
provide it directly. If they're working through a problem and seem to want guidance, 
offer hints and encourage them to try solving it themselves."""

        response =  await self.call_llm(prompt, system_message=system_message)
        return response