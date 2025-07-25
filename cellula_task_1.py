# -*- coding: utf-8 -*-
"""Cellula_Task_1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19HcYqfoe8ew1Vb-_0mzDK78Ctng6GQPa
"""

import os

print("Top-level:", os.listdir("dataset"))

first = os.listdir("dataset")[0]
print("Inside first folder:", os.listdir(f"dataset/{first}"))

!pip install -q gdown

import gdown
import zipfile
import os
from torchvision.datasets import ImageFolder
from torchvision import transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np

file_id = "1WEySXMFz6v1OgPkLKJ8QIp3Lk-eyTObY"
url = f"https://drive.google.com/uc?id={file_id}"
gdown.download(url, "dataset.zip", quiet=False)


with zipfile.ZipFile("dataset.zip", "r") as zip_ref:
    zip_ref.extractall("dataset")

print("Top-level folders:", os.listdir("dataset"))
print("Inside Teeth_Dataset:", os.listdir("dataset/Teeth_Dataset"))

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


dataset = ImageFolder(root="dataset/Teeth_Dataset/Training", transform=transform)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

print("Detected classes:", dataset.classes)

data_iter = iter(dataloader)
images, labels = next(data_iter)

fig, ax = plt.subplots(1, 5, figsize=(15, 3))
for i in range(5):
    img = images[i].numpy().transpose((1, 2, 0))
    img = img * np.array([0.229, 0.224, 0.225]) + np.array([0.485, 0.456, 0.406])
    img = np.clip(img, 0, 1)
    ax[i].imshow(img)
    ax[i].set_title(f"Label: {dataset.classes[labels[i]]}")
    ax[i].axis('off')
plt.show()

import torch
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self, num_classes):
        super(SimpleCNN, self).__init__()

        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),  
            nn.ReLU(),
            nn.MaxPool2d(2),                             

            nn.Conv2d(16, 32, kernel_size=3, padding=1), 
            nn.ReLU(),
            nn.MaxPool2d(2),                             
        )

       
        self._to_linear = 32 * 32 * 32

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self._to_linear, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = SimpleCNN(num_classes=len(dataset.classes))
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 5

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images, labels = images.to(device), labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)

    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {running_loss/len(dataloader):.4f}, Accuracy: {100 * correct/total:.2f}%")

dataset = ImageFolder(root="dataset/Teeth_Dataset/Testing", transform=transform)

import matplotlib.pyplot as plt
import numpy as np

model.eval()
with torch.no_grad():
    img, label = dataset[160]
    img_input = img.unsqueeze(0).to(device).to(torch.float)
    output = model(img_input)
    pred = output.argmax(dim=1).item()
    predicted_class = dataset.classes[pred]

    img_plot = img.numpy().transpose(1, 2, 0)
    img_plot = img_plot * np.array([0.229, 0.224, 0.225]) + np.array([0.485, 0.456, 0.406])
    img_plot = np.clip(img_plot, 0, 1)


    plt.imshow(img_plot)
    plt.title(f"Predicted: {predicted_class} | Actual: {dataset.classes[label]}")
    plt.axis('off')
    plt.show()
