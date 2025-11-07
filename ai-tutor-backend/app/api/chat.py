# # app/api/chat.py
# from fastapi import APIRouter, Depends, Body, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select

# from app.api.auth import get_current_user
# from app.api import chat_agent
# from app.database.session import get_db
# from app.models.interaction import InteractionLog

# router = APIRouter()


# class ChatRequest(BaseModel):
#     query: str


# class ChatResponse(BaseModel):
#     response: str


# @router.post("/message", response_model=ChatResponse)
# async def chat_message(
#     request: ChatRequest = Body(...),
#     current_user: str = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Send a chat message from the learner; returns assistant response.
#     Also logs the interaction in the database.
#     """
#     user_id = current_user["id"] if isinstance(current_user, dict) and "id" in current_user else current_user
#     session_state = {"user_id": user_id}

#     # Generate AI response
#     response = chat_agent.respond(request.query, session_state)

#     # Log interaction in DB
#     log_entry = InteractionLog(
#         user_id=user_id,
#         session_id=None,
#         type="chat",
#         topic=None,
#         user_input=request.query,
#         agent_response=response,
#         extra_data={}
#     )

#     db.add(log_entry)
#     await db.commit()
#     await db.refresh(log_entry)

#     return {"response": response}


# @router.get("/history")
# async def get_chat_history(
#     current_user: str = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Retrieve the last 20 chat messages for the current user.
#     """
#     user_id = current_user["id"] if isinstance(current_user, dict) and "id" in current_user else current_user

#     try:
#         result = await db.execute(
#             select(InteractionLog)
#             .where(InteractionLog.user_id == user_id)
#             .where(InteractionLog.type == "chat")
#             .order_by(InteractionLog.timestamp.desc())
#             .limit(20)
#         )
#         chats = result.scalars().all()

#         if not chats:
#             return {"history": []}

#         history = [
#             {
#                 "id": c.id,
#                 "user_input": c.user_input,
#                 "agent_response": c.agent_response,
#                 "timestamp": c.timestamp.isoformat() if c.timestamp else None
#             }
#             for c in chats
#         ]

#         return {"history": history}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to load chat history: {str(e)}")


from fastapi import APIRouter, Depends, Body, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.auth import get_current_user
from app.agents.chat_agent import ChatAgent
from app.database.session import get_db
from app.models.interaction import InteractionLog
from app.models.session import LearningSession  # ✅ Import this
from datetime import datetime

# ✅ Instantiate the agent ONCE
chat_agent = ChatAgent(model_name="mistral")

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    session_id: int | None = None  # uses your integer FK


class ChatResponse(BaseModel):
    response: str
    session_id: int


from datetime import datetime

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest = Body(...),
    current_user: str = Depends(get_current_user),  # 👈 explicitly mark as string
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user  # ✅ directly use string user_id
    session_id = request.session_id

    # Create new session if not provided
    if not session_id:
        new_session = LearningSession(
            user_id=user_id,
            started_at=datetime.utcnow(),
            current_topic=request.query[:80],
            status="active",
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        session_id = new_session.id

    # Fetch previous chat logs
    result = await db.execute(
        select(InteractionLog)
        .where(InteractionLog.session_id == session_id)
        .where(InteractionLog.type == "chat")
        .order_by(InteractionLog.timestamp.asc())
    )
    logs = result.scalars().all()

    conversation_history = []
    for log in logs:
        conversation_history.append({"role": "user", "content": log.user_input})
        conversation_history.append({"role": "assistant", "content": log.agent_response})

    # Handle both async/sync chat_agent
    response = await chat_agent.respond(request.query, conversation_history)


    # Save the interaction
    log_entry = InteractionLog(
        user_id=user_id,
        session_id=session_id,
        type="chat",
        user_input=request.query,
        agent_response=response,
        extra_data={}
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)

    return {"response": response, "session_id": session_id}




@router.get("/sessions")
async def get_chat_sessions(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve chat sessions (LearningSession-based) for this user.
    """
    user_id = current_user["id"] if isinstance(current_user, dict) else current_user

    try:
        # Fetch all sessions for this user (most recent first)
        result = await db.execute(
            select(
                LearningSession.id,
                LearningSession.started_at,
                LearningSession.current_topic,
                LearningSession.status
            )
            .where(LearningSession.user_id == user_id)
            .order_by(LearningSession.started_at.desc())
        )
        sessions = result.all()

        if not sessions:
            return {"sessions": []}

        # Format sessions for frontend
        formatted = []
        for s in sessions:
            formatted.append({
                "session_id": s[0],
                "title": s[2] or f"Chat #{s[0]}",  # Use current_topic or fallback
                "status": s[3],
                "created_at": s[1].isoformat() if s[1] else None
            })

        return {"sessions": formatted}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sessions: {str(e)}")



@router.get("/history")
async def get_chat_history(
    session_id: int = Query(..., description="LearningSession ID"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve chat history for a given LearningSession.
    """
    user_id = current_user["id"] if isinstance(current_user, dict) else current_user

    result = await db.execute(
        select(InteractionLog)
        .where(InteractionLog.user_id == user_id)
        .where(InteractionLog.session_id == session_id)
        .where(InteractionLog.type == "chat")
        .order_by(InteractionLog.timestamp.asc())
    )
    chats = result.scalars().all()

    if not chats:
        return {"history": []}

    history = []
    for c in chats:
        ts = c.timestamp.isoformat() if c.timestamp else None
        history.append({"role": "user", "content": c.user_input, "timestamp": ts})
        history.append({"role": "assistant", "content": c.agent_response, "timestamp": ts})

    return {"history": history}
