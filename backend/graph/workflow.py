from langgraph.graph import StateGraph, END
from backend.graph.state import ConversationState
from backend.graph.router import intent_router, route_by_next_node
from backend.agents.order_agent import order_agent
from backend.agents.track_agent import track_agent
from backend.agents.ticket_agent import ticket_agent
from backend.agents.return_agent import return_agent
from backend.rag.faq_agent import faq_llm
from backend.memory import save_memory
from dotenv import load_dotenv

load_dotenv()


def persist_memory(state: ConversationState):
    """
    Persist only recent messages for conversation continuity.
    """
    save_memory(state["session_id"], state["messages"][-2:])
    return state


def create_workflow():
    graph = StateGraph(ConversationState)

    # -----------------------------
    # ENTRY POINT
    # -----------------------------
    graph.set_entry_point("intent_router")

    # -----------------------------
    # NODES
    # -----------------------------
    graph.add_node("intent_router", intent_router)
    graph.add_node("faq_llm", faq_llm)
    graph.add_node("order_agent", order_agent)
    graph.add_node("track_agent", track_agent)
    graph.add_node("ticket_agent", ticket_agent)
    graph.add_node("return_agent", return_agent)
    graph.add_node("persist_memory", persist_memory)

    # -----------------------------
    # CONDITIONAL ROUTING
    # -----------------------------
    graph.add_conditional_edges(
        "intent_router",
        route_by_next_node,
        {
            "faq_agent": "faq_llm",
            "order_agent": "order_agent",
            "track_agent": "track_agent",
            "ticket_agent": "ticket_agent",
            "return_agent": "return_agent",
            "END": END,
        }
    )

    # -----------------------------
    # MEMORY → END
    # -----------------------------
    for node in [
        "faq_llm",
        "order_agent",
        "track_agent",
        "ticket_agent",
        "return_agent",
    ]:
        graph.add_edge(node, "persist_memory")

    graph.add_edge("persist_memory", END)

    return graph.compile()
