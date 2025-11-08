# app/agents/base_agent.py
import logging
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# Optional import: Gemini SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all agents — supports both Ollama (local) and Gemini (cloud).
    Automatically switches backend based on model name.
    """

    def __init__(self, model_name: str = "gemini-2.5-pro"):
        self.model_name = model_name
        self.is_gemini = model_name.lower().startswith("gemini")
        self.ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

        if self.is_gemini:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("❌ Missing GEMINI_API_KEY in environment variables (.env).")

            if not GEMINI_AVAILABLE:
                raise ImportError(
                    "❌ google-generativeai not installed. Run: pip install google-generativeai"
                )

            genai.configure(api_key=api_key)
            logger.info(f"Initialized BaseAgent with Gemini model: {self.model_name}")
        else:
            logger.info(f"Initialized BaseAgent with Ollama model: {self.model_name} @ {self.ollama_url}")

    # ----------------------------------------------------------------------
    async def call_llm(
        self,
        prompt: str,
        system_message: str = "You are a helpful AI tutor.",
        max_tokens: int = 500,
    ) -> str:
        """
        Generate a response using either Gemini API or Ollama (auto-selected).
        """

        if self.is_gemini:
            return await self._call_gemini(prompt, system_message, max_tokens)
        else:
            return await self._call_ollama(prompt, system_message, max_tokens)

    # ----------------------------------------------------------------------
    async def _call_ollama(self, prompt: str, system_message: str, max_tokens: int) -> str:
        """Call local Ollama LLM API"""
        logger.debug(f"Calling Ollama with prompt length: {len(prompt)}")

        full_prompt = f"{system_message}\n\n{prompt}"
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.3},
        }

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.ollama_url}/api/generate"
                async with session.post(
                    url, json=payload, timeout=aiohttp.ClientTimeout(total=150)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error {response.status}: {error_text}")
                        return f"[LLM Error] Ollama request failed ({response.status})"

                    result = await response.json()
                    reply = result.get("response", "").strip()

                    if not reply:
                        logger.warning("Ollama returned empty response")
                        return "I couldn’t generate a proper response. Please try again."

                    logger.info(f"✅ Ollama generated {len(reply)} chars")
                    return reply

        except asyncio.TimeoutError:
            logger.error("❌ Ollama request timed out")
            return "[LLM Error] Ollama request timed out."
        except Exception as e:
            logger.error(f"❌ Ollama call failed: {e}", exc_info=True)
            return f"[LLM Error] Ollama call failed: {e}"

    # ----------------------------------------------------------------------
    async def _call_gemini(self, prompt: str, system_message: str, max_tokens: int) -> str:
        """Call Google Gemini API (via google-generativeai SDK)."""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._sync_gemini_call, prompt, system_message)
        except Exception as e:
            logger.error(f"❌ Gemini call failed: {e}", exc_info=True)
            return f"[LLM Error] Gemini call failed: {e}"

    # ----------------------------------------------------------------------
    def _sync_gemini_call(self, prompt: str, system_message: str) -> str:
        model = genai.GenerativeModel(self.model_name)
        combined_prompt = f"{system_message}\n\n{prompt}"
        response = model.generate_content(combined_prompt)

        # ✅ Handle both .text and .candidates structures
        reply = ""
        if hasattr(response, "text") and response.text:
            reply = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            for cand in response.candidates:
                if hasattr(cand, "content"):
                    parts = getattr(cand.content, "parts", [])
                    reply = " ".join(str(p) for p in parts if p).strip()
                if reply:
                    break

        if not reply:
            return "Gemini returned an empty response."

        logger.info(f"✅ Gemini generated {len(reply)} chars")
        return reply

