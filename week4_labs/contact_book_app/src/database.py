# database.py
import sqlite3
def init_db():
    """Initializes the database and creates the contacts table if it doesn't exist."""
    conn = sqlite3.connect('contacts.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT
        )
    ''')
    conn.commit()
    return conn

def add_contact_db(conn, name, phone, email):
    """Adds a new contact to the database."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)",
        (name, phone, email)
    )
    conn.commit()

def get_all_contacts_db(db_conn, search: str = "", filter_by: str = "all"):
    cursor = db_conn.cursor()
    try:
        if search:
            like_term = f"%{search}%"
            if filter_by == "name":
                cursor.execute("SELECT id, name, phone, email FROM contacts WHERE name LIKE ?", (like_term,))
            elif filter_by == "phone":
                cursor.execute("SELECT id, name, phone, email FROM contacts WHERE phone LIKE ?", (like_term,))
            elif filter_by == "email":
                cursor.execute("SELECT id, name, phone, email FROM contacts WHERE email LIKE ?", (like_term,))
            else:
                cursor.execute(
                    "SELECT id, name, phone, email FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?",
                    (like_term, like_term, like_term)
                )
        else:
            cursor.execute("SELECT id, name, phone, email FROM contacts")
        return cursor.fetchall()
    finally:
        cursor.close()

def update_contact_db(conn, contact_id, name, phone, email):
    """Updates an existing contact in the database."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?",
        (name, phone, email, contact_id)
    )
    conn.commit()

def delete_contact_db(conn, contact_id):
    """Deletes a contact from the database."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
