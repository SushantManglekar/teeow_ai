import json
import re
import logging
from langchain_ollama import OllamaLLM
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import JsonOutputParser
from app.schemas.state import ChatFlowState

logger = logging.getLogger("ai_assistant")
llm = OllamaLLM(model="llama3.2")


def safe_json_parse(text: str) -> dict:
    """
    Attempts to safely parse a JSON string. If the initial attempt fails,
    it uses LangChain's OutputFixingParser as a fallback.
    """
    try:
        if not isinstance(text, str):
            logger.warning("Input is not a string. Attempting to convert...")
            text = str(text)

        # Clean & normalize
        text = text.strip()
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        text = re.sub(r'(?<!\\)(\n|\r|\t)', ' ', text)
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        text = text.encode("utf-8", "ignore").decode()

        # Try direct JSON parse
        parsed = json.loads(text)
        logger.info("Direct JSON parsing successful.")
        return parsed

    except json.JSONDecodeError as e:
        logger.warning("Direct JSON parsing failed: %s", e)
        logger.debug("Preview of invalid JSON: %s", text[:500] + ("..." if len(text) > 500 else ""))

        try:
            logger.info("Attempting fallback using OutputFixingParser...")
            parser = OutputFixingParser.from_llm(
                parser=JsonOutputParser(),
                llm=llm
            )
            parsed = parser.parse(text)
            logger.info("Fallback parser succeeded.")
            return parsed

        except Exception as fallback_err:
            logger.exception("Fallback parser failed.")
            return {}


async def generate_response_node(state: ChatFlowState) -> ChatFlowState:
    """
    Generates an AI response using the retrieved memory, detected intent, and the user query.
    """
    if not state.prompt or any(p is None for p in state.prompt):
        logger.error("Prompt messages are invalid or contain None.")
        raise ValueError("Prompt messages are invalid or contain None.")

    logger.debug("Final prompt sent to LLM: %s", state.prompt)

    try:
        response = llm.invoke(state.prompt)
        logger.info("LLM response received successfully.")
    except Exception as e:
        logger.exception("LLM invocation failed.")
        raise

    # Parse the response
    parsed_response = safe_json_parse(response)
    if parsed_response:
        logger.info("Response parsed into JSON successfully.")
    else:
        logger.warning("Response parsing returned an empty result.")

    state.response = parsed_response
    return state
