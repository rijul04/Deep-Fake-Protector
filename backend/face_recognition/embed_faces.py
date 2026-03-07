import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model

# Load ArcFace only
# app = FaceAnalysis(allowed_modules=['detection', 'recognition']) # detection needs to be loaded i think but will only use the recog/arcface part
app = get_model("../../.insightface/models/model.onnx") # downloaded arc face model named after model
# app.prepare(ctx_id=0, det_size=(640, 640))
app.prepare(ctx_id=0)

def embed_faces(img: cv2.typing.MatLike):
    # ArcFace expects 112x112
    img = cv2.resize(img, (112, 112))
    
    embedding = app.get_feat(img)
    # breakpoint()
    
    # if len(faces) == 0:
    #     return None
    
    # embedding = faces[0].embedding  # 512-dim numpy array
    # if len(faces) == 0:
    #     return None

    if embedding is None:
        return None
    
    return embedding