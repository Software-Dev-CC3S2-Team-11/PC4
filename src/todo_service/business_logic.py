import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from os import getenv
from fastapi import HTTPException

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
        cursor.execute(
            "SELECT id,title,description FROM Task WHERE username = %s", (username,))
        return cursor.fetchall()
    except psycopg2.Error as e:
        print("Error al obtener las tareas", e)
        connection.rollback()
        raise HTTPException(
            500, detail='Surgió un error en la base de datos al obtener las tareas')


def add_task(username: str, title: str, description: str):
    try:
        cursor.execute(
            "INSERT INTO Task(username, title, description) VALUES (%s, %s, %s)",
            (username, title, description)
        )
        connection.commit()

    except psycopg2.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(
            404, detail='Ya existe una tarea con ese titulo, eliga otro')

    except psycopg2.Error as e:
        print("Error al agregar la tarea: ", e)
        connection.rollback()
        raise HTTPException(
            500, detail='Surgió un error en la base de datos durante la inserción')


def update_task(task_id: int, title: str, description: str):
    try:
        cursor.execute(
            "UPDATE Task SET title = %s, description = %s WHERE id = %s",
            (title, description, task_id)
        )
        connection.commit()

        if (cursor.rowcount == 0):
            raise HTTPException(404, detail=f'No hay una tarea con el id {id}')

    except psycopg2.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(
            404, detail='Ya existe una tarea con ese título, eliga otro')
    except psycopg2.Error as e:
        connection.rollback()
        print("Error al actualizar la tarea:", e)
        raise HTTPException(
            500, detail='Surgió un error en la base de datos durante la actualizacion')


def remove_task(task_id: int):
    try:
        cursor.execute("DELETE FROM Task WHERE id = %s", (task_id,))
        connection.commit()

        if (cursor.rowcount == 0):
            raise HTTPException(
                404, detail=f'No existe una tarea con el id {task_id}')
    except psycopg2.Error as e:
        print("Error al eliminar la tarea : ", e)
        connection.rollback()
        raise HTTPException(
            500, detail='Surgió un error en la base de datos durante la eliminación')
