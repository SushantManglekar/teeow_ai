from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document

from .prompt_engine import PromptEngine
from .vector_store import VectorStore
from langchain_ollama import OllamaLLM


class RAGPipeline:
    def __init__(self):
        self.llm = OllamaLLM(model="llama3.2")
        self.prompt_engine = PromptEngine()
        self.vector_store = VectorStore()

    def run(self, user_query: str, chat_history: list = []):
        # Step 1: Detect intent
        intent = self.prompt_engine.detect_intent(user_query)

        # Step 2: Get relevant prompt templates
        gen_prompt_template = self.prompt_engine.get_generational_system_prompt(intent)
        ret_prompt_template = self.prompt_engine.get_retrieval_system_prompt(intent)


        dummy_data = [
            Document(
                page_content="Authentic Coorg pork curry served in a cozy restaurant.",
                metadata={
                    "title": "Pandi Curry at Raintree",
                    "location": "Madikeri",
                    "category": "food",
                    "source": "tripadvisor"
                }
            ),
            Document(
                page_content="Abbey Falls is a majestic waterfall near Madikeri, surrounded by lush coffee plantations and spice estates.",
                metadata={
                    "title": "Abbey Falls",
                    "location": "Madikeri",
                    "category": "nature",
                    "source": "karnataka tourism"
                }
            ),
            Document(
                page_content="Dubare Elephant Camp offers unique elephant interactions like feeding, bathing, and guided forest walks.",
                metadata={
                    "title": "Dubare Elephant Camp",
                    "location": "Dubare",
                    "category": "wildlife",
                    "source": "incredible india"
                }
            ),
            Document(
                page_content="Namdroling Monastery, also known as the Golden Temple, showcases Tibetan architecture and offers a peaceful retreat.",
                metadata={
                    "title": "Namdroling Monastery",
                    "location": "Bylakuppe",
                    "category": "culture",
                    "source": "lonely planet"
                }
            ),
            Document(
                page_content="Tadiandamol is the highest peak in Coorg, offering scenic hiking trails and panoramic views of the Western Ghats.",
                metadata={
                    "title": "Tadiandamol Trek",
                    "location": "Kakkabe",
                    "category": "hiking",
                    "source": "indiahikes"
                }
            ),
            Document(
                page_content="Coorg is famous for its coffee plantations where visitors can tour the estates and learn about coffee production.",
                metadata={
                    "title": "Coorg Coffee Trail",
                    "location": "Coorg",
                    "category": "experience",
                    "source": "coorg tourism"
                }
            ),
            Document(
                page_content="Zostel Coorg is a vibrant hostel in Madikeri that attracts backpackers with community vibes and local experiences.",
                metadata={
                    "title": "Zostel Coorg",
                    "location": "Madikeri",
                    "category": "stay",
                    "source": "zostel"
                }
            )
        ]
        self.vector_store.load_data(dummy_data)
        # Step 3: Use LLM to refine the query (based on chat history, if needed)
        retriever_prompt = self.prompt_engine.build_retriever_prompt(ret_prompt_template)
        retriever_messages = retriever_prompt.format_messages(
            input=user_query,
            chat_history=chat_history
        )
        refined_query = self.llm.invoke(retriever_messages)

        # Step 4: Retrieve relevant documents using refined query
        retriever = self.vector_store.get_retriever()
        documents = retriever.get_relevant_documents(refined_query)
        context_chunks = [doc.page_content for doc in documents]

        # Step 5: Build the final generative prompt
        generator_prompt = self.prompt_engine.build_generator_prompt(gen_prompt_template)
        formatted_prompt = generator_prompt.format(
            system_prompt=gen_prompt_template,
            user_query=user_query,
            context=context_chunks
        )

        # Step 6: Get answer from LLM
        response = self.llm.invoke(formatted_prompt)

        return {
            "answer": response,
            "context": context_chunks,
            "refined_query": refined_query,
            "generator_prompt": formatted_prompt,
            "retriever_messages": retriever_messages
        }



# ✅ Test it
if __name__ == "__main__":
   
    dummy_data = [
            Document(
        page_content="Authentic Coorg pork curry served in a cozy restaurant.",
        metadata={
            "title": "Pandi Curry at Raintree",
            "location": "Madikeri",
            "category": "food",
            "source": "tripadvisor"
        }
    )

    ]

    rag = RAGPipeline()
    rag.vector_store.load_data(dummy_data)

    user_query = "Where can I try local Coorg dishes?"
    result = rag.run(user_query)

    print("\n--- LLM Answer ---\n", result["answer"])
    print("\n--- Refined Query ---\n", result["refined_query"])
    print("\n--- Used Context ---\n", result["context"])
    print("\n--- Final Prompt Sent to LLM ---\n", result["generator_prompt"])

