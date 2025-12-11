import asyncio
import os
import random
import uuid
from enum import Enum
from typing import List

import pandas as pd
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, create_engine

# random.seed(123)
import db_utils as db
from agent import (
    exec_agent,
)


class Response(BaseModel):
    text: str


class ChatInfo(BaseModel):
    chat_id: str


class RoleMessage(str, Enum):
    USER = "user"
    AI = "ai"


class Message(BaseModel):
    role: RoleMessage
    content: str
    id: str


class ChatHistoryResponse(BaseModel):
    conversation: list[Message]


class MessageInput(BaseModel):
    input_data: str


app = FastAPI()


sqlite_file_name = "chat_bot.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)
SQLModel.metadata.create_all(engine)


@app.post("/chats/{chat_id}")
async def talk(chat_id: uuid.UUID, data: MessageInput) -> dict:
    out = exec_agent(data.input_data, chat_id, engine)
    # resp = out["content"]
    return out


@app.post("/chats")
def create_chat():
    random_title = random.randint(0, 1000)
    new_chat = db.create_chat(engine, title=f"Title_{random_title}")

    return new_chat


@app.get("/chats")
def list_all_chats():
    results = db.get_all_chats(engine)

    return results


#
#
@app.get("/chats/{chat_id}")
def read_chat(chat_id: uuid.UUID) -> List:
    chat_messages = db.get_messages_per_id(engine, chat_id)
    return chat_messages


#
##
##
@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: uuid.UUID) -> str:
    db.delete_chat(engine, chat_id)
    return f"Chat {chat_id} deleted."


#
async def fake_data_streamer():
    for i in range(10):
        yield b"some fake data"
        await asyncio.sleep(0.5)


@app.get("/stream")
async def prova_stream():
    return StreamingResponse(fake_data_streamer(), media_type="text/plain")


from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
    "utente1": {
        "username": "xxxx",
        "full_name": "xxxx xxxx",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


#
if __name__ == "__main___":
    uvicorn.run(app)
#
