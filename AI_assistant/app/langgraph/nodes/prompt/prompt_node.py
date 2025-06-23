# app/langgraph/nodes/prompt/prompt_node.py

from jinja2 import Template
from json import dumps
from app.schemas.state import ChatFlowState
from app.langgraph.nodes.prompt.get_prompt import PromptBuilder
import logging

logger = logging.getLogger("ai_assistant")


async def prompt_node(state: ChatFlowState) -> ChatFlowState:
    logger.debug(f"Starting prompt_node for session_id: {state.session_id}")

    try:
        builder = PromptBuilder()
        intent_obj = state.intent_object

        logger.debug("Rendering system_instruction from intent object...")
        rendered_instruction = Template(intent_obj["system_instruction"]).render(
            sub_intent=state.sub_intent,
            user_location=state.user_location,
            current_time=state.current_time
        )
        logger.info("System instruction rendered successfully.")

        logger.debug("Rendering output_format template...")
        output_format_raw = dumps(intent_obj["output_format"], indent=2)
        rendered_output_format = Template(output_format_raw).render(
            sub_intent=state.sub_intent,
            user_location=state.user_location
        )
        logger.info("Output format rendered successfully.")

        logger.debug("Formatting full prompt using ChatPromptTemplate...")
        prompt_template = builder.get_prompt()
        prompt_messages = prompt_template.format_messages(
            system_instruction=rendered_instruction,
            output_format=rendered_output_format,
            user_query=state.user_query,
            user_location=state.user_location,
            current_time=state.current_time,
            user_preferences=state.user_preferences or "",
            chat_history_summary=state.chat_history_summary or "",
            chat_memory=state.chat_memory or "",
            realtime_info=state.realtime_info or ""
        )
        logger.info("Prompt messages constructed successfully.")

        # Optionally log first message snippet
        logger.debug(f"Prompt preview: {prompt_messages[0].content[:100]}...")

        state.prompt = prompt_messages

    except Exception as e:
        logger.exception(f"Failed to construct prompt for session_id: {state.session_id}")
        raise

    return state
