import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from business_logic import get_tasks, add_task, update_task, remove_task
from dotenv import load_dotenv
from os import getenv
from contextlib import asynccontextmanager
import db

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(lifespan=lifespan)

security = HTTPBearer()


SECRET_KEY = getenv("SECRET_KEY")


class Task(BaseModel):
    title: str
    description: str


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        print(credentials.credentials)
        payload = jwt.decode(credentials.credentials,
                             SECRET_KEY, algorithms=["HS256"])
        print("PAYLOAD:", payload)
        return payload["username"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


@app.get("/tasks")
def get_tasks_endoint(user: str = Depends(verify_token)):
    return get_tasks(user)


@app.post("/tasks")
def new_task_endpoint(task: Task, username: str = Depends(verify_token)):
    add_task(username=username, title=task.title, description=task.description)
    return {"message": "Tarea registrada"}


@app.put("/tasks/{task_id}")
def update_task_endpoint(task_id: int, task: Task,
                         user: str = Depends(verify_token)):

    update_task(task_id, task.title, task.description)
    return {"message": "Tarea actualizada"}


@app.delete("/tasks/{task_id}")
def remove_task_endpoint(task_id: int, user: str = Depends(verify_token)):
    remove_task(task_id)
    return {"message": "Tarea eliminada"}
