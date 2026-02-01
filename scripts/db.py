import sqlite3
import os

DB_NAME = "emails.db"

def init_db():
    """Creates the database and emails table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            sender TEXT,
            subject TEXT,
            body TEXT,
            category TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            summary TEXT,
            suggested_reply TEXT,
            is_phishing INTEGER DEFAULT 0,
            security_reason TEXT,
            is_newsletter INTEGER DEFAULT 0
        )
    ''')
    
    # Hackathon Migration: Try to add columns if they don't exist
    try:
        c.execute("ALTER TABLE emails ADD COLUMN summary TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        c.execute("ALTER TABLE emails ADD COLUMN suggested_reply TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE emails ADD COLUMN is_phishing INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE emails ADD COLUMN security_reason TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE emails ADD COLUMN is_newsletter INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

def save_email(email_data, category, summary="", suggested_reply="", is_phishing=0, security_reason="", is_newsletter=0):
    """Saves a processed email to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO emails (id, sender, subject, body, category, timestamp, summary, suggested_reply, is_phishing, security_reason, is_newsletter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_data["id"],
            email_data["from"],
            email_data["subject"],
            email_data["body"],
            category,
            email_data.get("date", ""),
            summary,
            suggested_reply,
            is_phishing,
            security_reason,
            is_newsletter
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Email already exists
        return False
    finally:
        conn.close()

def get_all_emails():
    """Fetches all emails for the dashboard."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, sender, subject, body, category, timestamp, summary, suggested_reply, is_phishing, security_reason, is_newsletter FROM emails ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    # Convert to list of dicts
    emails = []
    for row in rows:
        emails.append({
            "id": row[0],
            "from": row[1],
            "subject": row[2],
            "body": row[3],
            "category": row[4],
            "timestamp": row[5],
            "summary": row[6] if row[6] else "No summary available",
            "suggested_reply": row[7] if row[7] else "",
            "is_phishing": row[8] if row[8] is not None else 0,
            "security_reason": row[9] if row[9] else "",
            "is_newsletter": row[10] if row[10] is not None else 0
        })
    return emails
