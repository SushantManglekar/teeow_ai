# flows/langgraph/recommendation_graph.py

from langgraph.graph import StateGraph, END
from app.schemas.state import ChatFlowState

# Node imports
from app.langgraph.nodes.memory.memory_node import retrieve_memory_node
from app.langgraph.nodes.memory.summarize_history_node import summarize_history_node
from app.langgraph.nodes.prompt.prompt_node import prompt_node
from app.langgraph.nodes.generate_response_node import generate_response_node
from app.langgraph.nodes.save_to_db_node import save_to_db_node

def build_recommendation_graph():
    graph = StateGraph(ChatFlowState)

    # Add each node
    graph.add_node("retrieve_memory", retrieve_memory_node)
    graph.add_node("summarize_history", summarize_history_node)
    graph.add_node("build_prompt", prompt_node)
    graph.add_node("generate_response", generate_response_node)
    graph.add_node("save_to_db", save_to_db_node)

    # Define flow
    graph.set_entry_point("retrieve_memory")
    graph.add_edge("retrieve_memory", "summarize_history")
    graph.add_edge("summarize_history", "build_prompt")
    graph.add_edge("build_prompt", "generate_response")
    graph.add_edge("generate_response", "save_to_db")
    graph.add_edge("save_to_db", END)

    return graph.compile()
