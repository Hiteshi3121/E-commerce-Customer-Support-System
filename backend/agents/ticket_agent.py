from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from datetime import datetime, timedelta
from backend.db import get_connection
from backend.graph.state import ConversationState, get_last_human_message
from dotenv import load_dotenv
import uuid

load_dotenv()

# -----------------------------
# Database connection
# -----------------------------
conn = get_connection()
cursor = conn.cursor()

# -----------------------------
# LLM for agent reasoning
# -----------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# =====================================================================
# TOOL 1: Generate ticket ID
# =====================================================================
def generate_ticket_id():
    return f"TCK-{uuid.uuid4().hex[:6].upper()}"


# =====================================================================
# TOOL 2: Create support ticket
# =====================================================================
def create_ticket(ticket_num, user_id, order_id, issue, status):
    cursor.execute(
        """
        INSERT INTO support_tickets (ticket_num, user_id, order_id, issue, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (ticket_num, user_id, order_id, issue, status)
    )
    conn.commit()


# =====================================================================
# AGENT: Ticket Agent
# =====================================================================
def ticket_agent(state: ConversationState) -> ConversationState:
    """
    LLM-powered Ticket Agent.
    Supports:
    - Normal order-based tickets
    - Human escalation tickets (NO order ID required)
    """

    user_id = state.get("user_id")
    order_id = state.get("active_order_id")
    escalation_reason = state.get("escalation_reason")
    user_text = get_last_human_message(state["messages"])

    ticket_num = generate_ticket_id()

    # =====================================================
    # 🚨 STEP 1: HUMAN ESCALATION (NO ORDER ID REQUIRED)
    # =====================================================
    if escalation_reason :
        issue = f"Escalated Reason: {escalation_reason}"

        create_ticket(
            ticket_num=ticket_num,
            user_id=user_id,
            order_id=None,
            issue=issue,
            status="ESCALATED"
        )
        
        state["messages"].append(
            AIMessage(
                content=(
                    "👤 **Your request has been escalated to a human support agent :**\n\n"
                    f"🎫 Ticket Number: **{ticket_num}**\n\n"
                    f"🎫 **{issue}**\n\n"
                    "Our team will review the conversation and get back to you shortly.\n\n"
                    "In case you don't get a call back in next 12hrs.\n Please contact our customer support team :\n\n"
                    f"📞 *Phone: +91 98765 43210 (8 AM - 10 PM IST)*\n"
                    f"📧 *Email: support@novacart.in*\n"
                )
            )
        )
        return state

    # =====================================================
    # STEP 2: Ensure ORDER ID exists (for normal tickets)
    # =====================================================
    if not order_id:
        state["messages"].append(
            AIMessage(
                content=(
                    "Sure 👍 Please provide your **ORDER ID** to raise a support ticket.\n\n"
                    "*Example: Raise a ticket for ORD-XXXX because my item is damaged*"
                )
            )
        )
        return state
    

    # =====================================================
    # STEP 3: Extract issue using LLM
    # =====================================================
    issue_prompt = f"""
You are a customer support assistant.

User message:
"{user_text}"

Task:
- Extract the customer's issue clearly.
- If the issue is unclear, return null.

Respond ONLY in JSON:
{{
  "issue": null or "<issue description>"
}}
"""
    try:
        issue_data = eval(llm.invoke(issue_prompt).content.strip())
        issue = issue_data.get("issue")
    except Exception:
        issue = None

    # =====================================================
    # STEP 4: Ask for issue if missing
    # =====================================================
    if not issue or not isinstance(issue, str) or len(issue.strip()) < 5:
        state["messages"].append(
            AIMessage(
                content=(
                    "📝 Please briefly describe the issue you are facing with your order.\n\n"
                    "*Example: The product arrived damaged*"
                )
            )
        )
        return state

    # =====================================================
    # STEP 5: Create normal support ticket
    # =====================================================
    create_ticket(
        ticket_num=ticket_num,
        user_id=user_id,
        order_id=order_id,
        issue=issue,
        status="OPEN"
    )

    # =====================================================
    # STEP 6: Respond to user
    # =====================================================
    state["messages"].append(
        AIMessage(
            content=(
                "🎫 **Support Ticket Created Successfully!**\n\n"
                f"🆔 Order ID: {order_id}\n"
                f"🎫 Ticket Number: **{ticket_num}**\n\n"
                f"📝 Issue: {issue}\n\n"
                "Our support team will review your request and get back to you soon."
            )
        )
    )

    return state

