import psycopg
from uuid import uuid4
from datetime import datetime
conn = psycopg.connect("host=localhost dbname=postgres user=postgres password=postgres")

def current_db():
    return conn.cursor()


def insert_message(role: str, message: str):
    id = uuid4()
    dateNow = datetime.now()
    with current_db() as cur:
        cur.execute(
            "INSERT INTO messages (id, role, message, datetime) VALUES (%s, %s, %s, %s)",
            (str(id), role, message, dateNow)
        )
        conn.commit()

def get_history_messages():
    with current_db() as cur:
        cur.execute("SELECT role, message, datetime FROM messages ORDER BY datetime DESC LIMIT 5")
        rows = cur.fetchall()
        return [{"role": row[0], "message": row[1], "datetime": row[2]} for row in rows]
