import cv2
import torch
from torchvision import transforms, models
from torch import nn
from PIL import Image

# Need to change model used and so on to make sure it matches the correct model i used for training set


from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "efficientnet_v2m_deepfake_v2.pt"   # adjust name/location if needed


# Load model
device = torch.device("cuda")
model  = models.efficientnet_v2_m(weights=None)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model = model.to(device)
model.eval()

# Transform — must match exactly what you used during training
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],
                         [0.229,0.224,0.225])
])

def predict(image_path):
    img    = Image.open(image_path).convert("RGB")
    tensor = transform(img).unsqueeze(0).to(device)  # add batch dimension

    with torch.no_grad():
        outputs = model(tensor)
        probs   = torch.softmax(outputs, dim=1)
        pred    = outputs.argmax(dim=1).item()

    labels = {0: "FAKE", 1: "REAL"}
    print(f"Prediction : {labels[pred]}")
    print(f"Confidence : {probs[0][pred].item() * 100:.1f}%")
    print(f"Real: {probs[0][1].item()*100:.1f}%  |  Fake: {probs[0][0].item()*100:.1f}%")

def predictv2(image: cv2.typing.MatLike):
    pil_image = Image.fromarray(image)
    tensor = transform(pil_image).unsqueeze(0).to(device)  # add batch dimension

    with torch.no_grad():
        outputs = model(tensor)
        probs   = torch.softmax(outputs, dim=1)
        pred    = outputs.argmax(dim=1).item()

    labels = {0: "FAKE", 1: "REAL"}
    print(f"Prediction : {labels[pred]}")
    print(f"Confidence : {probs[0][pred].item() * 100:.1f}%")
    print(f"Real: {probs[0][1].item()*100:.1f}%  |  Fake: {probs[0][0].item()*100:.1f}%")

    return {
        "prediction": labels[pred],
        "confidence": round(probs[0][pred].item() * 100, 2),
    }

# Test it
# predict("test2.png")