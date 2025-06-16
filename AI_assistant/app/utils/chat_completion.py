# teeow_rag_ui.py

import os
import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema import messages_from_dict, messages_to_dict

# -------------------------
# Mock Data for Knowledge Base
# -------------------------


mock_docs = [
    {"content": "Abbey Falls is a popular waterfall in Coorg surrounded by coffee plantations."},
    {"content": "Dubare Elephant Camp offers elephant interactions including bathing and feeding."},
    {"content": "Try Coorgi Pandi Curry at Raintree Restaurant in Madikeri for an authentic experience."},
    {"content": "Stay at Zostel Coorg for budget-friendly and social accommodation with local guides."}
]

# -------------------------
# Build FAISS Vector Store
# -------------------------
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
texts = [doc["content"] for doc in mock_docs]
vectorstore = FAISS.from_texts(texts, embedding)
retriever = vectorstore.as_retriever()

# -------------------------
# System Prompt Template
# -------------------------
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are Teeow.ai, a structured travel assistant.
Use the context below to answer the user query.
Respond strictly in JSON with keys day_1, day_2, ..., each having activities, food, and hotel.
Context: {context}
User: {question}
"""
)

# -------------------------
# Connect to Local LLM (Ollama)
# -------------------------
llm = Ollama(model="llama3.2")

rag_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    combine_docs_chain_kwargs={"prompt": prompt_template}
)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Teeow.ai RAG Chat", layout="wide")
st.title("🧳 Teeow.ai")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask your travel question...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    result = rag_chain.invoke({
        "question": user_input,
        "chat_history": messages_from_dict([])  # can be enhanced with actual chat objects
    })

    answer = result["answer"]
    st.session_state.chat_history.append(("ai", answer))

# Display chat messages
for role, message in st.session_state.chat_history:
    if role == "user":
        with st.chat_message("user"):
            st.markdown(message)
    else:
        with st.chat_message("assistant"):
            st.markdown(f"```json\n{message}\n```")
