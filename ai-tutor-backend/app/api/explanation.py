# app/api/explanation.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
import logging

from app.agents.explanation_agent import ExplanationAgent
from app.api.auth import get_current_user
from app.models.content import Explanation, Topic
from app.database.session import get_db

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["explanation"])

# ✅ Single shared agent instance
explanation_agent = ExplanationAgent()


# ====================== REQUEST MODEL ======================
class ExplanationRequest(BaseModel):
    topic: str
    level: str = "beginner"
    style: str = "visual"


# ====================== CREATE/GET EXPLANATION ======================
@router.post("/")
async def get_explanation(
    request: ExplanationRequest,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate and store a detailed explanation for a given topic.
    Idempotent: safe to call multiple times with the same topic.
    """
    # 🔤 Normalize topic: strip leading/trailing whitespace
    raw_topic = request.topic
    normalized_topic = raw_topic.strip()
    
    if not normalized_topic:
        raise HTTPException(
            status_code=400,
            detail="Topic name cannot be empty or whitespace-only"
        )

    logger.info(f"📘 Explanation request for topic: '{normalized_topic}', level: {request.level}, user: {current_user}")
    
    try:
        # 🔁 Retry loop to handle race conditions (max 2 attempts)
        topic = None
        for attempt in range(2):
            # 🔍 Look up existing topic
            result = await db.execute(select(Topic).where(Topic.name == normalized_topic))
            topic = result.scalar_one_or_none()

            if topic:
                logger.debug(f"✅ Topic found in attempt {attempt + 1}: ID={topic.id}")
                break

            # ➕ Try to create new topic
            logger.info(f"🆕 Attempt {attempt + 1}: Creating new topic '{normalized_topic}'")
            new_topic = Topic(name=normalized_topic)
            db.add(new_topic)
            try:
                await db.commit()
                await db.refresh(new_topic)
                topic = new_topic
                logger.info(f"✅ Topic created successfully with ID: {topic.id}")
                break
            except Exception as commit_err:
                await db.rollback()
                logger.warning(f"⚠️ Commit failed on attempt {attempt + 1}: {str(commit_err)}")
                if attempt == 0 and "UNIQUE constraint failed" in str(commit_err):
                    # Likely a race condition — retry lookup
                    continue
                else:
                    # Unrecoverable error
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to create topic: {str(commit_err)}"
                    )

        if not topic:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve or create topic after retries"
            )

        # 💡 Generate explanation via agent
        logger.info(f"🤖 Generating explanation for: '{normalized_topic}'")
        try:
            explanation_text = await explanation_agent.explain_concept(
                topic=normalized_topic,
                level=request.level,
                style=request.style
            )
            if not explanation_text or not explanation_text.strip():
                raise ValueError("Explanation agent returned empty or whitespace-only content")
            logger.info(f"✅ Explanation generated (length: {len(explanation_text)})")
        except Exception as agent_error:
            logger.error(f"❌ Agent failed: {str(agent_error)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate explanation: {str(agent_error)}"
            )

        # 💾 Save explanation
        new_explanation = Explanation(
            topic_id=topic.id,
            level=request.level,
            style=request.style,
            content=explanation_text,
            examples=[],
        )
        db.add(new_explanation)
        await db.commit()
        await db.refresh(new_explanation)
        logger.info(f"💾 Explanation saved with ID: {new_explanation.id}")

        return {
            "id": new_explanation.id,
            "topic": topic.name,
            "level": new_explanation.level,
            "style": new_explanation.style,
            "explanation": new_explanation.content,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 Unexpected error: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Explanation generation failed: {str(e)}"
        )


# ====================== GET EXPLANATION HISTORY ======================
@router.get("/history")
async def get_explanation_history(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all generated explanations for the current user."""
    try:
        result = await db.execute(
            select(Explanation)
            .order_by(Explanation.created_at.desc() if hasattr(Explanation, 'created_at') else Explanation.id.desc())
            .limit(50)
        )
        explanations = result.scalars().all()

        if not explanations:
            logger.info("ℹ️ No explanation history found.")
            return []

        # 🔗 Resolve topic names
        topic_ids = {e.topic_id for e in explanations if e.topic_id is not None}
        topic_map = {}
        if topic_ids:
            topic_result = await db.execute(select(Topic).where(Topic.id.in_(topic_ids)))
            topic_map = {t.id: t.name for t in topic_result.scalars().all()}

        logger.info(f"📜 Returning {len(explanations)} explanations")

        return [
            {
                "id": e.id,
                "topic": topic_map.get(e.topic_id, "Unknown Topic"),
                "level": e.level,
                "style": e.style,
                "content": e.content,
            }
            for e in explanations
        ]

    except Exception as e:
        logger.error(f"❌ Failed to load history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load explanation history: {str(e)}"
        )


# ====================== CLEAR HISTORY ======================
@router.delete("/clear")
async def clear_explanation_history(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear all explanation history for the current user."""
    try:
        logger.warning("⚠️ Clearing all explanation history...")
        await db.execute(delete(Explanation))
        await db.commit()
        logger.info("✅ Explanation history cleared")
        return {"message": "Explanation history cleared successfully"}
    except Exception as e:
        logger.error(f"❌ Clear failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear explanation history: {str(e)}"
        )