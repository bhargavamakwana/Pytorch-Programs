# Pytorch FashionMNIST Example

import torch
import os
import pandas as pd
from torch import nn

from torch.utils.data import Dataset
# To load the data in batches. One can iterate using the loop or enumerate to
# to get the batch.
from torch.utils.data import DataLoader
# Pre-loaded datasets, which we can download
from torchvision import datasets
# This transform is useful to convert the dataset into pytorch format
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt

# Load the Training data
training_data = datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor()
)

# Load the testing data
testing_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download = True,
    transform=ToTensor()
)

# Define your labels

labels_map = {
    0: "T-Shirt",
    1: "Trouser",
    2: "Pullover",
    3: "Dress",
    4: "Coat",
    5: "Sandal",
    6: "Shirt",
    7: "Sneaker",
    8: "Bag",
    9: "Ankle Boot",
}

figure = plt.figure(figsize=(8, 8))
cols, rows = 3, 3
# Check random data
for i in range(cols, cols*rows+1):
  sample_idx = torch.randint(len(training_data), size = (1,)).item()
  #print(sample_idx)
  img, label = training_data[sample_idx]
  figure.add_subplot(rows, cols, i)
  plt.title(labels_map[label])
  plt.axis("off")
  plt.imshow(img.squeeze(), cmap="gray")
plt.show()

# define train and test Dataloader object
train_dataloader = DataLoader(training_data, batch_size=64, shuffle=True)
test_dataloader = DataLoader(testing_data, batch_size=64, shuffle=True)

# Display image and label.
train_features, train_labels = next(iter(train_dataloader))
print(f"Feature batch shape: {train_features.size()}")
print(f"Labels batch shape: {train_labels.size()}")
img = train_features[0].squeeze()
label = train_labels[0]
plt.imshow(img, cmap="gray")
plt.show()
print(f"Label: {label}")

"""
Define your network in this function. use nn.Module to inherit parent class
and methods. The forward method is defined here, but never called. This is
because The pytorch method when passed using model(x) calls it every time
internally.
"""
class Network(torch.nn.Module):
  def __init__(self):
    super(Network, self).__init__()
    # define convolution layers of the n/w
    self.flatten = nn.Flatten()
    self.linear_relu_stack = nn.Sequential(
        nn.Linear(28*28, 512),
        nn.ReLU(),
        nn.Linear(512, 512),
        nn.ReLU(),
        nn.Linear(512, 10),
    )

  # define feedforward function after initializing the n/w
  def forward(self, x):
    # conv 1
    x = self.flatten(x)
    logits = self.linear_relu_stack(x)
    return logits

# check if nvidia gpu is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Using {device} device')

# Define your model and load it to device specified.
model = Network().to(device)
print(model)

# Define the train loop.
def train_loop(dataloader, model, loss_fn, optimizer, learning_rate, batch = 64):
  
  # Size to rationalize the loss
  size = len(train_dataloader.dataset)
  total_loss = 0
  num_batches = len(dataloader)

  for batch, (train_features, train_labels) in enumerate(train_dataloader):
    preds = model(train_features)
    loss = loss_fn(preds, train_labels)
    total_loss += loss
    # Backpropagation. Every time the gradient is calculated using backward()
    # function it is stored and added with previous gradients. To overcome that
    # we use the below function.
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # if batch % 100 == 0:
    #   loss, current = loss.item(), batch * len(preds)
    #   print(f"loss: {loss:>7f} [{current:>5d}/{size:>5d}]")

  return total_loss / num_batches

# test loop
def test_loop(dataloader, model, loss_fn):
  size = len(dataloader.dataset)
  num_batches = len(dataloader)
  loss, correct = 0, 0
  # Since we do not need to train the model.
  with torch.no_grad():
    # Iterate in batches.
    for test_features, test_labels in dataloader:
      pred = model(test_features)
      loss += loss_fn(pred, test_labels)
      correct += (pred.argmax(1) == test_labels).type(torch.float).sum().item()
      
  loss /= num_batches

  correct /= size
  print(f"Test Error: \n Accuracy: {100*correct:>0.1f}%, Avg Loss: {loss:>8f} \n")
  return loss

# Define your learning rate, batch and number of epochs. Remember the more the 
# number of epochs the more the model with see the data. Hence, it will tend to 
# overfit on training data. To avoid that we also see how the model performs on 
# the test data and plot the train and test loss over epochs. when the test loss
# starts to diverge, means that the model has started to overfit the data.
learning_rate = 1e-2
batch = 64
epochs = 100
# Define your loss.
loss_fn = torch.nn.CrossEntropyLoss()
# Define your optimizer. 
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
total_train, total_test = [], []
for t in range(epochs):
  print(f"Epoch {t+1}\n-----------------------")
  train_loss = train_loop(train_dataloader, model, loss_fn, optimizer, learning_rate=learning_rate)
  test_loss = test_loop(test_dataloader, model, loss_fn)
  total_train.append(train_loss)
  total_test.append(test_loss)
plt.figure(figsize=(16,6))
plt.plot(total_train, color = 'red')
plt.plot(total_test, color="green")
plt.show()

