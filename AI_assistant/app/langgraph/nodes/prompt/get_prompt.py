from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from jinja2 import Template
import json
import logging

logger = logging.getLogger("ai_assistant")


class PromptBuilder:
    """
    Flexible prompt builder for Teeow.ai generation tasks.
    Allows formatting with dynamic variables using LangChain's ChatPromptTemplate.
    """

    def __init__(self):
        logger.debug("Initializing PromptBuilder...")

        try:
            system_template = """
                You are **Teeow.ai**, a smart and friendly AI **travel consultant**.

                - system_instruction: {system_instruction}

                📌 Personalization:
                - Location: {user_location}
                - Time: {current_time}
                - Preferences: {user_preferences}
                - Past Summary: {chat_history_summary}
                - Last Messages: {chat_memory}

                📡 Real-time Info: {realtime_info}
                🧾 FORMAT INSTRUCTIONS:
                You must **respond ONLY using the JSON structure shown below**. Do not create new keys. Do not add fields like "answer", "suggestions", or "follow_up" unless they already exist in the format. 

                🧱 OUTPUT STRUCTURE (MUST match exactly):
                ```json
                {output_format}
                ```
            """

            user_template = "User Query: {user_query}"

            self.template = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_template),
                HumanMessagePromptTemplate.from_template(user_template)
            ])

            logger.info("PromptBuilder initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize PromptBuilder.")

    def get_prompt(self):
        logger.debug("Retrieving ChatPromptTemplate from PromptBuilder.")
        return self.template


if __name__ == "__main__":

    intent_obj = {
        "intent": "recommendation",
        "sub_intents": ["food", "attractions", "activities", "local gems"],
        "description": "User is looking for suggestions or recommendations, often based on location, context or personal preferences.",
        "examples": [
            "Find best restaurants near me",
            "What to do in Paris this weekend?",
            "Cool things to see in Goa today"
        ],
        "flow_id": "recommendation_flow",
        "confidence_threshold": 0.75,
        "system_instruction": "Suggest 2–3 personalized and highly-rated {sub_intent} options based on user preferences, location, and time. Use real-time data if available. Respond in a friendly, clear tone and include ratings, descriptions, and links.",
        "required_prompt_parameters": [
            "intent", "sub_intent", "user_query", "user_location", "current_time",
            "user_preferences", "chat_history_summary", "chat_memory", "output_format"
        ],
        "optional_prompt_parameters": ["realtime_info"],
        "output_format": {
            "title": "Top Recommendations for {sub_intent} in {user_location}",
            "summary": "Here are the most relevant, high-quality suggestions based on your preferences:",
            "items": [
                {
                    "name": "Place Name",
                    "description": "Short summary of what makes it great.",
                    "rating": 4.5,
                    "price_level": "$$",
                    "distance_km": 1.2,
                    "link": "https://..."
                }
            ],
            "follow_up": "Want to explore similar options or book something now?"
        }
    }
    
    # Simulated input values
    state = {
        "sub_intent": "food",
        "user_location": "New Delhi",
        "current_time": "2025-06-22 12:30 PM",
        "user_query": "Find romantic vegetarian restaurants near me",
        "user_preferences": "vegetarian, romantic, low budget",
        "chat_history_summary": "User is planning a romantic weekend in Delhi",
        "chat_memory": "Previously asked for cafes and couple activities",
        "realtime_info": "3 romantic vegetarian restaurants nearby are open with 4.5+ ratings"
    }

    # ✅ Fix: Pre-render system_instruction and output_format using jinja2
    rendered_instruction = Template(intent_obj["system_instruction"]).render(**state)
    rendered_output_format = Template(json.dumps(intent_obj["output_format"], indent=2)).render(**state)

    # Build prompt
    builder = PromptBuilder()
    prompt = builder.get_prompt()

    # Final prompt messages
    messages = prompt.format_messages(
        system_instruction=rendered_instruction,
        output_format=rendered_output_format,
        user_query=state["user_query"],
        user_location=state["user_location"],
        current_time=state["current_time"],
        user_preferences=state["user_preferences"],
        chat_history_summary=state["chat_history_summary"],
        chat_memory=state["chat_memory"],
        realtime_info=state["realtime_info"]
    )

    # Print prompt messages
    print("\n--- Rendered Prompt Messages ---\n")
    for msg in messages:
        print(f"{msg.type.upper()}: {msg.content}\n")
