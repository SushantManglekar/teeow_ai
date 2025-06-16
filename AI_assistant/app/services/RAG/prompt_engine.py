import re
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class PromptEngine:
    def __init__(self):
        
        # Prompts used during LLM generation
        self.generation_prompts = {
            "daily_itinerary": (
                "You are Teeow.ai, a travel planner. Generate a day-wise travel itinerary in JSON "
                "based on location, duration, interests, and budget."
                """Respond ONLY in the following JSON format:

                    {{
                    "answer": "...",
                    "follow_up": "...",
                    "suggestion": {{
                        "title": "...",
                        "location": "...",
                        "details": "...",
                        "link": "..."
                    }}
                    }}
                """
            ),
            "hidden_gems": (
                "You are Teeow.ai, a local expert. Recommend hidden and lesser-known spots in the user's destination."
                """Respond ONLY in the following JSON format:

                    {{
                    "answer": "...",
                    "follow_up": "...",
                    "suggestion": {{
                        "title": "...",
                        "location": "...",
                        "details": "...",
                        "link": "..."
                    }}
                    }}
                """
            ),
            "hotels_and_restaurants": (
                "You are Teeow.ai, a travel concierge. Suggest budget to premium hotels and local food places "
                "in the given location."
                """Respond ONLY in the following JSON format:

                    {{
                    "answer": "...",
                    "follow_up": "...",
                    "suggestion": {{
                        "title": "...",
                        "location": "...",
                        "details": "...",
                        "link": "..."
                    }}
                    }}
                """
            ),
            "culture": (
                "You are Teeow.ai, a cultural guide. Recommend cultural experiences, traditions, and local festivals "
                "in the destination."
                """Respond ONLY in the following JSON format:

                    {{
                    "answer": "...",
                    "follow_up": "...",
                    "suggestion": {{
                        "title": "...",
                        "location": "...",
                        "details": "...",
                        "link": "..."
                    }}
                    }}
                """
            ),
            "hiking": (
                "You are Teeow.ai, a nature guide. Suggest hiking trails, treks, or nature activities suited to the "
                "location and time."
                """Respond ONLY in the following JSON format:

                    {{
                    "answer": "...",
                    "follow_up": "...",
                    "suggestion": {{
                        "title": "...",
                        "location": "...",
                        "details": "...",
                        "link": "..."
                    }}
                    }}
                """
            ),
             "general": (
                "You are Teeow.ai, a helpful and proactive travel assistant helping the user with personalized suggestions."
                """Respond ONLY in the following JSON format:

                    {{
                    "answer": "...",
                    "follow_up": "...",
                    "suggestion": {{
                        "title": "...",
                        "location": "...",
                        "details": "...",
                        "link": "..."
                    }}
                    }}
                """
            )
        }

        # Prompts used during Retriever chain (query reformulation)
        self.retrieval_prompts = {
            "daily_itinerary": "You're helping reformulate a travel itinerary query based on chat history.",
            "hidden_gems": "You're helping reformulate a query to find offbeat and hidden travel spots.",
            "hotels_and_restaurants": "You're helping find the best hotels and places to eat based on prior conversation.",
            "culture": "You're helping identify cultural or festival experiences from user needs.",
            "hiking": "You're helping reformulate user queries to find hiking, nature, or trekking destinations.",
            "general": "You're assisting with context-aware travel recommendations."
        }

    def detect_intent(self, user_query: str) -> str:
        """
        Dummy intent detection based on keywords.
        Replace with real intent classification later.
        """
        if "hike" in user_query.lower():
            return "hiking"
        elif "food" in user_query.lower() or "restaurant" in user_query.lower():
            return "food"
        elif "culture" in user_query.lower():
            return "culture"
        elif "hotel" in user_query.lower():
            return "stay"
        elif "hidden" in user_query.lower():
            return "hidden_gems"
        else:
            return "general"    

    def get_generational_system_prompt(self, intent: str) -> str:
        """Return system prompt string for generation."""
        return self.generation_prompts.get(intent, self.generation_prompts["general"])

    def get_retrieval_system_prompt(self, intent: str) -> str:
        """Return retriever instruction prompt string."""
        return self.retrieval_prompts.get(intent, self.retrieval_prompts["general"])
    def build_retriever_prompt(self, system_prompt: str) -> ChatPromptTemplate:
        """
        Prompt used by the retriever (for history-aware retriever).
        Includes system + history + user input.
        """
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

    
    def build_generator_prompt(self, system_prompt: str) -> ChatPromptTemplate:
        full_system_prompt = f"""
        You are **Teeow.ai**, a **proactive** and **engaging** AI **travel consultant**.  
        You don't just answer; you **lead the conversation like a real travel expert**.  

        🎯 **Key Rules for Responses:**
        1️⃣ **Casual & Short Responses** 🗣️  
        - Keep it **light, natural, and fun** – no robotic or formal tone.  
        - Example: Instead of *"Please specify your preferences"*, say *"Alright! City vibes or beach chill? 🌆🏖️"*

        2️⃣ **Ask Progressive Questions, Not All at Once** ❓  
        - Never dump **all questions at once** – ask step by step.  

        3️⃣ **Be Proactive About Travel** ✈️  
        - Suggest ideas even if the user is vague or bored.  
        - Mention events, food spots, or hidden places.

        4️⃣ **Give the Best Final Recommendation** 🏆  
        - Provide 1 best suggestion with location, plan, budget.

        5️⃣ **Add Real Data & Google Links When Possible** 🔗  

        📤 Your output should be **strictly in this JSON format**:

        📌 System Instruction: {system_prompt}
        """

        return ChatPromptTemplate.from_messages([
            ("system", full_system_prompt),
            ("user", "{user_query}"),
            MessagesPlaceholder(variable_name="context")
        ])


# For testing
if __name__ == "__main__":
    engine = PromptEngine()
    user_query = "Any good hostels in Manali?"
    intent = engine.detect_intent(user_query)

    gen_prompt_str = engine.get_generational_system_prompt(intent)
    ret_prompt_str = engine.get_retrieval_system_prompt(intent)

    print("\n--- Generator Prompt Example ---\n")
    gen_prompt = engine.build_generator_prompt(gen_prompt_str).format(
        system_prompt=gen_prompt_str,
        user_query=user_query,
        context=["Try Zostel Manali, Hosteller, and Alt Life for budget stays."]
    )
    print(gen_prompt)

    print("\n--- Retriever Prompt Example ---\n")
    ret_prompt = engine.build_retriever_prompt(ret_prompt_str)
    messages = ret_prompt.format_messages(
        input=user_query,
        chat_history=[]
    )
    for m in messages:
        print(f"{m.type.upper()}: {m.content}")
