import torch as t

x = t.tensor([10, 13, 15, 18.], requires_grad=True)
y= x + 2
print(y)

z = y.mul(y)
print(z)

a = z*z*z
print(a)

gradient_vector = t.ones_like(a)
a.backward(gradient_vector)
print(x.grad)
