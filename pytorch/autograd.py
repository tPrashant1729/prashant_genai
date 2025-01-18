import torch as t

weights = t.ones(2, 3, requires_grad=True)

for epoch in range(3):
    model_op = (weights * 3)
    model_op.retain_grad()  # Retain gradient for non-leaf node
    op_mean = model_op.mean()
    op_mean.retain_grad()  # Retain gradient for non-leaf node
    op_add = op_mean.add(4)
    op_add.retain_grad()  # Retain gradient for non-leaf node
    
    op_add.backward()
    
    print("op_add.grad:", op_add.grad)
    print("op_mean.grad:", op_mean.grad)
    print("model_op.grad:", model_op.grad)
    print("weights.grad:", weights.grad)
    
    weights.grad.zero_()  # Reset gradients for next epoch
