from typing import Annotated

import datetime
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager

class Identity_Vector(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    embedding: str = Field(index=True)
    created_at: datetime.datetime = Field(default_factory=datetime.utcnow, nullable=False)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # I Think yield means wait till shutdown so below it is shutdown events?

app = FastAPI(lifespan=lifespan)


# Below for CRUD

@app.post("/heroes/")
def create_identity_vector(identity_vector: Identity_Vector, session: SessionDep) -> Identity_Vector:
    session.add(identity_vector)
    session.commit()
    session.refresh(identity_vector)
    return identity_vector


@app.get("/heroes/")
def read_identity_vector(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Identity_Vector]:
    identity_vectors = session.exec(select(Identity_Vector).offset(offset).limit(limit)).all()
    return identity_vectors


@app.get("/identity_vector/{identity_vector_id}")
def read_identity_vector(identity_vector_id: int, session: SessionDep) -> Identity_Vector:
    identity_vector = session.get(Identity_Vector, identity_vector_id)
    if not identity_vector:
        raise HTTPException(status_code=404, detail="identity_vector not found")
    return identity_vector


@app.delete("/identity_vectors/{identity_vector_id}")
def delete_identity_vector(identity_vector_id: int, session: SessionDep):
    identity_vector = session.get(Identity_Vector, identity_vector_id)
    if not identity_vector:
        raise HTTPException(status_code=404, detail="identity_vector not found")
    session.delete(identity_vector)
    session.commit()
    return {"ok": True}