import torch
from torchvision import datasets, transforms, models
from torch import nn, optim

if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))

# 1. Load dataset
# Transforms occur to follow how EfficientNet Expects as was trained on 224 x 224 images, needs tensor 
# and iamges are also expected to be normalised (can find the normalised equation used online)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

dataset    = datasets.ImageFolder("ff_data/data/", transform=transform)
train_size = int(0.8 * len(dataset))
val_size   = len(dataset) - train_size
train_data, val_data = torch.utils.data.random_split(dataset, [train_size, val_size])

train_loader = torch.utils.data.DataLoader(train_data, batch_size=64, shuffle=True,  num_workers=4, pin_memory=True, persistent_workers=True)
val_loader   = torch.utils.data.DataLoader(val_data,   batch_size=64, shuffle=False, num_workers=4, pin_memory=True, persistent_workers=True)

print("Loader Done")

# 2. Load pretrained EfficientNet V2-M and swap the final layer
device = torch.device("cuda")
model  = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)
model  = model.to(device)

print("Model Ready with updated Classification Layer")

# 3. Training setup
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

# 4. Training loop
print("Ready for training")
for epoch in range(10):
    model.train()
    for images, labels in train_loader:
        images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        outputs = model(images)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        print("Train Loader Done")
    print(f"Epoch {epoch+1} complete")

# 5. Save weights
torch.save(model.state_dict(), "efficientnet_v2m_deepfake.pt")