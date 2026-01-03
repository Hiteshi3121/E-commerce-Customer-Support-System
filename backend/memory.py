# memory.py
import sqlite3
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

MEMORY_DB = "memory.db"

def init_memory_db():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversation_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def save_memory(session_id: str, messages):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    for msg in messages:
        role = "human" if isinstance(msg, HumanMessage) else "ai"
        cursor.execute(
            "INSERT INTO conversation_memory (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, msg.content),
        )

    conn.commit()
    conn.close()

def load_memory(session_id: str, limit: int = 6):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content FROM conversation_memory
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (session_id, limit))

    rows = cursor.fetchall()
    conn.close()

    messages = []
    for role, content in reversed(rows):
        if role == "human":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))

    return messages
