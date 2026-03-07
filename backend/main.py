import base64
from typing import List, Literal

import cv2
from fastapi import FastAPI, Response
import numpy as np
from pydantic import BaseModel
from sqlmodel import Session
from face_recognition.embed_faces import embed_faces
from face_recognition.detect_faces import detect_faces, detect_faces_with_metadata
from deep_fake_analysis.predict import predictv2
from databases.database import Identity_Vector, create_db_and_tables, create_identity_vector, read_identity_vector, router

from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

    
app = FastAPI(lifespan=lifespan)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


    # I Think yield means wait till shutdown so below it is shutdown events?


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





@app.post("/person_face_image")
async def read_root(file: UploadFile = File(...)):

     # file gets sent as bytes so read and stored in contents then converted into a int8 array then decode converts into correct shape
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    cv2_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    cv2_faces = detect_faces(cv2_img)

    faces = [cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB) for image_bgr in cv2_faces]
    for face in faces:
        embedded_face = embed_faces(face)
        if embedded_face is None:
            return {"No Face"}
        
        identity_vector = Identity_Vector(embedding=embedded_face.tobytes())
        create_identity_vector(identity_vector)

    return {"Hello": "World"}





@app.post("/deepfake_image/{retType}")
async def create_upload_file(retType: Literal["BASIC", "BLURRED"] = "BASIC", file: UploadFile = File(...)):

    # file gets sent as bytes so read and stored in contents then converted into a int8 array then decode converts into correct shape
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    cv2_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if retType == "BASIC":
        
        cv2_faces = detect_faces(cv2_img)

        faces = [cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB) for image_bgr in cv2_faces]

        predictions = predictv2(faces[0])
        return {"filename": file.filename, "predictions": predictions}
    elif retType == "BLURRED":
        
        faces_with_metadata = detect_faces_with_metadata(cv2_img)

        faces = [{"image": cv2.cvtColor(fwmd["image"], cv2.COLOR_BGR2RGB), "metadata": fwmd["metadata"]} for fwmd in faces_with_metadata]

        predictions = [{"prediction": predictv2(fwmd["image"]), "metadata": clean_metadata(fwmd["metadata"])} for fwmd in faces]

        positive_predictions = [prediction for prediction in predictions if prediction["prediction"]["prediction"] == "FAKE"]

        # Add user_image embeddings here
        
        list_identitiy_vectors = [iv.embedding for iv in read_identity_vector()]
        identity_vectors_list = [{"image": embed_faces(face["image"]), "metadata": face["metadata"]} for face in faces] # add if statement here to check cosine similarity method or so on
        breakpoint()

        # User_image embeddings above

        img_copy = cv2_img.copy()
        for prediction in positive_predictions:
            img_copy = blur(img_copy, prediction["metadata"]["bbox"])

        _, encoded_img = cv2.imencode('.PNG', img_copy)

        encoded_img = base64.b64encode(encoded_img)

        return {"predictions": predictions, "image": encoded_img}
    




# helper func to clean passed back meta data to allow the dict to become json seriable
def clean_metadata(metadata):
    cleaned_metadata = {}
    cleaned_metadata["bbox"] = metadata["bbox"].tolist()
    cleaned_metadata["kps"] = metadata["kps"].tolist()
    cleaned_metadata["det_score"] = float(metadata["det_score"])

    return cleaned_metadata



# blurred stuff below need to fully fix but is custom made
def blur(img: cv2.typing.MatLike, bbox: List | None = None):
    guassian_blur_filter = np.array(
        [[1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]]
    )


    RESCALE_FACTOR = 20
    
    resized_img = cv2.resize(img, (img.shape[1] // RESCALE_FACTOR, img.shape[0] // RESCALE_FACTOR))
    blurred_img = np.zeros((resized_img.shape[0], resized_img.shape[1], resized_img.shape[2]), dtype=np.uint8) if bbox is not None else resized_img.copy()

    H_RANGE_START = int(bbox[1]) // RESCALE_FACTOR if bbox is not None else 1
    H_RANGE_END = int(bbox[3]) // RESCALE_FACTOR if bbox is not None else resized_img.shape[0]-1

    W_RANGE_START = int(bbox[0]) // RESCALE_FACTOR if bbox is not None else 1
    W_RANGE_END = int(bbox[2]) // RESCALE_FACTOR if bbox is not None else resized_img.shape[1]-1

    for h in range(H_RANGE_START, H_RANGE_END):
        for w in range(W_RANGE_START, W_RANGE_END):

            top_left = resized_img[h-1][w-1]
            top_middle = resized_img[h-1][w]
            top_right = resized_img[h-1][w+1]

            middle_left = resized_img[h][w-1]
            middle_middle = resized_img[h][w]
            middle_right = resized_img[h][w+1]

            bottom_left = resized_img[h+1][w-1]
            bottom_middle = resized_img[h+1][w]
            bottom_right = resized_img[h+1][w+1]

            specificImg = np.array(
                [[top_left, top_middle, top_right],
                [middle_left, middle_middle, middle_right],
                [bottom_left, bottom_middle, bottom_right]]
            )


            filtered_point = np.sum(specificImg * guassian_blur_filter[:, :, None], axis=(0,1)) / np.sum(guassian_blur_filter)

            blurred_img[h][w] = filtered_point
        
    upscaled_img = cv2.resize(blurred_img, (img.shape[1], img.shape[0]))
    

    if bbox is not None:
        img[int(bbox[1]): int(bbox[3]), int(bbox[0]): int(bbox[2])] = (0, 0, 0)

    ret_img = np.bitwise_or(img, upscaled_img)

    # doesnt fully work not doing how i like it make sure to look into this and fix

    return ret_img


