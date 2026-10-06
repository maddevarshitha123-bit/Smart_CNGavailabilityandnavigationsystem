"""Create tables, load sample stations and create the first admin.

Run from project root:  python scripts/init_db.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mysql.connector
import config
from utils.auth import hash_password, validate_password


def run_sql_file(cursor, path):
    text = path.read_text(encoding="utf-8")
    for stmt in text.split(";"):
        lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
        stmt = "\n".join(lines).strip()
        if stmt:
            cursor.execute(stmt)


def main():
    conn = mysql.connector.connect(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD)
    cur = conn.cursor()
    run_sql_file(cur, config.SCHEMA_PATH)
    cur.execute(f"USE {config.DB_NAME}")
    cur.execute("SELECT COUNT(*) FROM stations")
    if cur.fetchone()[0] == 0:
        run_sql_file(cur, config.SAMPLE_DATA_PATH)
        print("Sample stations loaded.")
    email = os.getenv("ADMIN_EMAIL", "admin@example.com").lower()
    pw = os.getenv("ADMIN_PASSWORD", "")
    cur.execute("SELECT 1 FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        print("Admin already exists.")
    elif validate_password(pw):
        print("ADMIN_PASSWORD in .env is too weak (need 8+ chars, upper, lower, digit, special). Admin not created.")
    else:
        cur.execute("INSERT INTO users (name,email,password_hash,role) VALUES (%s,%s,%s,'admin')",
                    ("Administrator", email, hash_password(pw)))
        print(f"Admin created: {email}")
    conn.commit(); conn.close()
    print("Database ready.")


if __name__ == "__main__":
    main()
