import numpy as np

X = np.array([1,2,3,4], dtype=np.float32)
y = np.array([2,4,6,8], dtype=np.float32)

w=0.0



def forward(x):
    return w*x

def loss(y_pred, y):
    return ((y_pred-y)**2).mean()

# 1/N*((w*x-y)**2)
# dw/dx = 1/N*2*x*(w*x-y)
def gredient(x, y, y_pred):
    return np.dot(2*x, (y_pred-y))

lr = 0.01
epochs = 20
print(f'Prediction before training: f(5) = {forward(5):.3f}')

#training:
for epoch in range(epochs):
    y_pred=  forward(X)
    l = loss(y_pred, y)
    dw = gredient(X,y,y_pred)
    w -= dw*lr

    if epoch%2 == 0:
        print(f"epoch={epoch},weights={w:.4f},loss={l:.4f}")

print(f'Prediction after training: f(5) = {forward(5):.3f}')
