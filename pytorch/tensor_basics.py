import torch as t
import numpy as np

x = t.rand(4,4)
print(x)
y = x.numpy()
print(type(y))

x.add_(2) # trailing '_' function make changes inplace
print(x)
print(y)
#sharing same memory, be carefull

# numpy can only handle tensors on cpu, so to convert to numpy array from tensor, that was on gpu. First we have to transfer all tensors to cpu
