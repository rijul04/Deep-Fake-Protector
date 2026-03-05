import cv2
from insightface.app import FaceAnalysis


app = FaceAnalysis(allowed_modules=['detection'])
app.prepare(ctx_id=0, det_size=(640, 640))

# This will return the actual images
def detect_faces(img: cv2.typing.MatLike):
    
    

    faces = app.get(img)

    faces_list = []

    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)
        cropped_img = img[y1:y2, x1:x2]
        # cv2.imwrite(f"{rename}.jpg", cropped)
        if cropped_img.size == 0:
            continue
        faces_list.append(cropped_img)
    
    return faces_list

#  Make func that returns the whole meta data used for getting bbox data