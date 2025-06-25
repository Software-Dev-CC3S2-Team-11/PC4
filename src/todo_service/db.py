import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from os import getenv

load_dotenv()


def init_db():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                DROP TABLE task;
                CREATE TABLE task (
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    username TEXT NOT NULL
                );
            """)
            conn.commit()
        conn.close()
        print("Tabla 'tasks' creada")
    except Exception as e:
        print("Error al crear la tabla:", e)


def get_connection():
    return psycopg2.connect(
        host=getenv("DB_HOST"),
        port=getenv("DB_PORT"),
        database=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )
