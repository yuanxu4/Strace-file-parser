import numpy as np


all_traces = np.array(([1,2,3,4,5],[3,4,6,7,8],[54,36,24,56,23]))
list1 = [1,54]
traces_useful = np.array(([i for i in all_traces if i[0] in list1]))
print(traces_useful)