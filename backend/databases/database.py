from typing import Annotated

from datetime import datetime
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

router = APIRouter()

class Identity_Vector(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    embedding: bytes = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# SessionDep = Annotated[Session, Depends(get_session)]


# Below for CRUD

def create_identity_vector(identity_vector: Identity_Vector) -> Identity_Vector:
    with Session(engine) as session:
        session.add(identity_vector)
        session.commit()
        session.refresh(identity_vector)
        
    return identity_vector


def read_identity_vector(
    offset: int = 0,
    limit: int = 100,
) -> list[Identity_Vector]:
    with Session(engine) as session:
        identity_vectors = session.exec(select(Identity_Vector).offset(offset).limit(limit)).all()
        return identity_vectors


def read_identity_vector_id(identity_vector_id: int) -> Identity_Vector:
    with Session(engine) as session:
        identity_vector = session.get(Identity_Vector, identity_vector_id)
        if not identity_vector:
            return None
    return identity_vector


def delete_identity_vector(identity_vector_id: int):
    with Session(engine) as session:
        identity_vector = session.get(Identity_Vector, identity_vector_id)
        if not identity_vector:
            return None

        session.delete(identity_vector)
        session.commit()

        return {"ok": True}