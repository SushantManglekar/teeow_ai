# Core chat logic or orchestration

import streamlit as st
import json
from app.utils.rag_pipeline import RAGPipeline


# Init RAG pipeline
rag = RAGPipeline()

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Teeow.ai RAG Chat", layout="wide")
st.title("🧳 Teeow.ai - Travel Chat Assistant")

# Session state to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat input box
user_input = st.chat_input("Ask your travel question...")

# Handle input
if user_input:
    st.session_state.chat_history.append(("user", user_input))

    # Run the RAG pipeline
    result = rag.run(user_input, chat_history=st.session_state.chat_history)

    # Try to parse JSON response
    try:
        parsed_json = json.loads(result["answer"])
        pretty_response = json.dumps(parsed_json, indent=2)
    except json.JSONDecodeError:
        pretty_response = result["answer"]

    st.session_state.chat_history.append(("ai", pretty_response))

# -------------------------
# Display chat messages
# -------------------------
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        if role == "ai":
            st.markdown(f"```json\n{message}\n```")
        else:
            st.markdown(message)
