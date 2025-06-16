from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import datetime
from fastapi.responses import JSONResponse
from app.schemas.message import MessageCreate, MessageOut
from app.schemas.chat import ChatRequest,ChatResponse
from app.models.message import Message
from app.db.connection import get_db
from app.services.RAG.rag_pipeline import RAGPipeline
from sqlalchemy.future import select
from sqlalchemy import desc
from .routes import router
import json

def parse_escaped_json(response_str: str) -> dict:
    try:
        # Remove newlines and parse the escaped JSON
        cleaned = response_str.strip()
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")


rag_pipeline = RAGPipeline()

@router.post("/ask")
async def ask_chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Fetch previous chat messages
        result = await db.execute(
            select(Message).where(Message.session_id == request.chat_session_id).order_by(desc(Message.timestamp))
        )
        messages = result.scalars().all()
        chat_history = [(msg.sender, msg.message) for msg in messages]
        print(chat_history)
        # 2. Save user query to DB
        user_msg = Message(
            id=uuid4(),
            session_id=request.chat_session_id,
            sender="user",
            message=request.user_query,
            timestamp=datetime.utcnow()
        )
        db.add(user_msg)
        await db.flush()  # get `user_msg.id`

        # 3. Generate AI response
        rag_result = rag_pipeline.run(request.user_query, chat_history)

        # 4. Save AI response to DB with response_to = user_msg.id
        ai_msg = Message(
            id=uuid4(),
            session_id=request.chat_session_id,
            sender="ai",
            message=rag_result["answer"],
            response_to=user_msg.id,
            timestamp=datetime.utcnow()
        )
        db.add(ai_msg)
        await db.commit()

        # 5. Return structured response
        return JSONResponse(content={"answer": parse_escaped_json(rag_result["answer"])})

        # ChatResponse(
            
            # refined_query=rag_result["refined_query"],
            # context=[doc.page_content for doc in rag_result["context"]],
            # generator_prompt=rag_result["generator_prompt"]
        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))