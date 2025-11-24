import os
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, text, exc
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


"logging"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

"models"
class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid64)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)

"data access layer for operating user info"
class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create_user(
        self, name: str, surname: str, email: str) -> User:
        new_user = User(
            name=name, 
            surname=surname,
            email=email,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

app = FastAPI()

@app.get("/users")
def read_root(name: str, age: int):
    return {"name" : f"hi, {name}", "age" : f"wow, u r {age}"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/notfound", status_code=status.HTTP_404_NOT_FOUND)
def notfound():
    return {"message" : "not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host ="0.0.0.0", port=8000)