# flows/langgraph/nodes/retrieve_memory.py

from app.langgraph.nodes.memory.langchain_memory import Memory
from app.schemas.state import ChatFlowState
import logging

logger = logging.getLogger("ai_assistant")

async def retrieve_memory_node(state: ChatFlowState) -> ChatFlowState:
    logger.debug(f"Starting memory retrieval for session_id: {state.session_id}")

    try:
        memory_loader = Memory(session_id=state.session_id, db=state.db)
        memory = await memory_loader.get_memory()
        state.chat_memory = memory
        logger.info(f"Successfully retrieved memory for session_id: {state.session_id}")
    except Exception as e:
        logger.exception(f"Failed to retrieve memory for session_id: {state.session_id}")
        raise

    return state
