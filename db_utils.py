import random
import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

random.seed(123)


class Chats(
    SQLModel, table=True
):  # table=True to tell SQLModel that this is a table model, i
    # l'impostazione default=None, è per dire che quando creo l oggetto non specifico l id
    # int | None  parlaa  python e all detor
    # il pezzo cin fiels si riferisce a sqlModel e pydantic
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    date_time: datetime = Field(default_factory=datetime.now)
    messages: List["Messages"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Messages(SQLModel, table=True):
    message_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # non posso avere chat_id come primary key perche deve essere unica
    # inoltre è sbagliayo fare
    # chat_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=False)
    # va fatto invece
    chat_id: uuid.UUID = Field(foreign_key="chats.id")
    role: str
    content: str
    date_time: datetime = Field(default_factory=datetime.now)
    # non ci vanno le parentesi in datetime.now perche lo devo avere come callable, altrimenti sarebbe
    # eseguito solo una volta ad inizio script per tutto il db


def get_messages_per_id(engine, chat_id: uuid.UUID) -> List[Messages]:
    with Session(engine) as session:
        statement = select(Messages).where(Messages.chat_id == chat_id)
        results = session.exec(statement)
        return results.all()


def get_all_chats(engine) -> List[Chats]:
    with Session(engine) as session:
        statement = select(Chats)
        results = session.exec(statement)
        return results.all()


def get_chat_by_id(engine, chat_id: uuid.UUID) -> Chats | None:
    with Session(engine) as session:
        chat = session.get(Chats, chat_id)
        return chat


def delete_chat(engine, chat_id: uuid.UUID):
    with Session(engine) as session:
        chat_to_delete = session.exec(
            select(Chats).where(Chats.id == chat_id)
        ).first()  # ottiene l'oggetto singolo oppure none

        if chat_to_delete:
            session.delete(chat_to_delete)
            session.commit()
            return True

        return False


def create_chat(engine, title: str) -> Chats:
    new_chat = Chats(title=title)
    with Session(engine) as session:
        session.add(new_chat)
        session.commit()
        session.refresh(new_chat)
    return new_chat


def add_message(engine, chat_id: uuid.UUID, role: str, content: str) -> Messages:
    new_message = Messages(chat_id=chat_id, role=role, content=content)

    with Session(engine) as session:
        session.add(new_message)
        session.commit()
        session.refresh(new_message)

    return new_message
