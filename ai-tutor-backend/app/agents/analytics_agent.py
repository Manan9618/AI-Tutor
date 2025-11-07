# app/agents/analytics_agent.py
import asyncio
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AnalyticsAgent(BaseAgent):
    """
    Analyzes student performance and provides actionable insights.
    """

    def __init__(self, model_name: str = "mistral"):
        super().__init__(model_name=model_name)

    # ✅ Make async
    async def generate_recommendations(self, user_id: str, memory_agent) -> str:
        """
        Analyze a user's performance and recommend next steps.
        If the LLM takes too long, return a safe fallback.
        """
        profile = memory_agent.get_profile(user_id)
        prompt = (
            f"Analyze this student's performance: {profile['performance']} "
            f"and analytics: {profile['analytics']}. "
            f"Identify weak areas and recommend next learning actions."
        )

        try:
            # Timeout after 10 seconds max
            response = await asyncio.wait_for(
                self.call_llm(prompt, system_message="You are an educational analytics expert.", max_tokens=200),
                timeout=10
            )

            # Clean up response
            if not response or response.startswith("[LLM Error]"):
                raise ValueError("Invalid LLM response")

            return response.strip()

        except asyncio.TimeoutError:
            logger.warning("⏳ LLM took too long for recommendations — using fallback.")
            return "The student is progressing steadily. Recommend reinforcing weak areas through short practice sessions."

        except Exception as e:
            logger.error(f"⚠️ Failed to generate recommendations: {e}")
            return "Unable to generate detailed recommendations right now. Please try again later."

    # ✅ Keep this sync (fast) — no LLM here
    def generate_dashboard_metrics(self, user_id: str, memory_agent) -> dict:
        """
        Quickly compute static performance metrics for dashboard display.
        (No heavy LLM call — runs instantly.)
        """
        profile = memory_agent.get_profile(user_id)
        perf = profile.get("performance", {})
        analytics = profile.get("analytics", {})

        # Compute average score and knowledge gaps
        if perf:
            avg_score = sum(d.get("score", 0) for d in perf.values()) / len(perf)
            gaps = [t for t, d in perf.items() if d.get("score", 0) < 0.6]
        else:
            avg_score = 0
            gaps = []

        # Update cached analytics
        analytics.update({
            "average_score": round(avg_score, 2),
            "knowledge_gaps": gaps,
        })

        memory_agent.save_analytics(user_id, analytics)
        return analytics

    # ✅ Optional helper for async background updates
    async def refresh_analytics_background(self, user_id: str, memory_agent):
        """
        Run LLM-based analytics generation in the background — non-blocking.
        """
        try:
            recs = await self.generate_recommendations(user_id, memory_agent)
            profile = memory_agent.get_profile(user_id)
            analytics = profile.get("analytics", {})
            analytics["latest_recommendations"] = recs
            memory_agent.save_analytics(user_id, analytics)
            logger.info(f"✅ Background analytics updated for user {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Background analytics refresh failed: {e}")
