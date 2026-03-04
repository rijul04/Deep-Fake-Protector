from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel
from deep_fake_analysis.predict import predictv2

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

class Prediction():
    prediction: Literal["REAL", "FAKE"]
    confidens: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


# Source - https://stackoverflow.com/a/68287488
# Posted by fchancel
# Retrieved 2026-03-04, License - CC BY-SA 4.0

from fastapi import FastAPI, File, UploadFile

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    prediction = predictv2(file.file)
    return {"filename": file.filename, "prediction": prediction}

