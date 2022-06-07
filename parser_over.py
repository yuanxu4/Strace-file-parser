
import string
import sys
import numpy as np



files = {}

class file_t:
    def __init__(self, i, s):
        self.inode = i
        self.size = s
        self.OPflow = []
        self.time_stamp = []
        self.time_open = ""
        self.overtime = 0
    overtime = 0
    inode = -1
    size = -1
    OPflow = []
    time_stamp = []
    time_open = 0.0

    def print_file(self):
        print(f"inode: {self.inode:<15} size: {self.size:<10}")

    def print_overlap(self):
        for i in self.overlaps_done:
            print(f"inode:{i.inode:<15} t:{i.timestart:<17}-{i.timeend:<17}  ws:{i.writesize:<10}  rs:{i.readsize:<10}")

class syscall:
    seq = -1
    time = ""
    op = ""
    inode = -1
    isize = -1
    off = -1
    opsize = -1
    # def print_syscall(self):
    
    
    def add_newfile(self, is_write):
        new_file = file_t(self.inode, self.isize)
        new_file.OPflow.append(self)
        new_file.time_open = float(self.time)
        files[self.inode] = new_file
        return

    #@profile
    def do_syscall(self):
        if self.op == "OPEN":
            file = files.get(self.inode)
            if file is not None:
                file.size = self.isize
                file.OPflow.append(self)
                file.time_open = float(self.time)
                return 
            self.add_newfile(False)
            return 

        elif self.op == "CLOSE":
            file = files.get(self.inode)
            if file is not None:
                file.size = self.isize
                file.OPflow.append(self) 
                if file.time_open != 0.0:
                    if float(self.time) - file.time_open >= 10:
                        file.time_stamp.append((file.time_open, float(self.time)))
                    file.time_open = 0.0
            return

        elif self.op == "FSYNC" or self.op == "FDATASYNC" or self.op == "READ" or self.op == "WRITE":
            file = files.get(self.inode)
            if file is not None:
                file.size = self.isize
                file.OPflow.append(self)
                return 
            self.add_newfile(False)
            return






def parse_trace(line:string):
    args = line.split()
    newsys = syscall()
    newsys.seq = int(args[0])
    newsys.time = args[1]
    newsys.op = args[2]
    newsys.inode = int(args[3])
    newsys.isize = int(args[4])
    if len(args) > 6:
        newsys.off = int(args[5])
        newsys.opsize = int(args[6])
    return newsys

def overlap(tuple1, tuple2):
    max_start = max(tuple1[0], tuple2[0])
    min_end = min(tuple1[1], tuple2[1])
    return (max_start, min_end), min_end - max_start
    # if tuple1[0] > tuple2[1] or tuple1[1] < tuple2[0]:
    #     return 0
    # if tuple1[1]>tuple2[1]:
    #     if tuple1[0] < tuple2[0]:
    #         return tuple2
    #     elif tuple1[0] < tuple2[1]:
    #         return (tuple1[0],tuple2[1])
    #     return 0
    # else:
    #     if tuple1[0] > tuple2[0]:
    #         return tuple1
    #     elif tuple1[1] > tuple2[0]:
    #         return (tuple2[0], tuple1[1])
    #     return 0        

if __name__ == "__main__":
    # set input file name
    TRACE_FILE = "test"
    OUT_FILE = "output"
    if len(sys.argv) >= 2:
        TRACE_FILE = sys.argv[1]
    
    line_threshold = float('inf')

    print("doing parser...")
    with open(TRACE_FILE,'r',encoding='utf8') as log_file:
        lines = log_file.readlines()
        for i, line in enumerate(lines):
            linesys = parse_trace(line)
            linesys.do_syscall()
            if i >= line_threshold:
                break
            if i != 0 and i % 100000 == 0:
                print(f"{i} lines parsed")

    print("caculate overlap...")
    #with open(OUT_FILE, "w") as out_f:
    print(len(files))
    for i, f in enumerate(files.values()):
        print(i)
        #print("=========================================================", file=out_f)
        for tuple in f.time_stamp:
            for f2 in files.values():
                if f2 != f:
                    for tuple2 in f2.time_stamp:
                        intersect, intersect_t = overlap(tuple, tuple2)
                        if intersect_t >= 10:
                            f.overtime += intersect_t
                            #print (f"{f.inode:<15} {f2.inode:<15} t:{intersect[0]:<17}-{intersect[1]:<17}", file=out_f)
    files_sorted = sorted(files.items(), key = lambda x:x[1].overtime, reverse = True)
    #with open(OUT_FILE, "w") as out_f:
    for i, f in enumerate(files_sorted):
        if i < 1000:
            print(f[0])
