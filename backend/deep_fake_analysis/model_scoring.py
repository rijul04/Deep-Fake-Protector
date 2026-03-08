import random

import torch
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
from torchvision import datasets, transforms, models
from torch import nn
from torch.utils.data import DataLoader, Subset
from tqdm import tqdm

device = torch.device("cuda")
model  = models.efficientnet_v2_s(weights=None)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)
model.load_state_dict(torch.load("efficientnet_v2s_deepfake.pt", map_location=device))
model = model.to(device)
model.eval()

# transform = transforms.Compose([
#     transforms.Resize(256),
#     transforms.CenterCrop(224),
#     transforms.ToTensor(),
#     transforms.Normalize([0.485,0.456,0.406],
#                          [0.229,0.224,0.225])
# ])
# For ABOVE THE ABOVE IS THE RIGHT TRANSFORM BUT FOR VERSION ) DID THE BELOW TRANSFORMATION

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# full_dataset = datasets.ImageFolder("./cfd_data/data/faces", transform=transform)
# train_data, val_data = torch.utils.data.random_split(full_dataset, [len(full_dataset)-5000, 5000])
# test_loader  = DataLoader(val_data, batch_size=32, shuffle=False, num_workers=4)
test_dataset = datasets.ImageFolder("./cdf_data/data/faces", transform=transform)

# print(test_dataset.classes)
# print(test_dataset.class_to_idx)
# exit()

class_indices = {}
for idx, (_, label) in enumerate(test_dataset.samples):
    if label not in class_indices:
        class_indices[label] = []
    class_indices[label].append(idx)

# Sample 5000 from each class
samples_per_class = 5000
selected_indices = []
for label, indices in class_indices.items():
    selected_indices.extend(random.sample(indices, samples_per_class))

random.shuffle(selected_indices)

subset = Subset(test_dataset, selected_indices)
test_loader = DataLoader(subset, batch_size=32, shuffle=False, num_workers=4)


all_preds, all_labels, all_probs = [], [], []

with torch.no_grad():
    for images, labels in tqdm(test_loader):
        images  = images.to(device)
        outputs = model(images)
        probs   = torch.softmax(outputs, dim=1)[:, 1]
        preds   = outputs.argmax(dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.numpy())
        all_probs.extend(probs.cpu().numpy())

all_preds  = np.array(all_preds)
all_labels = np.array(all_labels)
all_probs  = np.array(all_probs)

# Calculations below
accuracy = accuracy_score(all_labels, all_preds)
f1 = f1_score(all_labels, all_preds, average='weighted')
auc = roc_auc_score(all_labels, all_probs)
cm = confusion_matrix(all_labels, all_preds)

tn, fp, fn, tp = cm.ravel()
precision = tp / (tp + fp)
recall    = tp / (tp + fn)

print("=" * 50)
print("BASELINE MODEL EVALUATION")
print("=" * 50)
print(f"Accuracy:  {accuracy:.4f}  ({accuracy*100:.1f}%)")
print(f"F1 Score:  {f1:.4f}")
print(f"AUC:       {auc:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"\nConfusion Matrix:")
print(f"               Predicted Real  Predicted Fake")
print(f"Actual Real    {tn:<15} {fp}")
print(f"Actual Fake    {fn:<15} {tp}")
print(f"\nFull Report:")
print(classification_report(all_labels, all_preds, target_names=['real', 'fake']))