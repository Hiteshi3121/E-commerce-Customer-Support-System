# backend/db.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "orders.db")


# -------------------------------------------------
# Users table
# -------------------------------------------------
def init_users_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# Main DB initialization (SINGLE SOURCE OF TRUTH)
# -------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # -----------------------------
    # Orders table (existing schema)
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        order_id TEXT UNIQUE,
        product_id TEXT,
        product_name TEXT,
        status TEXT,
        return_reason TEXT,
        return_date TIMESTAMP,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -----------------------------
    # 🔄 Migration: add quantity column
    # -----------------------------
    cursor.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in cursor.fetchall()]

    if "quantity" not in columns:
        cursor.execute(
            "ALTER TABLE orders ADD COLUMN quantity INTEGER DEFAULT 1"
        )

    # -----------------------------
    # 🔄 Migration: add payment_mode column
    # -----------------------------
    if "payment_mode" not in columns:
        cursor.execute(
            "ALTER TABLE orders ADD COLUMN payment_mode TEXT DEFAULT 'COD'"
        )

    # -----------------------------
    # Support tickets table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_num TEXT,
        user_id TEXT,
        order_id TEXT,
        issue TEXT,
        status TEXT,
        ticket_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -----------------------------
    # Returns table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS returns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        order_id TEXT,
        reason TEXT,
        status TEXT,
        return_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

    # Initialize users table
    init_users_db()


# -------------------------------------------------
# DB connection helper
# -------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)




# db.py
# import sqlite3
# import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB_NAME = os.path.join(BASE_DIR, "orders.db")

# def init_users_db():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         user_id TEXT PRIMARY KEY,
#         username TEXT UNIQUE,
#         password TEXT
#     )
#     """)

#     conn.commit()
#     conn.close()


# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS orders (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         user_id TEXT,
#         order_id TEXT,
#         product_id TEXT,
#         product_name TEXT,
#         status TEXT,
#         return_reason TEXT,
#         return_date TIMESTAMP,
#         order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
#     """)

#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS support_tickets (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         ticket_num TEXT,
#         user_id TEXT,
#         order_id TEXT,
#         issue TEXT,
#         status TEXT,
#         ticket_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
#     """)

#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS returns (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         user_id TEXT,
#         order_id TEXT,
#         reason TEXT,
#         status TEXT,
#         return_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
#     """)

#     conn.commit()
#     conn.close()

#     init_users_db()

# def get_connection():
#     return sqlite3.connect(DB_NAME, check_same_thread=False)

