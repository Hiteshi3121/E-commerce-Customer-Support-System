#------3 main.py (FastAPI) with active session correction-------
from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from pydantic import BaseModel

import uuid

from langchain_core.messages import HumanMessage

from backend.graph.workflow import create_workflow
from backend.db import init_db
from backend.memory import init_memory_db, save_memory
from backend.auth.auth_routes import router as auth_router


# ----------------------------------
# App Initialization
# ----------------------------------
app = FastAPI(title="NovaCart Backend")

app.include_router(auth_router)

init_db()
init_memory_db()

graph = create_workflow()

# ----------------------------------
# Models
# ----------------------------------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


# ----------------------------------
# Health
# ----------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ----------------------------------
# Start Chat Session
# ----------------------------------
@app.post("/chat/session/start")
def start_chat_session(user_id: str):
    """
    user_id comes from frontend AFTER login
    """

    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    
    # initialize memory for this conversation
    save_memory(session_id, [])

    return {"session_id": session_id}


# ----------------------------------
# Chat
# ----------------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, user_id: str, session_id: str        ):
    """
    user_id is provided implicitly by frontend (stored after login)
    session_id is resolved automatically
    """

    state = {
        "messages": [HumanMessage(content=req.message)],
        "intent": "",
        "user_id": user_id,
        "session_id": session_id
    }

    result = graph.invoke(state)

    reply = result["messages"][-1].content if result.get("messages") else ""

    return ChatResponse(
        response=reply,
        session_id=session_id
    )

#-------2 main.py (FastAPI) -------
# from dotenv import load_dotenv
# load_dotenv()

# import os
# from fastapi import FastAPI
# from pydantic import BaseModel

# import uuid

# from langchain_core.messages import HumanMessage

# from backend.graph.workflow import create_workflow
# from backend.db import init_db
# from backend.memory import init_memory_db, save_memory
# from backend.auth.auth_routes import router as auth_router


# # ----------------------------------
# # App Initialization
# # ----------------------------------
# app = FastAPI(title="NovaCart Backend")

# app.include_router(auth_router)

# init_db()
# init_memory_db()

# graph = create_workflow()

# # ----------------------------------
# # TEMP SESSION STORE (Prototype-safe)
# # ----------------------------------
# ACTIVE_SESSIONS = {}   # user_id -> session_id


# # ----------------------------------
# # Models
# # ----------------------------------
# class ChatRequest(BaseModel):
#     message: str


# class ChatResponse(BaseModel):
#     response: str
#     session_id: str


# # ----------------------------------
# # Health
# # ----------------------------------
# @app.get("/health")
# def health():
#     return {"status": "ok"}


# # ----------------------------------
# # Start Chat Session
# # ----------------------------------
# @app.post("/chat/session/start")
# def start_chat_session(user_id: str):
#     """
#     user_id comes from frontend AFTER login
#     """

#     session_id = f"sess_{uuid.uuid4().hex[:8]}"

#     ACTIVE_SESSIONS[user_id] = session_id #this maps user to session

#     # initialize memory for this conversation
#     save_memory(session_id, [])

#     return {"session_id": session_id}


# # ----------------------------------
# # Chat
# # ----------------------------------
# @app.post("/chat", response_model=ChatResponse)
# def chat(req: ChatRequest, user_id: str):
#     """
#     user_id is provided implicitly by frontend (stored after login)
#     session_id is resolved automatically
#     """

#     session_id = ACTIVE_SESSIONS.get(user_id)

#     if not session_id:
#         return ChatResponse(
#             response="❗ No active chat session. Please start a new chat.",
#             session_id=""
#         )

#     state = {
#         "messages": [HumanMessage(content=req.message)],
#         "intent": "",
#         "user_id": user_id,
#         "session_id": session_id
#     }

#     result = graph.invoke(state)

#     reply = result["messages"][-1].content if result.get("messages") else ""

#     return ChatResponse(
#         response=reply,
#         session_id=session_id
#     )
