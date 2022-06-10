import sys
import numpy as np
from joblib import Parallel, delayed
#from line_profiler import LineProfiler
# from datetime import datetime as dt
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from matplotlib.backends.backend_pdf import PdfPages
# import datetime


files = {}

class file_t:
    def __init__(self, i, s):
        self.inode = i
        self.size = s
        # self.OPflow = []
        self.time_stamp = []
        self.time_open = 0
        self.overtime = 0
        self.open_count = 0
    open_count = 0
    inode = -1
    size = -1
    # OPflow = []
    time_stamp = []
    time_open = 0
    overtime = 0

    def print_file(self):
        print(f"inode: {self.inode:<15} size: {self.size:<10}")

    

def add_newfile(syscall, i, s):
    new_file = file_t(i, s)
    # new_file.OPflow.append(syscall)
    new_file.time_open = syscall[1]
    new_file.open_count += 1
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
            file.open_count += 1
            file.size = syscall[4]
            # file.OPflow.append(syscall)
            if file.open_count == 1:
                file.time_open = syscall[1]
            return 
        add_newfile(syscall, syscall[3], syscall[4])
        return 
    # CLOSE
    if syscall[2] == 1:
        file = files.get(syscall[3])
        if file is not None:
            file.size = syscall[4]
            file.open_count -= 1
            # file.OPflow.append(syscall)
            if file.time_open != 0.0:
                if file.open_count  == 0:
                    if syscall[1] - file.time_open >= 20:
                        file.time_stamp.append((file.time_open, syscall[1]))
                    file.time_open = 0.0
        return
    # FSYNC
    if syscall[2] == 4 or syscall[2] == 5:
        file = files.get(syscall[3])
        if file is not None:
            file.size = syscall[4]
            # file.OPflow.append(syscall)
            return 
        add_newfile(syscall,syscall[3], syscall[4])
        return 
    # READ
    if syscall[2] == 2:
        file = files.get(syscall[3])
        if file is not None:
            file.size = syscall[4]
            # file.OPflow.append(syscall)
            return 
        add_newfile(syscall,syscall[3], syscall[4])
        return 
    # WRITE
    if syscall[2] == 3:
        file = files.get(syscall[3])
        if file is not None:
            file.size = syscall[4]
            # file.OPflow.append(syscall)
            return 
        add_newfile(syscall,syscall[3], syscall[4])
        return   

def overlap(tuple1, tuple2):
    max_start = max(tuple1[0], tuple2[0])
    min_end = min(tuple1[1], tuple2[1])
    return min_end - max_start

def get_onefile(i,filesin):
    ret = []
    logfile = open("../log/"+str(i)+".log", "w+")
    print(f"this file is for {i}")
    for index,f in enumerate(filesin.values()):
        if index % JOB_NUM == i:  
            print(index,file = logfile)
            logfile.flush()
            for tuple in f.time_stamp:
                for f2 in filesin.values():
                    if f != f2:
                        # print(len(f2.time_stamp))
                        for tuple2 in f2.time_stamp:
                            intersect_t = overlap(tuple, tuple2)
                            if intersect_t >= 10:
                                f.overtime += intersect_t
            ret.append((f.inode,f.overtime))
    logfile.seek(0,0)
    print(f"done",file = logfile)
    logfile.close()
    return ret



if __name__ == "__main__":
    # set input file name
    TRACE_FILE = "../all_trace.npy"
    OUT_FILE = "../overlap_files_20"
    JOB_NUM = 80
    if len(sys.argv) >= 2:
        TRACE_FILE = sys.argv[1]
    
    line_threshold = 10000000#float('inf')


    all_traces = np.load(TRACE_FILE)
    for i, line in enumerate(all_traces):
        do_syscall(line)
        if i >= line_threshold:
            break
        if i != 0 and i % 1000000 == 0:
            print(f"{i} lines finished")

    print("caculate overlap...")
    #with open(OUT_FILE, "w") as out_f:
    print(f"file length is {len(files)}")
    
    ret_list = Parallel(n_jobs = JOB_NUM)(delayed(get_onefile)(i,files) for i in range(JOB_NUM))
    # for i,f in enumerate(files.values()):
    #     print(i)
    #     for tuple in f.time_stamp:
    #         for f2 in files.values():
    #             if f2 != f:
    #                 # print(len(f2.time_stamp))
    #                 for tuple2 in f2.time_stamp:
    #                     intersect_t = overlap(tuple, tuple2)
    #                     if intersect_t >= 10:
    #                         f.overtime += intersect_t
    
    # print("start sorted")
    # files_sorted = sorted(files.items(), key = lambda x:x[1].overtime, reverse = True)
    # with open(OUT_FILE, "w") as out_f:
    #     for i, f in enumerate(files_sorted):
    #         if i < 1000:
    #             print(int(f[0]),file = out_f)
    files_sorted = []
    for l in ret_list:
        files_sorted += l
    print("start sorted")
    files_sorted = sorted(files_sorted, key = lambda x:x[1], reverse = True)
    with open(OUT_FILE, "w") as out_f:
        for i, f in enumerate(files_sorted):
            if i < 4000:
                print(int(f[0]),file = out_f)
