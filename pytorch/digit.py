import torch
import torch.nn as nn
import torch.utils
import torch.utils.data
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train_dataset = torchvision.datasets.MNIST(root="./data", train=True, transform=transforms.ToTensor(), download=True)
test_dataset = torchvision.datasets.MNIST(root="./data", train=False, transform=transforms.ToTensor(), )

# hyper parameters
batch_size = 100
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle= True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle= False)

train_data, train_target = next(iter(train_loader))
print(train_data.shape)

n_total_steps = len(test_loader)
print(f"len of test laoder {n_total_steps}")
# model
input_size = 784 # 28*28
output_size = 10
hidden_size = 392

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.l2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)

        return out
    
model = NeuralNet(input_size, hidden_size, output_size)

# loss
criterian = nn.CrossEntropyLoss()

#optim
lr = 0.01
optim = torch.optim.Adam(model.parameters(), lr = lr)

# training
no_epochs = 2
n_total_steps = len(train_loader)
for epoch in range(no_epochs):
    samples_ = 0
    for i, (samples, labels) in enumerate(train_loader):
        samples_ += len(samples)
        flattened = samples.reshape(-1, 28*28)
        output = model(flattened)

        #loss
        loss = criterian(output, labels)

        # backward
        loss.backward()
        optim.step()
        optim.zero_grad()

        if (i + 1) % 100 == 0:
            print(f"Epoch: {epoch+1}/{no_epochs}, step: {i+1}/{n_total_steps}, loss:{loss.item():.4f}")
    print("total samples:",(samples_))

with torch.no_grad():
    n_sample = 0
    n_correct = 0
    for images, labels in test_loader:
        images = images.reshape(-1, 28*28)
        output = model(images)
        _, prediction = torch.max(output.data, 1)
        n_sample += labels.size(0)
        n_correct += (prediction == labels).sum().item()

    acc = 100*n_correct/n_sample
    print(f"accuracy : {acc} % ")
