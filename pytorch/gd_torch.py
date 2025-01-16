import torch as t
import torch.nn as nn
X = t.tensor([[1],[2],[3],[4]], dtype=t.float32)
y = t.tensor([[2],[4],[6],[8]], dtype=t.float32)
X_test = t.tensor([5], dtype=t.float32)
n_samples, n_features = X.shape

# w = t.tensor(0.0, requires_grad=True)

input_feature, output_feature = n_features, n_features

model = nn.Linear(input_feature, output_feature)

# def forward(x):
#     return w*x


# def loss(y_pred, y):
#     return ((y_pred-y)**2).mean()
loss = nn.MSELoss()
# 1/N*((w*x-y)**2)
# dw/dx = 1/N*2*x*(w*x-y)
# def gredient(x, y, y_pred):
#     return t.dot(2*x, (y_pred-y))
lr = 0.04
epochs = 100
optimizer = t.optim.SGD(model.parameters(), lr = lr)
print(f'Prediction before training: f(5) = {model(X_test).item():.3f}')

#training:
for epoch in range(epochs):
    y_pred=  model(X)
    l = loss(y,y_pred)
    # dw = gredient(X,y,y_pred)
    l.backward()
    optimizer.step()
    optimizer.zero_grad()
    # with t.no_grad():
    #     w -= lr*w.grad

    # w.grad.zero_()

    if epoch%10 == 0:
        [w], [b] =  model.parameters()
        # print(w[0].item())
        print(f"epoch={epoch},weights={w[0].item():.4f},loss={l:.4f}")

print(f'Prediction after training: f(5) = {model(X_test).item():.3f}')
