import torch
from torchvision import datasets, transforms, models
from torch import nn, optim
from tqdm.auto import tqdm
from torch.amp import autocast, GradScaler
scaler = GradScaler(device="cuda")

## Trying to speed up using GradScalar + Autocast wont run rn run wen add validation feedback for next iteration

## Trying to speed up processing in this block
torch.backends.cudnn.benchmark = True

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Optional (PyTorch 2.x): lets matmul pick faster kernels
torch.set_float32_matmul_precision("high")
#################

if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))

# 1. Load dataset
# Transforms occur to follow how EfficientNet Expects as was trained on 256 images i think need to check, needs tensor 
# and iamges are also expected to be normalised (can find the normalised equation used online)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

dataset    = datasets.ImageFolder("ff_data/data/faces", transform=transform)
train_size = int(0.8 * len(dataset))
val_size   = len(dataset) - train_size
train_data, val_data = torch.utils.data.random_split(dataset, [train_size, val_size])

train_loader = torch.utils.data.DataLoader(train_data, batch_size=64, shuffle=True,  num_workers=8, pin_memory=True, persistent_workers=True)
val_loader = torch.utils.data.DataLoader(val_data, batch_size=64, num_workers=8, pin_memory=True, persistent_workers=True)

print("Loader Done")

# 2. Load pretrained EfficientNet V2-m and swap the final layer
device = torch.device("cuda")
model  = models.efficientnet_v2_m(weights=models.EfficientNet_V2_M_Weights.IMAGENET1K_V1, progress = True)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)

# Below for two phase training
# Freeze all layers
for param in model.parameters():
    param.requires_grad = False

# Unfreeze only the classifier
for param in model.classifier.parameters():
    param.requires_grad = True


model = model.to(device)
model = model.to(memory_format=torch.channels_last)
model = torch.compile(model)  # PyTorch 2.x

print("Model Ready with updated Classification Layer")

# 3. Training setup
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)
# scheduler to help stop overshooting?
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=2, factor=0.5)

# 4. Training loop
print("Ready for training")

best_val_loss = float('inf')

for epoch in range(10):

    # phase 2 switch below
    if epoch == 5:
        print("Phase 2 unfreezing all layers")
        for param in model.parameters():
            param.requires_grad = True
        optimizer = optim.Adam(model.parameters(), lr=1e-5)  # 10x lower LR
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=2, factor=0.5)

    model.train()

    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{10}", leave=False)

    for images, labels in pbar:
        images, labels = images.to(device, non_blocking=True).to(memory_format=torch.channels_last), labels.to(device, non_blocking=True)
        optimizer.zero_grad()

        with autocast(device_type="cuda"):
            outputs = model(images)
            loss = criterion(outputs, labels)


        # outputs = model(images)
        # loss    = criterion(outputs, labels)
        # loss.backward()
        # optimizer.step()
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

    # Validation
    model.eval()
    correct, total, val_loss = 0, 0, 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            with autocast(device_type="cuda"):
                outputs = model(images)
                loss = criterion(outputs, labels)
            val_loss += loss.item()
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)

    avg_val_loss = val_loss / len(val_loader)
    print(f"Epoch {epoch+1} | Val Loss: {avg_val_loss:.4f} | Val Acc: {correct/total:.4f}")

    # 5. Save weights if better
    
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        torch.save(model.state_dict(), "efficientnet_v2m_deepfake_v2.pt") 
        print(f">> Best model saved (val_loss: {avg_val_loss:.4f})")
    
    scheduler.step(avg_val_loss)

    print(f"Epoch {epoch+1} complete")


