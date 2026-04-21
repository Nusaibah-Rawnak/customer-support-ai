import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "customers.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_customer_by_name(name: str) -> str:
    """Get customer profile by name (partial match supported)."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM customers WHERE name LIKE ?", (f"%{name}%",)
    )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return json.dumps({"error": f"No customer found with name matching '{name}'"})
    return json.dumps([dict(row) for row in rows])


def get_tickets_by_customer_name(name: str) -> str:
    """Get all support tickets for a customer by name."""
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT t.id, t.subject, t.description, t.status, t.priority,
               t.created_date, t.resolved_date, c.name as customer_name
        FROM support_tickets t
        JOIN customers c ON t.customer_id = c.id
        WHERE c.name LIKE ?
        ORDER BY t.created_date DESC
    """, (f"%{name}%",))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return json.dumps({"error": f"No tickets found for customer matching '{name}'"})
    return json.dumps([dict(row) for row in rows])


def get_open_tickets() -> str:
    """Get all open or in-progress support tickets."""
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT t.id, t.subject, t.status, t.priority, t.created_date,
               c.name as customer_name
        FROM support_tickets t
        JOIN customers c ON t.customer_id = c.id
        WHERE t.status IN ('Open', 'In Progress')
        ORDER BY t.priority DESC, t.created_date ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return json.dumps({"message": "No open tickets found."})
    return json.dumps([dict(row) for row in rows])


def get_all_customers() -> str:
    """Get a summary list of all customers."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT id, name, email, plan, country, joined_date FROM customers ORDER BY name"
    )
    rows = cursor.fetchall()
    conn.close()
    return json.dumps([dict(row) for row in rows])


def run_sql_query(query: str) -> str:
    """Run a read-only SQL SELECT query against the database."""
    query = query.strip()
    if not query.lower().startswith("select"):
        return json.dumps({"error": "Only SELECT queries are allowed."})
    try:
        conn = get_db_connection()
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return json.dumps([dict(row) for row in rows])
    except Exception as e:
        return json.dumps({"error": str(e)})