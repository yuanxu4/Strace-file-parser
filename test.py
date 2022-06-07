import numpy as np

a = np.arange(10).reshape(2,5)
b = np.array(([3,5,7],
            [1,4,7],
            [9,2,56]))
b = b[b[:,0].argsort()]
print(b)

