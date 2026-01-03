# -----------------2 order_agent (LLM-powered agent) -----------------

from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
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
# TOOL: Create order
# =====================================================================
def create_order(user_id: str, product: str, quantity: int):
    order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"

    cursor.execute(
        """
        INSERT INTO orders (order_id, user_id, product_name, quantity, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, user_id, product, quantity, "PLACED")
    )
    conn.commit()

    return order_id


# =====================================================================
# AGENT: Order Agent
# =====================================================================
def order_agent(state: ConversationState) -> ConversationState:
    """
    LLM-powered Order Agent.
    """

    user_text = get_last_human_message(state["messages"])
    user_id = state["user_id"]

    # -------------------------------------------------
    # STEP 1: Agent reasoning — extract entities
    # -------------------------------------------------
    prompt = f"""
You are an order assistant for an e-commerce platform.

User message:
"{user_text}"

Extract:
- product name
- quantity (default to 1 if not mentioned)

If product is missing, set product to null.

Respond ONLY in JSON:
{{
  "product": null or "<product name>",
  "quantity": <number>
}}
"""
    try:
        response = llm.invoke(prompt).content.strip()
        data = eval(response)
    except Exception:
        data = {"product": None, "quantity": 1}

    product = data.get("product")
    quantity = data.get("quantity", 1)

    # -------------------------------------------------
    # STEP 2: Validate product (FIXED LOGIC)
    # -------------------------------------------------
    if (
        not product
        or not isinstance(product, str)
        or product.strip() == ""
        or product.lower() == "missing_product"
        or len(product.strip()) < 3
    ):
        state["messages"].append(
            AIMessage(
                content=(
                    "Sure 👍 Add the Product to your cart. \n\n"
                    "Example: *Order 2 wireless headphones*"
                )
            )
        )
        return state

    # -------------------------------------------------
    # STEP 3: Place order
    # -------------------------------------------------
    order_id = create_order(user_id, product, quantity)

    # -------------------------------------------------
    # STEP 4: Respond
    # -------------------------------------------------
    state["messages"].append(
        AIMessage(
            content=(
                "🎉 **YOUR ORDER PLACED SUCCESSFULLY** 🎉\n\n"
                f"🆔 Order ID: {order_id}\n"
                f"📦 Product: {product}\n"
                f"🔢 Quantity: {quantity}\n\n"
                "You can track or return this order anytime."
            )
        )
    )

    return state











#----------------------1.Order_agent Without LLM-------------------
# import os
# import uuid
# from langchain_core.messages import AIMessage
# from backend.db import get_connection
# from backend.graph.state import ConversationState
# from backend.graph.state import get_last_human_message
# from dotenv import load_dotenv
# load_dotenv()

# conn = get_connection()
# cursor = conn.cursor()

# def order_agent(state: ConversationState) -> ConversationState:

#     user_input = get_last_human_message(state["messages"])
#     product = user_input.replace("i want to place a order of", "").strip()
#     user_id = state["user_id"]
#     order_id = f"ORD-{uuid.uuid4().hex[:6]}"
#     product_id = f"PRD-{uuid.uuid4().hex[:6]}"

#     cursor.execute(
#         """
#         INSERT INTO orders (user_id, order_id, product_id, product_name, status)
#         VALUES (?, ?, ?, ?, ?)
#         """,
#         (
#             user_id,
#             order_id,
#             product_id,
#             product,
#             "PLACED"
#         )
#     )
#     conn.commit()
       
#     state["messages"].append(
#         AIMessage(content=f"✅ Your order for has been placed successfully.\n Your Order ID is {order_id}.")
#     )
#     return state
