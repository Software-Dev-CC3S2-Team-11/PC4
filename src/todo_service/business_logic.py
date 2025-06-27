import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from os import getenv

load_dotenv()

connection = psycopg2.connect(
    host=getenv("DB_HOST"),
    port=getenv("DB_PORT"),
    database=getenv("DB_NAME"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    cursor_factory=RealDictCursor
)

cursor = connection.cursor()


def get_tasks(username: str) -> list:
    try:
        cursor.execute("SELECT * FROM Task WHERE username = %s", (username,))
        return cursor.fetchall()
    except psycopg2.Error as e:
        print("Error al obtener las tareas", e)
        connection.rollback()
        return []


def add_task(username: str, title: str, description: str):
    try:
        cursor.execute(
            "INSERT INTO Task(username, title, description) VALUES (%s, %s, %s)",
            (username, title, description)
        )
        connection.commit()
    except psycopg2.Error as e:
        print("Error al agregar la tarea: ", e)
        connection.rollback()


def update_task(task_id: int, title: str, description: str):
    try:
        cursor.execute(
            "UPDATE Task SET title = %s, description = %s WHERE id = %s",
            (title, description, task_id)
        )
        connection.commit()
    except psycopg2.Error as e:
        print("Error al actualizar la tarea:", e)
        connection.rollback()


def remove_task(task_id: int):
    try:
        cursor.execute("DELETE FROM Task WHERE id = %s", (task_id,))
        connection.commit()
    except psycopg2.Error as e:
        print("Error al eliminar la tarea : ", e)
        connection.rollback()
