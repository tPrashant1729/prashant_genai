import torch as t
from sklearn import datasets
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

n_sample, n_features = datasets.make_regression(100, 1, noise=20, random_state=1)

X = t.from_numpy(n_sample.astype(np.float32))
y = t.from_numpy(n_features.astype(np.float32))
y = y.view(y.shape[0], 1)

n_samples, n_features = X.shape
print(n_samples, n_features)

# 1) Model
# Linear model f = wx + b
input_size = n_features
output_size = 1
# input_size , output_size = X.shape
print(input_size , output_size)

lr = 0.03

# model
model = nn.Linear(input_size , output_size)
criterion = nn.MSELoss()
optimizer = t.optim.SGD(model.parameters(), lr = lr)

n_iter = 100
for epoch in range(n_iter):
    y_pred = model(X)
    loss = criterion(y, y_pred)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

    if (epoch+1)%5 == 0:
        print(f"epoch :{epoch+1}, loss :{loss.item():.4f}")

# Plot
predicted = model(X).detach().numpy()

plt.plot(X, y, 'ro')
plt.plot(X, predicted, 'b')
plt.show()