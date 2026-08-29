import psycopg
from uuid import uuid4
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg.connect(f"host={os.getenv("HOST_DATABASE")} port={os.getenv("PORT_DATABASE")} dbname={os.getenv("DATABASE_NAME")} user={os.getenv("DATABASE_USER")} password={os.getenv("DATABASE_PASSWORD")}")

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
    return id

def get_history_messages():
    with current_db() as cur:
        cur.execute("SELECT role, message, datetime FROM messages ORDER BY datetime DESC LIMIT 5")
        rows = cur.fetchall()
        return [{"role": row[0], "message": row[1], "datetime": row[2]} for row in rows]


def insert_image(public_url, filename: str, message_id:str, ):
    id = uuid4()
    with current_db() as cur:
        cur.execute(
            "INSERT INTO images (id, public_url, filename, message_id) VALUES (%s, %s, %s, %s)",
            (str(id), public_url, filename, message_id)
        )
        conn.commit()
    return id

def get_images(image_id):
    with current_db() as cur:
        cur.execute("SELECT public_url, filename FROM images WHERE id = %s", (image_id,))
        rows = cur.fetchone()
        return {"public_url": rows[0], "filename": rows[1]}