
import sys
import numpy as np
#from line_profiler import LineProfiler
# from datetime import datetime as dt
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from matplotlib.backends.backend_pdf import PdfPages
# import datetime


files = {}

class file_t:
    def __init__(self, i, s, r, w):
        self.inode = i
        self.size = s
        self.OPflow = []
        self.rsize = r
        self.wsize = w

    inode = -1
    size = -1
    OPflow = []
    rsize = -1
    wsize = -1

    def print_file(self):
        print(f"inode: {self.inode:<15} size: {self.size:<10}")

    def print_OPflow(self):
        out_str = ""
        for sys in self.OPflow[:1]:
            out_str += f"{sys.time:<15} {sys.op:<10} {sys.inode:<10} {sys.isize:<10} {sys.off:<10} {sys.opsize:<10}\n"
        print(out_str)

    

def add_newfile(syscall, i, s, r, w):
    new_file = file_t(i, s, r, w)
    new_file.OPflow.append(syscall)
    files[i] = new_file
    #print(f"{self.seq} add {self.inode}")
    return

#@profile
# "OPEN": "0", "CLOSE": "1", "READ": "2", "WRITE": "3","FSYNC":"4", "FDATASYNC":"5"
# 110258088 1411358401.108601 READ       2154987      19912      15450   720 HIT
def do_syscall(syscall):
    # OPEN
    if syscall[2] == 0:
        file = files.get(syscall[3])
        if file is not None:
            file.size = syscall[4]
            file.OPflow.append(syscall)
            return 
        add_newfile(syscall, syscall[3], syscall[4],0,0)
        return 
    # CLOSE
    if syscall[2] == 1:
        file = files.get(syscall[3])
        if file is not None:
            file.size = syscall[4]
            file.OPflow.append(syscall)
        return

    if syscall[2] == 4 or syscall[2] == 5:
        file = files.get(syscall[3])
        if file is not None:
            file.size = syscall[4]
            file.OPflow.append(syscall)
            return 
        add_newfile(syscall,syscall[3], syscall[4],0,0)
        return 

    if syscall[2] == 2:
        file = files.get(syscall[3])
        if file is not None:
            file.size = syscall[4]
            file.OPflow.append(syscall)
            file.rsize += syscall[6]
            return 
        add_newfile(syscall,syscall[3], syscall[4],syscall[6],0)
        return 

    if syscall[2] == 3:
        file = files.get(syscall[3])
        if file is not None:
            file.size = syscall[4]
            file.OPflow.append(syscall)
            file.wsize += syscall[6]
            return 
        add_newfile(syscall,syscall[3], syscall[4],0,syscall[6])
        return   


if __name__ == "__main__":
    # set input file name
    TRACE_FILE = "../all_trace.npy"
    OUT_FILE1 = "../rsize_file"
    OUT_FILE2 = "../wsize_file"
    
    line_threshold = 10000000 #float('inf')


    all_traces = np.load(TRACE_FILE)
    for i, line in enumerate(all_traces):
        do_syscall(line)
        if i >= line_threshold:
            break
        if i != 0 and i % 1000000 == 0:
            print(f"{i} lines finished")
    print("start sorted")
    files_sorted_r = sorted(files.items(), key = lambda x:x[1].rsize, reverse = True)
    files_sorted_w = sorted(files.items(), key = lambda x:x[1].wsize, reverse = True)
    #with open(OUT_FILE, "w") as out_f:
    print("get the most useful file")
    with open(OUT_FILE1, "w") as out_f:
        # print("The 1000 largest read file",file = out_f)
        for i, f in enumerate(files_sorted_r):
            if i < 4000:
                print(int(f[0]),file = out_f)
    with open(OUT_FILE2, "w") as out_f:
        # print("\n\n\nThe 1000 largest write file",file = out_f)
        for i, f in enumerate(files_sorted_w):
            if i < 4000:
                print(int(f[0]),file=out_f)
