import cv2
import os

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
for video in os.listdir("original_sequences/youtube/c23/videos/"):
    extract_frames(
        f"original_sequences/youtube/c23/videos/{video}",
        "data/real/",
        video
    )

# Run on deepfakes
for video in os.listdir("manipulated_sequences/Deepfakes/c23/videos/"):
    extract_frames(
        f"manipulated_sequences/Deepfakes/c23/videos/{video}",
        "data/fake/",
        video
    )