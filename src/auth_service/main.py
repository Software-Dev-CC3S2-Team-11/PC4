from fastapi import FastAPI
from routes import router
import uvicorn
import db

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
def startup():
    db.init_db()