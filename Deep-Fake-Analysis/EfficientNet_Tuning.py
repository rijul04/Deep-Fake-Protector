import torch
from torchvision import datasets, transforms, models
from torch import nn, optim

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

train_loader = torch.utils.data.DataLoader(train_data, batch_size=32, shuffle=True)
val_loader   = torch.utils.data.DataLoader(val_data,   batch_size=32)

# 2. Load pretrained EfficientNet V2-M and swap the final layer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model  = models.efficientnet_v2_m(weights=models.EfficientNet_V2_M_Weights.IMAGENET1K_V1)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)
model  = model.to(device)

# 3. Training setup
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

# 4. Training loop
for epoch in range(10):
    model.train()
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} complete")

# 5. Save weights
torch.save(model.state_dict(), "efficientnet_v2m_deepfake.pt")