import re
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from backend.graph.state import get_last_human_message
from dotenv import load_dotenv

load_dotenv()

ORDER_ID_REGEX = r"(ORD-[A-Za-z0-9]+)"

intent_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# ----------------------------------
# Human escalation trigger phrases
# ----------------------------------
ESCALATION_PHRASES = [
    "human", "agent", "real person","talk to support", "frustrating" "not helpful", "frustrated",
    "this is useless", "escalate", "talk to human", "speak to human", "real person", "customer service", "call center", "agent", "supervisor",
    "manager", "human agent", "live agent", "representative", "Customer support", "Need help", 
]

COMPLAINT_KEYWORDS = [
        "complaint", "complain", "worst", "terrible", "horrible",  "scam", "fraud", 
        "cheated", "consumer forum", "legal", "lawyer", "court", "sue", "police", "cyber crime"
    ]

URGENT_KEYWORDS = [
        "urgent", "emergency", "immediately", "asap", "right now",
        "critical", "very important", "need help now"
    ]


def llm_intent_classify(text: str) -> str:
    prompt = f"""
Classify the user's intent into ONE of the following:
- place_order
- track_order
- return_order
- raise_ticket
- faq_llm

User message:
"{text}"

Respond with ONLY the intent label.
"""
    return intent_llm.invoke(prompt).content.strip()

# ----------------------------------
# Main Router: Intent Classification
# ----------------------------------

def intent_router(state):
    """
    Router node:
    - decides next_node
    - ALWAYS returns state
    """

    user_text = get_last_human_message(state["messages"]).strip()
    lowered = user_text.lower()
    intent = None

    # ----------------------------------
    # 🔒 ORDER FLOW LOCK
    # ----------------------------------
    if state.get("order_context"):
        state["next_node"] = "order_agent"
        return state


    # =====================================================
    # 🚨 STEP 0: Explicit Human Escalation (User requested)
    # =====================================================
    if any(p in lowered for p in ESCALATION_PHRASES):
        state["escalation_reason"] = "User Requested Human"
        state["next_node"] = "ticket_agent"
        return state    
    if any(p in lowered for p in URGENT_KEYWORDS):
        state["escalation_reason"] = "Urgent User Request"
        state["next_node"] = "ticket_agent"
        return state
    if any(p in lowered for p in COMPLAINT_KEYWORDS):
        state["escalation_reason"] = "Detected Complaint / Legal Issues"
        state["next_node"] = "ticket_agent"
        return state

    # -----------------------------
    # STEP 1: Extract order ID
    # -----------------------------
    match = re.search(ORDER_ID_REGEX, user_text)
    if match:
        state["active_order_id"] = match.group(1)

    # -----------------------------
    # STEP 2: Detect invalid-looking order ID
    # -----------------------------
    if (
        not match
        and user_text.isalnum()
        and any(c.isdigit() for c in user_text)
        and len(user_text) < 15
    ):
        state["messages"].append(
            AIMessage(
                content=(
                    "⚠️ That doesn't look like a valid order ID.\n"
                    "Correct format: **ORD-XXXXXX**, Please check and try again."
                )
            )
        )
        state["next_node"] = "END"
        return state

    # -----------------------------
    # STEP 3: Detect intent (rule-based)
    # -----------------------------
    if any(q in lowered for q in ["what", "who", "company", "policy"]):
        intent = "faq_agent"

    elif "track" in lowered or "status" in lowered:
        intent = "track_agent"

    elif "return" in lowered or "send back" in lowered:
        intent = "return_agent"

    elif any(k in lowered for k in ["ticket", "complaint", "not received", "issue", "problem"]):
        intent = "ticket_agent"

    elif any(k in lowered for k in ["place", "buy", "order"]):
        intent = "order_agent"

    # -----------------------------
    # CASE A: Pending intent + order ID
    # -----------------------------
    if state.get("pending_intent") and state.get("active_order_id"):
        state["next_node"] = state["pending_intent"]
        state["pending_intent"] = None
        return state

    # -----------------------------
    # CASE C: Intent but missing Order ID
    # -----------------------------
    if intent in ["track_agent", "return_agent", "ticket_agent"] and not state.get("active_order_id"):
        state["pending_intent"] = intent
        state["messages"].append(
            AIMessage(
                content={
                    "track_agent": (
                        "Please provide your ORDER ID to TRACK your order.\n\n"
                        "*FORMAT: Track ORD-XXXX*"
                    ),
                    "return_agent": (
                        "Please provide your ORDER ID to RETURN your order.\n\n"
                        "*FORMAT: Return ORD-XXXX*"
                    ),
                    "ticket_agent": (
                        "Please provide your ORDER ID and issue to RAISE a SUPPORT TICKET.\n\n"
                        "*FORMAT: Raise ticket for ORD-XXXX with ISSUE*"
                    ),
                }[intent]
            )
        )
        state["next_node"] = "END"
        return state

    # -----------------------------
    # CASE B: Order ID but no intent
    # -----------------------------
    if state.get("active_order_id") and intent is None and not state.get("pending_intent"):
        state["messages"].append(
            AIMessage(
                content=(
                    f"I found your order ID **{state['active_order_id'].upper()}**.\n\n"
                    "*Please tell me exactly what you want me to do: (refer the below formate)*\n\n"
                    "• Track the ORD-XXXX\n\n"
                    "• Return the ORD-XXXX\n\n"
                    "• Raise a support ticket for ORD-XXXX with your concerns)"
                )
            )
        )
        state["next_node"] = "END"
        return state

    # -----------------------------
    # CASE A: Intent + order ID
    # -----------------------------
    if intent in ["track_agent", "return_agent", "ticket_agent"] and state.get("active_order_id"):
        state["next_node"] = intent
        return state

    # -----------------------------------------------------
    # 🚨 STEP 8: Never let just numbers go to LLM
    # ------------------------------------------------------
    if lowered.isdigit():
        state["messages"].append(
            AIMessage(
                content=(
                    "I can't understand, Can you please describe your Query."
                )
            )
        )
        state["next_node"] = "END"
        return state

    # -----------------------------
    # STEP 9: LLM fallback
    # -----------------------------
    llm_intent = llm_intent_classify(user_text)
    state["next_node"] = {
        "place_order": "order_agent",
        "track_order": "track_agent",
        "return_order": "return_agent",
        "raise_ticket": "ticket_agent",
    }.get(llm_intent, "faq_agent")

    return state


def route_by_next_node(state):
    return state.get("next_node", "END")


