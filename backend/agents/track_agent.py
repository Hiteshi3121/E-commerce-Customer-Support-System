from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from backend.db import get_connection
from backend.graph.state import ConversationState, get_last_human_message
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
# TOOL: Fetch order status
# =====================================================================
def get_order_status(order_id: str, user_id: str):
    cursor.execute(
        """
        SELECT status, product_name, quantity, order_date
        FROM orders
        WHERE order_id = ? AND user_id = ?
        """,
        (order_id, user_id)
    )
    return cursor.fetchone()


# Helper function: Add business days (Mon–Fri)
def add_business_days(start_date: datetime, days: int) -> datetime:
    """
    Add business days (Mon–Fri) to a date.
    """
    current_date = start_date
    added_days = 0

    while added_days < days:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # Monday–Friday
            added_days += 1

    return current_date


# =====================================================================
# AGENT: Track Agent
# =====================================================================
def track_agent(state: ConversationState) -> ConversationState:
    """
    LLM-powered Track Agent.
    - Uses router-provided order_id
    - Fetches order details from DB
    - Computes delivery ETA logically (5–7 business days)
    - Uses LLM only for friendly explanation
    """

    user_id = state["user_id"]
    order_id = state.get("active_order_id")

    # -------------------------------------------------
    # STEP 1: Ensure order ID exists
    # -------------------------------------------------
    if not order_id:
        state["messages"].append(
            AIMessage(
                content=(
                    "Sure 🙂 Please share your ORDER ID so I can track your order.\n\n"
                    "*Example: Track ORD-XXXX*"
                )
            )
        )
        return state

    # -------------------------------------------------
    # STEP 2: Fetch order details
    # -------------------------------------------------
    order = get_order_status(order_id, user_id)

    if not order:
        state["messages"].append(
            AIMessage(
                content=f"❌ I couldn’t find any order with ID **{order_id}** linked to your account."
            )
        )
        return state

    status, product_name, quantity, order_date = order

    # -------------------------------------------------
    # STEP 3: Parse order date
    # -------------------------------------------------
    order_datetime = datetime.fromisoformat(order_date)
    order_date_str = order_datetime.strftime("%d %b %Y")

    # -------------------------------------------------
    # STEP 4: Compute estimated delivery (5–7 business days)
    # -------------------------------------------------
    estimated_start = add_business_days(order_datetime, 5)
    estimated_end = add_business_days(order_datetime, 7)

    estimated_delivery_str = (
        f"{estimated_start.strftime('%d %b %Y')} – "
        f"{estimated_end.strftime('%d %b %Y')}"
    )

    # -------------------------------------------------
    # STEP 5: LLM explanation (language only)
    # -------------------------------------------------
    explanation_prompt = f"""
You are a customer support assistant.

Order details:
- Order ID: {order_id}
- Product: {product_name}
- Quantity: {quantity}
- Order Date: {order_date_str}
- Status: {status}
- Estimated Delivery Window: {estimated_delivery_str}

Explain the order status clearly and reassuringly.
Mention the estimated delivery window.
Keep it short and friendly.
"""

    try:
        status_explanation = llm.invoke(explanation_prompt).content.strip()
    except Exception:
        status_explanation = (
            f"Your order is currently **{status}** and is expected to arrive "
            f"between {estimated_delivery_str}."
        )

    # -------------------------------------------------
    # STEP 6: Respond to user
    # -------------------------------------------------
    state["messages"].append(
        AIMessage(
            content=(
                f"📦 **STATUS OF YOUR ORDER**\n\n"
                f"🆔 Order ID: {order_id}\n\n"
                f"🛍️ Product: {product_name}\n\n"
                f"🔢 Quantity: {quantity}\n\n"
                f"📅 Order Placed On: {order_date_str}\n\n"
                f"📍 Status: **{status}**\n\n"
                f"🚚 Estimated Delivery: **{estimated_delivery_str}**"
                
            )
        )
    )

    return state
