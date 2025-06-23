from uuid import uuid4
from datetime import datetime, timezone
from app.models.message import Message
from app.crud.message import create_message
from app.schemas.state import ChatFlowState
from app.utils.format_json_as_text import format_json_as_text  # type: ignore
import logging

logger = logging.getLogger("ai_assistant")

async def save_to_db_node(state: ChatFlowState) -> ChatFlowState:
    """
    Saves the user message and the AI response to the Postgres DB.
    """

    db = state.db
    session_id = state.session_id
    user_query = state.user_query
    response = state.response  # type: ignore

    # Format AI response into readable text
    ai_response = format_json_as_text(response)  # type: ignore

    logger.debug(f"Raw AI response for formatting: {response}")

    now = datetime.now(timezone.utc)

    # 1. Create user message
    user_msg = Message(
        id=uuid4(),
        session_id=session_id,
        sender="user",
        message=user_query,
        timestamp=now
    )

    try:
        user_msg = await create_message(db, user_msg)
        logger.info(f"User message saved with ID: {user_msg.id}")
    except Exception as e:
        logger.exception("❌ Failed to save user message to the database.")
        raise

    # 2. Create AI response message
    ai_msg = Message(
        id=uuid4(),
        session_id=session_id,
        sender="ai",
        message=ai_response,
        response_to=user_msg.id,
        timestamp=now
    )

    try:
        ai_msg = await create_message(db, ai_msg)
        logger.info(f"AI message saved with ID: {ai_msg.id} (response to {user_msg.id})")
    except Exception as e:
        logger.exception("❌ Failed to save AI message to the database.")
        raise

    return {
        "response": response
    }
