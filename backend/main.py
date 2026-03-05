from typing import Literal

import cv2
from fastapi import FastAPI, Response
import numpy as np
from pydantic import BaseModel
from face_recognition.detect_faces import detect_faces, detect_faces_with_metadata
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

@app.post("/uploadfile/{retType}")
async def create_upload_file(retType: Literal["BASIC", "BLURRED"] = "BASIC", file: UploadFile = File(...)):

    # file gets sent as bytes so read and stored in contents then converted into a int8 array then decode converts into correct shape
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    cv2_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if retType == "BASIC":
        
        cv2_faces = detect_faces(cv2_img)

        faces = [cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB) for image_bgr in cv2_faces]

        prediction = predictv2(faces[0])
        return {"filename": file.filename, "prediction": prediction}
    elif retType == "BLURRED":
        
        faces_with_metadata = detect_faces_with_metadata(cv2_img)
        # breakpoint()

        faces = [{"image": cv2.cvtColor(fwmd["image"], cv2.COLOR_BGR2RGB), "metadata": fwmd["metadata"]} for fwmd in faces_with_metadata]

        # breakpoint()

        prediction = [{"prediction": predictv2(fwmd["image"]), "metadata": clean_metadata(fwmd["metadata"])} for fwmd in faces]

        print(faces[0]["image"])

        return prediction


# helper func to clean passed back meta data to allow the dict to become json seriable
def clean_metadata(metadata):
    cleaned_metadata = {}
    cleaned_metadata["bbox"] = metadata["bbox"].tolist()
    cleaned_metadata["kps"] = metadata["kps"].tolist()
    cleaned_metadata["det_score"] = float(metadata["det_score"])

    return cleaned_metadata


def blur(img: cv2.typing.MatLike):
    guassian_blur_filter = np.array(
        [[1, 2, 1],
        [2, 4, 2],
        [1, 2, 1]]
    )

    blurred_img = img

    for h in range(1, img.shape[0]-1):
        for w in range(1, img.shape[1]-1):
            top_left = img[h-1][w-1]
            top_middle = img[h-1][w]
            top_right = img[h-1][w+1]

            middle_left = img[h][w-1]
            middle_middle = img[h][w]
            middle_right = img[h][w+1]

            bottom_left = img[h+1][w-1]
            bottom_middle = img[h+1][w]
            bottom_right = img[h+1][w+1]

            specificImg = np.array = (
                [top_left, top_middle, top_right],
                [middle_left, middle_middle, middle_right],
                [bottom_left, bottom_middle, bottom_right]
            )

            multipliedImg = specificImg * guassian_blur_filter

            filtered_point = int(np.sum(multipliedImg) / guassian_blur_filter.size) # will possobily need normalising and so on for this

            blurred_img[h][w] = filtered_point
    
    return blurred_img



