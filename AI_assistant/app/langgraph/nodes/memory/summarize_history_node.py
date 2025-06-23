# flows/langgraph/nodes/summarize_history.py

from app.schemas.state import ChatFlowState
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.models.message import Message
from sqlalchemy import select, asc
import logging

logger = logging.getLogger("ai_assistant")


async def summarize_history_node(state: ChatFlowState) -> ChatFlowState:
    """
    Summarizes the full chat session by querying all messages for the session_id from the DB.
    Returns updated state with `summary`.
    """
    db = state.db
    session_id = state.session_id

    logger.debug(f"Starting summarization for session_id: {session_id}")

    try:
        # Fetch all messages for session
        result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(asc(Message.timestamp))
        )
        rows = result.scalars().all()
        logger.info(f"Fetched {len(rows)} messages for summarization (session_id: {session_id})")

        # Short-circuit if not enough context
        if not rows or len(rows) < 12:
            logger.info(f"Insufficient messages for summarization (session_id: {session_id})")
            state.chat_history_summary = ""
            return state

        # Format messages
        history_text = "\n".join([
            f"{'User' if msg.sender == 'user' else 'AI'}: {msg.message}" for msg in rows
        ])
        logger.debug(f"Formatted history text for summarization (session_id: {session_id})")

        # Build prompt and chain
        prompt = PromptTemplate.from_template("""
            Summarize this travel-related conversation in **5 bullet points**.
            Focus on the user's intent, preferences, places discussed, and any questions asked.

            Conversation:
            {history}

            Summary:
        """)
        chain = prompt | OllamaLLM(model="llama3.2") | StrOutputParser()

        # Run summarization
        summary = chain.invoke({"history": history_text})
        state.chat_history_summary = summary.strip()

        logger.info(f"Generated summary for session_id: {session_id}")
        logger.debug(f"Summary: {state.chat_history_summary}")

    except Exception as e:
        logger.exception(f"Summarization failed for session_id: {session_id}")
        state.chat_history_summary = ""

    return state
