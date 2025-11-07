# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select

# from app.agents.explanation_agent import ExplanationAgent
# from app.api.auth import get_current_user
# from app.models.content import Explanation, Topic
# from app.database.session import get_db

# router = APIRouter(tags=["explanation"])  # ✅ No prefix here (prefix handled in main.py)

# # ✅ Single shared agent instance
# explanation_agent = ExplanationAgent()


# # ====================== REQUEST MODEL ======================
# class ExplanationRequest(BaseModel):
#     topic: str
#     level: str = "beginner"
#     style: str = "visual"


# # ====================== CREATE/GET EXPLANATION ======================
# @router.post("/")
# async def get_explanation(
#     request: ExplanationRequest,
#     current_user: str = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     """Generate and store a detailed explanation for a given topic."""
#     try:
#         # 🔍 Check if topic exists
#         result = await db.execute(select(Topic).where(Topic.name == request.topic))
#         topic = result.scalar_one_or_none()

#         # 🆕 Create topic if not exists
#         if not topic:
#             topic = Topic(name=request.topic)
#             db.add(topic)
#             await db.commit()
#             await db.refresh(topic)

#         # 💡 Generate explanation via agent
#         explanation_text = explanation_agent.explain_concept(request.topic, request.level, request.style
# )

#         # 💾 Store explanation in DB
#         new_explanation = Explanation(
#             topic_id=topic.id,
#             level=request.level,
#             style=request.style,
#             content=explanation_text,
#             examples=[],
#         )
#         db.add(new_explanation)
#         await db.commit()
#         await db.refresh(new_explanation)

#         return {
#             "topic": topic.name,
#             "level": new_explanation.level,
#             "style": new_explanation.style,
#             "explanation": new_explanation.content,
#             "id": new_explanation.id,
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")


# # ====================== GET EXPLANATION HISTORY ======================
# @router.get("/history")
# async def get_explanation_history(
#     current_user: str = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     """Return all generated explanations."""
#     try:
#         result = await db.execute(select(Explanation).order_by(Explanation.id.desc()))
#         explanations = result.scalars().all()

#         if not explanations:
#             return []  # ✅ Return empty list instead of raising 404 (frontend friendly)

#         # ✅ Collect topic names efficiently
#         topic_ids = {e.topic_id for e in explanations}
#         topic_results = await db.execute(select(Topic).where(Topic.id.in_(topic_ids)))
#         topic_map = {t.id: t.name for t in topic_results.scalars().all()}

#         return [
#             {
#                 "id": e.id,
#                 "topic": topic_map.get(e.topic_id),
#                 "level": e.level,
#                 "style": e.style,
#                 "content": e.content,
#             }
#             for e in explanations
#         ]

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to load explanation history: {str(e)}")

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
    """Generate and store a detailed explanation for a given topic."""
    logger.info(f"📘 Explanation request for topic: {request.topic}, level: {request.level}, user: {current_user}")
    
    try:
        # 🔍 Check if topic exists
        result = await db.execute(select(Topic).where(Topic.name == request.topic))
        topic = result.scalar_one_or_none()

        # 🆕 Create topic if not exists
        if not topic:
            logger.info(f"🆕 Creating new topic: {request.topic}")
            topic = Topic(name=request.topic)
            db.add(topic)
            await db.commit()
            await db.refresh(topic)

        # 💡 Generate explanation via agent
        logger.info(f"🤖 Generating explanation for: {request.topic}")
        try:
            explanation_text = await explanation_agent.explain_concept(
                topic=request.topic, 
                level=request.level, 
                style=request.style
            )
            logger.info(f"✅ Successfully generated explanation (length: {len(explanation_text)})")
        except Exception as agent_error:
            logger.error(f"❌ Agent failed to generate explanation: {str(agent_error)}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate explanation: {str(agent_error)}"
            )

        # 💾 Store explanation in DB
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
            "topic": topic.name,
            "level": new_explanation.level,
            "style": new_explanation.style,
            "explanation": new_explanation.content,
            "id": new_explanation.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 Unexpected error in get_explanation: {str(e)}", exc_info=True)
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
    """Return all generated explanations."""
    try:
        result = await db.execute(
            select(Explanation).order_by(Explanation.id.desc()).limit(50)
        )
        explanations = result.scalars().all()

        if not explanations:
            logger.info("ℹ️ No explanations found in database.")
            return []

        # ✅ Collect topic names efficiently and handle empty sets
        topic_ids = {e.topic_id for e in explanations if e.topic_id is not None}

        topic_map = {}
        if topic_ids:
            topic_results = await db.execute(select(Topic).where(Topic.id.in_(topic_ids)))
            topic_map = {t.id: t.name for t in topic_results.scalars().all()}

        logger.info(f"📜 Returning {len(explanations)} explanations from history")

        return [
            {
                "id": e.id,
                "topic": topic_map.get(e.topic_id, "Unknown"),
                "level": e.level,
                "style": e.style,
                "content": e.content,
            }
            for e in explanations
        ]

    except Exception as e:
        logger.error(f"❌ Failed to load explanation history: {str(e)}", exc_info=True)
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
    """Clear all explanation history."""
    try:
        logger.warning("⚠️ Clearing all explanation history...")
        await db.execute(delete(Explanation))
        await db.commit()
        logger.info("✅ Explanation history cleared successfully.")
        return {"message": "Explanation history cleared"}
    except Exception as e:
        logger.error(f"❌ Failed to clear history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")
