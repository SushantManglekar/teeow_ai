# detect_intent_node.py

from typing import List
from langchain_core.runnables import Runnable
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from app.schemas.state import ChatFlowState
import json
import logging

logger = logging.getLogger("ai_assistant")

class DetectIntentNode(Runnable):
    def __init__(self, kb_path: str, model_name: str = "llama3.2"):
        self.kb_path = kb_path
        self.vectorstore = self._load_vectorstore()
        self.llm = OllamaLLM(model=model_name, temperature=0)
        logger.info("DetectIntentNode initialized with model: %s", model_name)

    def _load_vectorstore(self):
        logger.debug("Loading vectorstore from knowledge base: %s", self.kb_path)
        try:
            with open(self.kb_path, "r") as f:
                kb = json.load(f)
        except Exception as e:
            logger.exception("Failed to load or parse KB JSON: %s", self.kb_path)
            raise

        docs = []
        for item in kb["intents"]:
            doc_text = f"""
                        Intent: {item['intent']}
                        Description: {item['description']}
                        Examples: {"; ".join(item['examples'])}
                    """
            docs.append(Document(page_content=doc_text, metadata={"intent": item["intent"]}))

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(docs, embeddings)
        logger.info("Vectorstore built with %d intent documents", len(docs))
        return vectorstore

    def _build_prompt(self, user_query: str, docs: List[Document]):
        logger.debug("Building prompt for intent classification...")
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that classifies user travel queries."),
            ("human", """
                User Query: {user_query}

                Here are the possible intent categories and their descriptions:

                {intents}

                🎯 Your task:
                Identify the **best-matching intent and sub_intent** based on the user query and the intent descriptions.

                🧾 Output format:
                Respond with exactly two values — the intent and the sub_intent — separated by a single comma.

                ✅ Format (no quotes, no labels, no JSON):
                intent_name,sub_intent_name

                ❌ Do not explain your answer.
                ❌ Do not include any extra text or formatting.
            """)
        ])
        return prompt_template.format_messages(
            user_query=user_query,
            intents="\n\n".join([doc.page_content for doc in docs])
        )

    def invoke(self, state: ChatFlowState) -> ChatFlowState:
        query = state.user_query
        logger.debug("Detecting intent for user query: %s", query)

        # Step 1: Retrieve relevant intents
        try:
            retrieved_docs = self.vectorstore.similarity_search(query, k=3)
            logger.info("Retrieved %d documents for intent classification", len(retrieved_docs))
        except Exception as e:
            logger.exception("Vector similarity search failed.")
            raise

        # Step 2: Generate prompt
        prompt_messages = self._build_prompt(query, retrieved_docs)
        logger.debug("Prompt successfully built for intent classification")

        # Step 3: Invoke LLM
        try:
            response = self.llm.invoke(prompt_messages)
            logger.info("LLM response received: %s", response.strip())
        except Exception as e:
            logger.exception("LLM invocation failed")
            raise

        # Step 4: Parse and assign intent
        try:
            detected_intent, detected_sub_intent = tuple((response.strip().lower().split(",")))
            state.intent = detected_intent.strip()
            state.sub_intent = detected_sub_intent.strip()
            logger.info("Intent detected: %s | Sub-intent: %s", state.intent, state.sub_intent)
        except Exception as e:
            logger.exception("Failed to parse LLM intent output: %s", response)
            raise

        return state
