# Deep-Fake-Protector

This is for my University undergradguate project at Queen Mary's University of London (QMUL)

The Basis of this project is a mix of Computer Vision, Image Processing and Web Development + One Shot AI face creation

It is to spot deep fakes using a past trained data set + also let users send in their own photos that they would like to be soley private. So when a user or someone using the exposed api sends their own photo to us the outcome is to return an image with blured faces and meta data if any deepfake detection (past a threshold) or a users face that they have sent in is detected.

One Shot AI face creation will be used so the user only will need to send in a certain amount of pictures, and then will use the technology to create many other versions of their face hopefully to make it easier to catch if the face is similar.

One Shot face Creation or Recognition not currently sure about it.


**Info:**
Requirements.txt will contain all the packages needed to be installed.


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
│ EFFICIENTNET V2 │     │       ARCFACE        │
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
| Deepfake classifier | EfficientNet V2 (PyTorch) | Classifies faces as real or manipulated |
| Training dataset | FaceForensics++ | Labelled real/fake face data for fine-tuning |
| Explainability | Grad-CAM | Heatmaps showing which regions triggered detection |
| Face embedding | ArcFace (InsightFace) | Converts faces into 512-dim identity vectors |
| Opt-out matching | Cosine Similarity (custom) | Compares embeddings against opt-out database |
| Face blurring | OpenCV | Applies blur to matched faces in output image |


### Things that I can write about in report:
- Compare why Retina Face instead of other versions like YOLO (face trained version) or the older MTCNN face detection
- Compare Why ArcFace instead of other versions like DeepFace or the older version FaceNet
- Why EfficientNEt instead of training model from scratch or other methods
- EfficientNet vs EfficientNet v2
- What model version of EfficientNet am using and why
- Why train using FaceForensics++
- Why store images as jpg and say not png for deep fake training dataset
- WHy certain things used in EfficientNet like what type of optimizer and loss algorithm
- THings added to the EfficientNet Tuning file to make it quicker / more efificient which in turn lets me use better models such as M instead of S EfficientNet
- How FaceForensics seems to generally use older pipelines for deep faking so more obvious in the sense of more artifacts and so on so is fine for baseline but will need to change it and can compare versions and data sets and so on
- Using croped face images or full iamges for training and  why
- Different Blur methods (if my method better than generic ones like np/cv2 ones)
- Need to understand how the face embeddings work
- Need to add normalisation/allignment for the face embeddings
- Add Tests

**Would Like to try manuualy code all of these things but for now use pre build**


### For training efficientNet for detecting deepfaked images
1) Installed cuda tools (specific needed ones as wsl2 was having issues with some of them)
2) installed pytorch
3) Went through pytorch tutorials about it where htye have the link to the paper of EfficientNet too
4) Watched https://www.youtube.com/watch?v=fR_0o25kigM&list=PLYjC48VOfl4nAw2-_lgmqIYxxKGCbsoJq&index=2
5) Tuned on data from FaceForensics++: https://github.com/ondyari/FaceForensics which first had to download from there data set after requesting access, they sent a script which can be seen in ./download_faceforensics.py which downloaded from EU2 server, where downloading the original and deepfakes dataset from it, comes as video so need to convert to images which I did though extract_frames.py
6) Tuning using EfficientNet_Tuning.py uses EfficientNetv2-M
7) Was being very slow so had to change things like change models to s version from m and edit amount of ram / processes wsl2 could access
8) Need To improve the Tuning as things such as validation step was not added
9) Currently gives wrong answers for the ones i make from online tools
10) If possible also use face2face dataset from faceforensics too as transfers facial expressions from one face to another
11) Maybe for training and evaluation need to use something that grabs just the face, unless whole image is usefull need to research!!!!! (Step 10 from pdf file plot confusion matrix and so on of current modedl and future ones)
12) Have just now used RetinaFace to take the faces of people from the frames which is to be trained for next model for deep fake analysis

<!-- Setting Up FastAPI -->
1) Setting up to get to work with DeepFakeAnalysis
2) Setting up basic version just a get endpoint with no protection or anything special

<!-- Setting up frontend -->
1) next isntall, kubb install, and other things from kubb
2) designing frontend design using figma
3) Using Lucide React for icons
4) Using FilePond for form designs to look better / Using amplify fo rfile upload component

<!-- Setting up retina face -->
1) Using Insight face as has both RetinaFacec and ArcFace
2) Has info of training your own models look into this if get to a point of doing from scratch
3) Using RetinaFace for predicting deepfake even wioth version 0 has increased acuracy



Going to see if after Efficient Net I can just directly blur the images using openCV2


<!-- Setting up blurring -->
1) Custom making blurring using box kernal
2) did through using 3 x 3 kernal but didnt want to make kernal larger so did downscale/upscale hack to try blurr it a lot more efficiently and i think (am not sure) means much harder to revert into the face before
3) Need to fix

<!-- Setting up ArcFace -->
1) Identity Vectors to be stored so will use SQLITE for now but make sure to get dev ready stuff so use an actual cloud storage platform
2) set up file "database.py" for Identity_Vector model to hold embeddings
3) set up embed_faces.py to use face_recog from insight face which will return face embeddings
4) Need to add normalisation/allignment for the face embeddings