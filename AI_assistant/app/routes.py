import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from langchain_ollama import OllamaLLM
from app.utils.load_intent_object import load_intent_object
from app.schemas.chat_ask import ChatRequest
from app.schemas.state import ChatFlowState
from typing import List
from app.schemas.chat_session import ChatSessionCreate, ChatSessionOut
from app.schemas.message import MessageCreate, MessageOut
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.crud import chat_session, message
from app.db.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.langgraph.nodes import detect_intent_node
from app.langgraph.flows import recommendation_graph

router: APIRouter = APIRouter()
logger = logging.getLogger("ai_assistant")

# Define once globally
llm = OllamaLLM(model="llama3.2")

INTENT_KB_PATH = "data/intents_knowledge_base.json"
intent_detector = detect_intent_node.DetectIntentNode(kb_path=INTENT_KB_PATH, model_name="llama3.2")


@router.post("/ask")
async def ask_chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Received /ask request for session ID: {request.chat_session_id}")
        
        base_state = ChatFlowState(
            user_query=request.user_query,
            session_id=request.chat_session_id,
            db=db
        )

        intent_state = intent_detector.invoke(base_state)
        logger.info(f"Detected intent: {intent_state.intent}, sub_intent: {intent_state.sub_intent}")

        intent_state.intent_object = load_intent_object(intent_state.intent, INTENT_KB_PATH)
        intent_state.user_location = "Pune, India"

        if intent_state.intent == "recommendation":
            logger.debug("Using recommendation graph for intent.")
            graph = recommendation_graph.build_recommendation_graph()
        else:
            logger.warning(f"Unsupported intent detected: {intent_state.intent}")
            return JSONResponse({"error": "Intent is not recommendation"})

        final_state = await graph.ainvoke(intent_state)
        logger.info("Successfully completed graph execution.")
        return JSONResponse(content=final_state["response"])

    except Exception as e:
        logger.exception("Unhandled error occurred in /ask route.")
        raise HTTPException(status_code=500, detail=f"Error in /ask: {str(e)}")


@router.post("/chat_sessions", response_model=ChatSessionOut)
async def create_chat(session_in: ChatSessionCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating new chat session: {session_in}")
    db_session = ChatSession(**session_in.model_dump())
    return await chat_session.create_chat_session(db, db_session)


@router.get("/chat_sessions/{session_id}", response_model=ChatSessionOut)
async def read_chat(session_id: UUID, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Fetching chat session: {session_id}")
    session = await chat_session.get_chat_session(db, session_id)
    if not session:
        logger.warning(f"Chat session {session_id} not found.")
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.get("/chat_sessions", response_model=List[ChatSessionOut])
async def list_chats(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    logger.info(f"Listing chat sessions with limit={limit} offset={offset}")
    sessions = await chat_session.get_all_chat_sessions(db, limit=limit, offset=offset)
    return sessions


@router.put("/chat_sessions/{session_id}", response_model=ChatSessionOut)
async def update_chat(session_id: UUID, session_update: ChatSessionCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Updating chat session: {session_id}")
    updated_session = await chat_session.update_chat_session(db, session_id, session_update.model_dump(exclude_unset=True))
    if not updated_session:
        logger.warning(f"Chat session {session_id} not found for update.")
        raise HTTPException(status_code=404, detail="Chat session not found")
    return updated_session


@router.delete("/chat_sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(session_id: UUID, db: AsyncSession = Depends(get_db)):
    logger.info(f"Deleting chat session: {session_id}")
    success = await chat_session.delete_chat_session(db, session_id)
    if not success:
        logger.warning(f"Chat session {session_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="Chat session not found")
    return None


@router.post("/chat_sessions/{session_id}/messages", response_model=MessageOut)
async def create_msg(session_id: UUID, msg_in: MessageCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating message for session {session_id}")
    db_msg = Message(**msg_in.model_dump(), session_id=session_id)
    return await message.create_message(db, db_msg)


@router.get("/chat_sessions/{session_id}/messages/{message_id}", response_model=MessageOut)
async def get_msg(session_id: UUID, message_id: UUID, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Fetching message {message_id} for session {session_id}")
    db_msg = await message.get_message(db, message_id)
    if not db_msg or db_msg.session_id != session_id:
        logger.warning(f"Message {message_id} not found in session {session_id}")
        raise HTTPException(status_code=404, detail="Message not found in this session")
    return db_msg


@router.get("/chat_sessions/{session_id}/messages", response_model=List[MessageOut])
async def get_messages_for_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    logger.info(f"Fetching all messages for session {session_id}")
    return await message.get_messages_for_session(db, session_id)


@router.put("/chat_sessions/{session_id}/messages/{message_id}", response_model=MessageOut)
async def update_msg(session_id: UUID, message_id: UUID, msg_in: MessageCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Updating message {message_id} in session {session_id}")
    db_msg = await message.get_message(db, message_id)
    if not db_msg or db_msg.session_id != session_id:
        logger.warning(f"Message {message_id} not found in session {session_id} for update.")
        raise HTTPException(status_code=404, detail="Message not found in this session")
    updated_msg = await message.update_message(db, message_id, msg_in.model_dump(exclude_unset=True))
    return updated_msg


@router.delete("/chat_sessions/{session_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_msg(session_id: UUID, message_id: UUID, db: AsyncSession = Depends(get_db)):
    logger.info(f"Deleting message {message_id} in session {session_id}")
    db_msg = await message.get_message(db, message_id)
    if not db_msg or db_msg.session_id != session_id:
        logger.warning(f"Message {message_id} not found in session {session_id} for deletion.")
        raise HTTPException(status_code=404, detail="Message not found in this session")
    deleted = await message.delete_message(db, message_id)
    if not deleted:
        logger.warning(f"Delete operation failed. Message {message_id} not found.")
        raise HTTPException(status_code=404, detail="Message not found")
    return None
