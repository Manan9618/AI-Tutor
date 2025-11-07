# # app/agents/base_agent.py
# import os
# import torch
# import logging
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# from transformers import BitsAndBytesConfig
# from huggingface_hub import InferenceClient

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# class BaseAgent:
#     """
#     Base class for all agents — handles LLM communication via Hugging Face.
#     Uses a shared model instance across all agents to avoid loading multiple times.
#     """

#     # Class-level cache for shared model and tokenizer
#     _shared_models = {}

#     def __init__(self, model_name: str = "google/gemma-2b-it"):
#         self.model_name = model_name

#         # Check if this model is already loaded
#         if model_name in BaseAgent._shared_models:
#             logger.info(f"♻️ Reusing already loaded model: {self.model_name}")
#             cached = BaseAgent._shared_models[model_name]
#             self.tokenizer = cached["tokenizer"]
#             self.model = cached["model"]
#             self.pipeline = cached["pipeline"]
#             self.client = cached["client"]
#             self.device = cached["device"]
#             self.hf_token = cached["hf_token"]
#             return

#         logger.info(f"🧠 Loading Hugging Face model: {self.model_name}")

#         # Get the token from environment variable or config
#         self.hf_token = os.getenv("HF_TOKEN")

#         if not self.hf_token:
#             logger.warning("⚠️ HF_TOKEN not found in environment. API calls may fail.")

#         # Automatically detect the best available device
#         if torch.cuda.is_available():
#             self.device = "cuda"
#         elif torch.backends.mps.is_available():
#             self.device = "mps"
#         else:
#             self.device = "cpu"

#         logger.info(f"⚙️ Using device: {self.device.upper()}")

#         try:
#             # Load tokenizer
#             logger.info("Loading tokenizer...")
#             self.tokenizer = AutoTokenizer.from_pretrained(
#                 self.model_name,
#                 token=self.hf_token,
#                 trust_remote_code=True
#             )

#             # Set pad token if not set
#             if self.tokenizer.pad_token is None:
#                 self.tokenizer.pad_token = self.tokenizer.eos_token
#                 logger.info("Set pad_token to eos_token")

#             # Try to load model locally (safe with fallback)
#             logger.info("Loading model...")
#             self.model = self._load_model_safe()

#             # Build pipeline
#             logger.info("Building text generation pipeline...")
#             self.pipeline = pipeline(
#                 "text-generation",
#                 model=self.model,
#                 tokenizer=self.tokenizer,
#                 max_new_tokens=500,
#                 do_sample=True,
#                 temperature=0.7,
#                 pad_token_id=self.tokenizer.eos_token_id,
#                 device=0 if self.device == "cuda" else -1,
#             )

#             self.client = None
#             logger.info("✅ Local model ready.")

#         except RuntimeError as e:
#             if "out of memory" in str(e).lower():
#                 logger.warning("🚨 GPU/MPS memory full — falling back to Hugging Face Inference API.")
#                 self.model = None
#                 self.pipeline = None
#                 self.tokenizer = AutoTokenizer.from_pretrained(
#                     self.model_name,
#                     token=self.hf_token,
#                     trust_remote_code=True
#                 )
#                 self.client = InferenceClient(self.model_name, token=self.hf_token)
#                 logger.info("✅ Inference API client ready.")
#             else:
#                 logger.error(f"❌ RuntimeError loading model: {str(e)}", exc_info=True)
#                 raise e
#         except Exception as e:
#             logger.error(f"❌ Unexpected error loading model: {str(e)}", exc_info=True)
#             raise e

#         # Cache the loaded model for reuse
#         BaseAgent._shared_models[model_name] = {
#             "tokenizer": self.tokenizer,
#             "model": self.model,
#             "pipeline": self.pipeline,
#             "client": self.client,
#             "device": self.device,
#             "hf_token": self.hf_token
#         }
#         logger.info(f"✅ Model {model_name} cached for future use")

#     def _load_model_safe(self):
#         """
#         Attempts to load the model with proper device mapping.
#         Falls back gracefully if device loading fails.
#         """
#         try:
#             # For MPS and CPU, don't use device_map="auto"
#             if self.device in ["mps", "cpu"]:
#                 logger.info(f"📱 Loading model directly to {self.device.upper()}")
#                 model = AutoModelForCausalLM.from_pretrained(
#                     self.model_name,
#                     token=self.hf_token,
#                     trust_remote_code=True,
#                     torch_dtype=torch.float16 if self.device == "mps" else torch.float32,
#                 )
#                 model = model.to(self.device)
#                 logger.info(f"✅ Model loaded to {self.device.upper()}")
#                 return model

#             # For CUDA, use quantization and device_map
#             else:
#                 logger.info("🚀 Loading model with 4-bit quantization for CUDA")
#                 quant_config = BitsAndBytesConfig(
#                     load_in_4bit=True,
#                     bnb_4bit_compute_dtype=torch.float16,
#                     bnb_4bit_quant_type="nf4",
#                     bnb_4bit_use_double_quant=True,
#                 )

#                 model = AutoModelForCausalLM.from_pretrained(
#                     self.model_name,
#                     token=self.hf_token,
#                     trust_remote_code=True,
#                     device_map="auto",
#                     quantization_config=quant_config,
#                 )
#                 logger.info("✅ Model loaded with quantization")
#                 return model

#         except Exception as e:
#             logger.warning(f"⚠️ Device-specific load failed: {e}")
#             logger.info("👉 Falling back to CPU mode.")
#             model = AutoModelForCausalLM.from_pretrained(
#                 self.model_name,
#                 token=self.hf_token,
#                 trust_remote_code=True,
#                 torch_dtype=torch.float32,
#             )
#             model = model.to("cpu")
#             logger.info("✅ Model loaded to CPU")
#             return model

#     # =============================================================
#     # ✅ UPDATED: Async-safe call_llm (prevents blocking FastAPI)
#     # =============================================================

#     async def call_llm(
#         self,
#         prompt: str,
#         system_message: str = "You are a helpful AI tutor.",
#         max_tokens: int = 500,
#     ) -> str:
#         """
#         Generate a response from the model (local or cloud).
#         Async-safe: runs blocking model generation in a background thread.
#         """
#         logger.debug(f"Calling LLM with prompt length: {len(prompt)}")

#         # Format prompt for Gemma model
#         full_prompt = (
#             f"<start_of_turn>user\n{system_message}\n{prompt}<end_of_turn>\n"
#             f"<start_of_turn>model\n"
#         )

#         try:
#             loop = asyncio.get_event_loop()

#             # ================
#             # Remote (HF API)
#             # ================
#             if self.client:
#                 logger.info("🌐 Using Hugging Face Inference API")
#                 response = await loop.run_in_executor(
#                     None,
#                     lambda: self.client.text_generation(
#                         full_prompt,
#                         max_new_tokens=max_tokens,
#                         temperature=0.7,
#                     ),
#                 )
#                 result = response.strip()
#                 logger.info(f"Generated response length: {len(result)}")
#                 return result

#             # ================
#             # Local Generation
#             # ================
#             logger.info("🧠 Using local model generation (threaded)")
#             outputs = await loop.run_in_executor(
#                 None,
#                 lambda: self.pipeline(
#                     full_prompt,
#                     max_new_tokens=max_tokens,
#                     num_return_sequences=1,
#                     pad_token_id=self.tokenizer.eos_token_id,
#                 ),
#             )

#             generated = outputs[0]["generated_text"]

#             # Extract only the model's response
#             if "<start_of_turn>model\n" in generated:
#                 reply = generated.split("<start_of_turn>model\n")[-1]
#             else:
#                 reply = generated[len(full_prompt):] if generated.startswith(full_prompt) else generated

#             reply = reply.replace("<end_of_turn>", "").strip()
#             logger.info(f"Generated response length: {len(reply)}")

#             if not reply or len(reply) < 10:
#                 logger.warning("Generated response is too short or empty")
#                 return "I apologize, but I couldn't generate a proper response. Please try again."

#             return reply

#         except Exception as e:
#             logger.error(f"❌ LLM call failed: {str(e)}", exc_info=True)
#             return f"[LLM Error] Failed to generate response: {str(e)}"

# app/agents/base_agent.py
import logging
import asyncio
import aiohttp
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all agents — handles LLM communication via Ollama.
    No model loading—just HTTP calls to localhost:11434.
    """

    def __init__(self, model_name: str = "mistral"):
        self.model_name = model_name
        base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        # ✅ Fix: Remove trailing slashes to prevent //api/generate (which causes 404)
        self.ollama_url = base_url.rstrip("/")
        logger.info(f"Intialized BaseAgent with Ollama model: {self.model_name} @ {self.ollama_url}")

    async def call_llm(
        self,
        prompt: str,
        system_message: str = "You are a helpful AI tutor.",
        max_tokens: int = 500,
    ) -> str:
        """
        Generate a response using Ollama's /api/generate endpoint.
        """
        logger.debug(f"Calling Ollama with prompt length: {len(prompt)}")

        # Combine system + user prompt
        full_prompt = f"{system_message}\n\n{prompt}"

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7,
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.ollama_url}/api/generate"
                logger.debug(f"📡 POST to: {url}")
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=150)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error {response.status}: {error_text}")
                        return f"[LLM Error] Ollama request failed: {response.status}"

                    result = await response.json()
                    reply = result.get("response", "").strip()

                    if not reply:
                        logger.warning("Ollama returned empty response")
                        return "I apologize, but I couldn't generate a proper response. Please try again."

                    logger.info(f"✅ Generated response length: {len(reply)}")
                    return reply

        except asyncio.TimeoutError:
            logger.error("❌ Ollama request timed out")
            return "[LLM Error] Request to Ollama timed out."
        except Exception as e:
            logger.error(f"❌ Ollama call failed: {str(e)}", exc_info=True)
            return f"[LLM Error] Failed to generate response: {str(e)}"