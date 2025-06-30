from fastapi import HTTPException
from pathlib import Path
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette import status
from fastapi.templating import Jinja2Templates
import psycopg2
from db import get_connection
from business_logic import bcrypt_context, create_access_token

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(request: Request,
                        username: str = Form(...),
                        email: str = Form(...),
                        password: str = Form(...)):
    """
    Crea un nuevo usuario en la base de datos
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Username already exists")
            
            hashed_password = bcrypt_context.hash(password)
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username,email,hashed_password))
            conn.commit()
        conn.close()

        return {"message": "User registered successfully"}

    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Inicia sesión con el usuario y contraseña proporcionados.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
        conn.close()

        if row and bcrypt_context.verify(password, row["password"]):
            return {"token": create_access_token(username)}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_users(request: Request):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT username, email FROM users")
            users = cur.fetchall()
        conn.close()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))