import cv2
import os

from tqdm import tqdm

def extract_frames(video_path, output_folder, video_name, every_n=10):
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % every_n == 0:
            cv2.imwrite(f"{output_folder}/{video_name}_frame_{saved}.jpg", frame) # Saving as jpeg for mainly storage reasons altho maybe using png (lossless) maybe better? maybe test
            saved += 1
        frame_count += 1
    cap.release()

# Run on original videos
videos = os.listdir("./downloaded/Celeb-real/")[:500]
for video in tqdm(videos):
    extract_frames(
        f"./downloaded/Celeb-real/{video}",
        "data/real/",
        video
    )

# Run on deepfakes
videos = os.listdir("./downloaded/Celeb-synthesis/")[:500]
for video in tqdm(videos):
    extract_frames(
        f"./downloaded/Celeb-synthesis/{video}",
        "data/fake/",
        video
    )