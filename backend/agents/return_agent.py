# -----------------4 return agent (llm and tools)-------------------

from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from backend.db import get_connection
from backend.graph.state import ConversationState, get_last_human_message
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Database connection (unchanged)
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
# TOOL 1: Validate order belongs to user
# =====================================================================
def validate_order(order_id: str, user_id: str):
    cursor.execute(
        "SELECT id, status FROM orders WHERE order_id=? AND user_id=?",  # 🔴 NEW: fetch status also
        (order_id, user_id)
    )
    return cursor.fetchone()

# =====================================================================
# TOOL 2 (Database tool): Create return request 
# =====================================================================
def create_return_request(user_id: str, order_id: str, reason: str):
    cursor.execute(
        """
        UPDATE orders
        SET status = ?, return_reason = ?
        WHERE order_id = ?
        """,
        ("RETURN_REQUESTED", reason, order_id)
    )

    cursor.execute(
        """
        INSERT INTO returns (user_id, order_id, reason, status)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, order_id, reason, "RETURN_REQUESTED")
    )
    conn.commit()


# =====================================================================
# AGENT: Return Agent with reasoning + tools
# =====================================================================
def return_agent(state: ConversationState) -> ConversationState:
    """
    LLM-powered Return Agent.
    - Uses LLM to extract return reason
    - Uses tools to validate order and create return
    - Prevents duplicate return requests
    """

    order_id = state.get("active_order_id")
    user_id = state["user_id"]
    user_text = get_last_human_message(state["messages"])

    # -------------------------------------------------
    # STEP 1: If order ID missing, ask user
    # -------------------------------------------------
    if not order_id:
        state["messages"].append(
            AIMessage(
                content=(
                    "Sure 👍 Please provide your ORDER ID to return your order.\n\n"
                    "*FORMAT: Return ORD-XXXX with reason*"
                )
            )
        )
        return state

    # -------------------------------------------------
    # STEP 2: Extract return reason using LLM
    # -------------------------------------------------
    prompt = f"""
You are a return assistant for an e-commerce platform.

User message:
"{user_text}"

Order ID: {order_id}

Task:
- Extract the return reason from the user's message.
- If no clear reason is mentioned, infer a generic reason like:
  "Customer requested return".

Respond with ONLY the return reason text.
"""
    return_reason = llm.invoke(prompt).content.strip()
    if not return_reason:
        return_reason = "Customer requested return"

    # -------------------------------------------------
    # STEP 3: Validate order using TOOL
    # -------------------------------------------------
    order = validate_order(order_id, user_id)

    if not order:
        state["messages"].append(
            AIMessage(content=f"❌ Order {order_id} not found or does not belong to you.")
        )
        return state

    order_db_id, order_status = order  # 🔴 NEW: unpack status

    # -------------------------------------------------
    # 🔴 STEP 3.1: CHECK IF RETURN ALREADY REQUESTED
    # -------------------------------------------------
    if order_status == "RETURN_REQUESTED":
        state["messages"].append(
            AIMessage(
                content=(
                    f"ℹ️ A return request for **Order {order_id}** has already been initiated.\n\n"
                    "Our team is currently processing it. You will be updated soon."
                )
            )
        )
        return state

    # -------------------------------------------------
    # STEP 4: Create return request
    # -------------------------------------------------
    create_return_request(user_id, order_id, return_reason)

    # -------------------------------------------------
    # STEP 5: Respond to user
    # -------------------------------------------------
    state["messages"].append(
        AIMessage(
            content=(
                "↩️ **Return Request Raised Successfully**\n\n"
                f"📦 Order ID: {order_id}\n"
                f"📝 Reason: {return_reason}\n\n"
                "Our team will process the return shortly."
            )
        )
    )

    return state








# #-----------------2 return agent (with updated returns table)----------------
# import re
# from langchain_core.messages import AIMessage
# from backend.db import get_connection
# from backend.graph.state import ConversationState
# from backend.graph.state import get_last_human_message


# conn = get_connection()
# cursor = conn.cursor()


# def return_agent(state: ConversationState) -> ConversationState:
#     """
#     Handles order return requests.
#     """

#     # ---- ADDED: use order ID resolved by router (do NOT re-parse intent) ----
#     order_id = state.get("active_order_id")

#     if not order_id:
#         state["messages"].append(
#             AIMessage(content="Sure👍,Please provide your ORDER ID to RETURN your order.\n\n *FORMATE: Return the (Order-ID)*")
#         )
#         return state

#     # ---- EXISTING LOGIC BELOW (UNCHANGED) ----
#     cursor.execute(
#         "SELECT id FROM orders WHERE order_id=? AND user_id=?",
#         (order_id, state["user_id"])
#     )
#     order = cursor.fetchone()

#     if not order:
#         state["messages"].append(
#             AIMessage(content=f"❌ Order {order_id} not found.")
#         )
#         return state

#     cursor.execute(
#         "UPDATE orders SET status=? WHERE order_id=?",
#         ("RETURN_REQUESTED", order_id)
#     )

#     return_reason = get_last_human_message(state["messages"])
#     cursor.execute(
#         """
#         INSERT INTO returns (user_id, order_id, reason, status)
#         VALUES (?, ?, ?, ?)
#         """,
#         (
#             state["user_id"],
#             order_id,
#             return_reason,
#             "RETURN_REQUESTED"
#         )
#     )
#     conn.commit()

#     state["messages"].append(
#         AIMessage(content=f"↩️ Return request raised successfully for order {order_id}.")
#     )

#     return state








#-------1 return_agent.PY code without RETURN TABLE update------------

# def return_agent(state: ConversationState) -> ConversationState:
#     last_msg = get_last_human_message(state["messages"])
#     text = last_msg
        
#     match = re.search(ORDER_ID_REGEX, text, re.IGNORECASE)
#     if not match:
#         state["messages"].append(
#             AIMessage(content="↩️ Please provide a valid order ID.")
#         )
#         return state

#     order_id = match.group(1)

#     cursor.execute(
#         "SELECT id FROM orders WHERE order_id=? AND user_id=?",
#         (order_id, state["user_id"])
#     )
#     if not cursor.fetchone():
#         state["messages"].append(
#             AIMessage(content=f"❌ Order {order_id} not found.")
#         )
#         return state

#     return_reason = re.sub(ORDER_ID_REGEX, "", text, flags=re.IGNORECASE).strip()
#     cursor.execute(
#         """
#         UPDATE orders
#         SET status='RETURN_REQUESTED',
#             return_reason=?,
#             return_date=CURRENT_TIMESTAMP
#         WHERE order_id=? AND user_id=?
#         """,
#         (return_reason, order_id, state["user_id"])
#     )
    
#     conn.commit()

#     state["messages"].append(
#         AIMessage(content=f"↩️ Return request raised for order {order_id}.")
#     )
#     return state
