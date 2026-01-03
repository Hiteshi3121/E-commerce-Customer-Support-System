#-------faq_agent.py-------
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from backend.rag.tools import company_info_tool
from backend.graph.state import get_last_human_message


llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)


def faq_llm(state):
    user_question = get_last_human_message(state["messages"])

    # ---- Step 1: Retrieve from vector DB ----
    tool_result = company_info_tool.invoke(user_question)

    if not tool_result.strip():
        state["messages"].append(
            AIMessage(content="I'm sorry, I don't have that information right now.")
        )
        return state

    # ---- Step 2: FORCE summarization ----
    messages = [
        SystemMessage(
            content=(
                "You are NovaCart's AI customer support assistant.\n"
                "You can answer questions about the company ONLY using the tool `company_info_tool`.\n"
                "read the pdf content provided carefully to understand and then answer\n"
                "Generate a concise and be friendly to the user's question.\n"
                "If the answer is not present in the context, tell the user politly that this information is not public. or not available in the document. and stop"
                "Do NOT guess."

                "Rules:"
                "- If the user asks about company info, policies, products, or services, you MUST call `company_info_tool`.\n"
                "- Do NOT answer from your own knowledge."
                "- If information is not found, say you don't know."
                "- Do not mention the document content verbatim, summarize it in a friendly way."
                "- Keep the answer under 2-3 lines."
                "- Do not mention that you are an AI model, and the tools used."
                "- give a structure answer."
            )
        ),
        HumanMessage(
            content=f"""
            User question:
            {user_question}

            Information for reference (do NOT copy directly):
            {tool_result}
            

            Final answer to the customer:
            """
        ),
    ]

    final_response = llm.invoke(messages)

    state["messages"].append(
        AIMessage(content=final_response.content)
    )

    return state



#---------------old simple FAQ agent----------------
# from langchain_groq import ChatGroq
# import os
# from langchain_core.messages import SystemMessage, AIMessage
# from backend.rag.tools import company_info_tool
# from backend.graph.state import ConversationState
# from dotenv import load_dotenv
# load_dotenv()

# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     temperature=0.4
# ).bind_tools([company_info_tool])

# def faq_llm(state: ConversationState) -> ConversationState:
#     """Main LLM call that handles the customer and AI assistant conversation. Summarize the tool output into a short, friendly answer"""
        
#     system_prompt = """
#             You are NovaCart's AI customer support assistant.

#             You can answer questions about the company
#             ONLY using the tool `company_info_tool`.

#             After receiving tool results:
#             - Summarize the tool output in under 2-3 line, and answer friendly
#             - Do NOT repeat the document verbatim
#             - Use simple, spoken language

#             Rules:
#             - If the user asks about company info, policies, products, or services,
#             you MUST call `company_info_tool`.
#             - Do NOT answer from your own knowledge.
#             - If the tool returns no information, say:
#             "I'm sorry, I don't have that information right now."
#         """
    
#     msgs = [SystemMessage(content=system_prompt)] + state["messages"][-6:]
#     response = llm.invoke(msgs)

#     state["messages"].append(
#         AIMessage(content=response.content, tool_calls=response.tool_calls)
#     )
#     return state