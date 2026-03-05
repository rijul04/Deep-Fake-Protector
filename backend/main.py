from typing import Literal

import cv2
from fastapi import FastAPI
import numpy as np
from pydantic import BaseModel
from face_recognition.detect_faces import detect_faces
from deep_fake_analysis.predict import predictv2
import torchvision.transforms as transforms

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

    # file gets sent as bytes so read and stored in contents then converted into a int8 array then decode converts into correct shape
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    cv2_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    cv2_faces = detect_faces(cv2_img)


    faces = [cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB) for image_bgr in cv2_faces]

    # breakpoint()

    prediction = predictv2(faces[0])
    return {"filename": file.filename, "prediction": prediction}

