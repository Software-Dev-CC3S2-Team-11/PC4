from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv

load_dotenv()

SECRET_KEY = getenv('SECRET_KEY')
ALGORITHM = getenv('ALGORITHM')

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(username: str):
    """
    Crea un token JWT con el email y el nombre de usuario del usuario
    """
    encode = {'username': username}
    expires = datetime.now() + timedelta(days=30)
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    """
    Verifica el token JWT y devuelve el payload si es válido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None