from backend.face_recognition.detect_faces import detect_faces
import os
import cv2
from tqdm.auto import tqdm


from pathlib import Path

HERE = Path(__file__).resolve().parent

pbar = tqdm(os.listdir(f"{HERE}/data/frames/real/"), leave=False)

for i, frame in enumerate(pbar):
    pbar.set_description(desc=f"Frames {i}/{len(os.listdir(f"{HERE}/data/frames/real/"))}")

    img = cv2.imread(f"{HERE}/data/frames/real/{frame}")
    
    if img is None:
        continue

    faces_images = detect_faces(img=img)

   

    for j, face_image in enumerate(faces_images):
        try:
            cv2.imwrite(f"{HERE}/data/faces/real/{frame}_{i}_face_{j}.jpg", face_image)
        except:
            print("errorHere")
            print(face_image)

print("Done Real onto Fake")

pbar = tqdm(os.listdir(f"{HERE}/data/frames/fake/"), leave=False)

for i, frame in enumerate(pbar):
    pbar.set_description(desc=f"Frames {i}/{len(os.listdir(f"{HERE}/data/frames/fake/"))}")

    img = cv2.imread(f"{HERE}/data/frames/fake/{frame}")

    if img is None:
        continue

    faces_images = detect_faces(img=img)

    for j, face_image in enumerate(faces_images):
        cv2.imwrite(f"{HERE}/data/faces/fake/{frame}_{i}_face_{j}.jpg", face_image)

