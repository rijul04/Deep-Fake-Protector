# Deep-Fake-Protector

This is for my University undergradguate project at Queen Mary's University of London (QMUL)

The Basis of this project is a mix of Computer Vision, Image Processing and Web Development + One Shot AI face creation

It is to spot deep fakes using a past trained data set + also let users send in their own photos that they would like to be soley private. So when a user or someone using the exposed api sends their own photo to us the outcome is to return an image with blured faces and meta data if any deepfake detection (past a threshold) or a users face that they have sent in is detected.

One Shot AI face creation will be used so the user only will need to send in a certain amount of pictures, and then will use the technology to create many other versions of their face hopefully to make it easier to catch if the face is similar.

One Shot face Creation or Recognition not currently sure about it,


General Pipeline:

## System Pipeline

### Main Processing Pipeline
```
┌─────────────────────────────────────────────┐
│           USER / PLATFORM                   │
│   Sends image or video via HTTP request     │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│                 FASTAPI                     │
│   Receives request, routes to pipeline,     │
│   returns processed image + metadata        │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│               RETINAFACE                    │
│   Detects all faces, returns bounding       │
│   boxes and cropped face regions            │
└─────────────────────┬───────────────────────┘
                      ↓
          ┌───────────┴───────────┐
          ↓                       ↓
┌─────────────────┐     ┌─────────────────────┐
│  EFFICIENTNET   │     │       ARCFACE        │
│                 │     │                      │
│ Classifies each │     │ Converts each face   │
│ face as real or │     │ into a 512-dim       │
│ deepfake        │     │ embedding vector     │
│                 │     │                      │
│ PyTorch,        │     │ InsightFace library  │
│ fine-tuned on   │     │                      │
│ FaceForensics++ │     └──────────┬───────────┘
└────────┬────────┘                ↓
         ↓                ┌─────────────────────┐
┌─────────────────┐       │  COSINE SIMILARITY  │
│    GRAD-CAM     │       │     PIPELINE        │
│                 │       │                     │
│ Generates       │       │ Compares embedding  │
│ heatmap showing │       │ against opt-out     │
│ which facial    │       │ database. Flags     │
│ regions flagged │       │ matches above       │
│ the model       │       │ threshold           │
│                 │       │                     │
│ pytorch-grad-   │       │ *** CUSTOM CODE *** │
│ cam library     │       │ NumPy               │
└────────┬────────┘       └──────────┬──────────┘
          └───────────┬───────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│                  OPENCV                     │
│   Blurs all opt-out matched faces,          │
│   composites Grad-CAM heatmap overlay       │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│              API RESPONSE                   │
│   Processed image + deepfake scores +       │
│   faces blurred + Grad-CAM heatmaps         │
└─────────────────────────────────────────────┘
```

---

### Opt-Out Registration Flow For User Uploading Their Face
```
┌─────────────────────────────────────────────┐
│   User uploads a single photo of their face │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│               RETINAFACE                    │
│         Detects and crops the face          │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│                  ARCFACE                    │
│       Generates 512-dim face embedding      │
└─────────────────────┬───────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│              OPT-OUT DATABASE               │
│   Embedding stored — all future images      │
│   processed through main pipeline will      │
│   check and blur this face if matched       │
└─────────────────────────────────────────────┘
```

---

### Technology Summary

| Component | Technology | Purpose |
|---|---|---|
| API layer | FastAPI | Exposes all functionality via REST endpoints |
| Face detection | RetinaFace (InsightFace) | Locates and crops all faces in an image |
| Deepfake classifier | EfficientNet (PyTorch) | Classifies faces as real or manipulated |
| Training dataset | FaceForensics++ | Labelled real/fake face data for fine-tuning |
| Explainability | Grad-CAM | Heatmaps showing which regions triggered detection |
| Face embedding | ArcFace (InsightFace) | Converts faces into 512-dim identity vectors |
| Opt-out matching | Cosine Similarity (custom) | Compares embeddings against opt-out database |
| Face blurring | OpenCV | Applies blur to matched faces in output image |



Compare why Retina Face instead of other versions like YOLO (face trained version) or the older MTCNN face detection
Compare Why ArcFace instead of other versions like DeepFace or the older version FaceNet


**Would Like to try manuualy code all of these things but for now use pre build**