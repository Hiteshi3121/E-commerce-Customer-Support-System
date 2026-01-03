import os
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()


class ConversationState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    intent: str
    session_id: str   # conversation memory
    user_id: str      # persistent identity

    # ---- order-aware conversation support ----
    active_order_id: Optional[str]   # stores detected order ID across turns
    pending_intent: Optional[str]    # stores intent until order ID is provided

    # ---- human escalation support ----
    escalation_reason: Optional[str]  # why conversation was escalated
    

def get_last_human_message(messages):
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""
