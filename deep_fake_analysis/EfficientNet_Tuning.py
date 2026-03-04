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
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],
                         [0.229,0.224,0.225])
])

dataset    = datasets.ImageFolder("ff_data/data/", transform=transform)
train_size = int(0.8 * len(dataset))
val_size   = len(dataset) - train_size
train_data, val_data = torch.utils.data.random_split(dataset, [train_size, val_size])

train_loader = torch.utils.data.DataLoader(train_data, batch_size=32, shuffle=True,  num_workers=8, pin_memory=True, persistent_workers=True)
val_loader = torch.utils.data.DataLoader(val_data,   batch_size=32, num_workers=8, pin_memory=True, persistent_workers=True)

print("Loader Done")

# 2. Load pretrained EfficientNet V2-s and swap the final layer
device = torch.device("cuda")
model  = models.efficientnet_v2_m(weights=models.EfficientNet_V2_M_Weights.IMAGENET1K_V1, progress = True)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)
model = model.to(device)
model = model.to(memory_format=torch.channels_last)
model = torch.compile(model)  # PyTorch 2.x

print("Model Ready with updated Classification Layer")

# 3. Training setup
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

# 4. Training loop
print("Ready for training")
for epoch in range(10):
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
    print(f"Epoch {epoch+1} complete")

# 5. Save weights
torch.save(model.state_dict(), "efficientnet_v2m_deepfake.pt")