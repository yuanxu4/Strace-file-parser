
import os
import string
import turtle
import sys
import numpy as np
import math
#from line_profiler import LineProfiler
# from datetime import datetime as dt
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from matplotlib.backends.backend_pdf import PdfPages
# import datetime


files = {}
opening_inode = []

class overlap:
    def __init__(self, i, t):
        self.timestart = t
        self.timeend = ""
        self.readsize = 0
        self.writesize = 0
        self.inode = i
    inode = -1
    timestart = ""
    timeend = ""
    readsize = -1
    writesize = -1

class file_t:
    def __init__(self, i, s):
        self.inode = i
        self.size = s
        self.OPflow = []
        self.overwriteoff = []
        self.overwritesize = []
        self.overlaps = {}
        self.overlaps_done = []
        self.overwritet = []

    inode = -1
    size = -1
    overwritet = []
    overwriteoff = []
    overwritesize = []
    OPflow = []
    overlaps = {}
    overlaps_done = []

    def print_file(self):
        print(f"inode: {self.inode:<15} size: {self.size:<10}")

    def print_overwrite(self):
        for i,o in enumerate(self.overwritet):
            print(f"{self.overwritet[i]:<15} {self.overwriteoff[i]:<10} {self.overwritesize[i]:<10}")

    def print_overlap(self):
        for i in self.overlaps_done:
            print(f"inode:{i.inode:<15} t:{i.timestart:<17}-{i.timeend:<17}  ws:{i.writesize:<10}  rs:{i.readsize:<10}")


    def print_OPflow(self):
        out_str = ""
        for sys in self.OPflow[:1]:
            out_str += f"{sys.time:<15} {sys.op:<10} {sys.inode:<10} {sys.isize:<10} {sys.off:<10} {sys.opsize:<10}\n"
        print(out_str)

class syscall:
    seq = -1
    time = ""
    op = ""
    inode = -1
    isize = -1
    off = -1
    opsize = -1
    # def print_syscall(self):
    
    def do_write(self, file_):
        if self.off < self.isize:
            file_.overwritet.append(self.time)
            file_.overwriteoff.append(self.off)
            if (self.off + self.opsize) < self.isize:
                file_.overwritesize.append(self.opsize)
            else :
                file_.overwritesize.append(self.isize - self.off)
                file_.size = self.off + self.opsize
        else:
            file_.size = self.off + self.opsize
        for i in opening_inode:
            if i != self.inode:
                ol = file_.overlaps.get(i)
                if ol is None:
                    ol = overlap(i, self.time)
                    file_.overlaps[i] = ol
                    #print(f"{self.seq} {self.inode} create a new for {i}")
                ol.writesize += self.opsize
                #assert(file_.overlaps[i].writesize == ol.writesize)
        return
    def add_newfile(self, is_write):
        new_file = file_t(self.inode, self.isize)
        new_file.OPflow.append(self)
        if is_write:
            self.do_write(new_file)
        files[self.inode] = new_file
        opening_inode.append(self.inode)
        #print(f"{self.seq} add {self.inode}")
        if self.op == "READ":
            for i in opening_inode:
                    if i != self.inode:
                        ol = overlap(i, self.time)
                        new_file.overlaps[i] = ol
                        ol.readsize += self.opsize
                        #print(f"{self.seq} {self.inode} create a new for {i}")
        return

    #@profile
    def do_syscall(self):
        if self.op == "OPEN":
            file = files.get(self.inode)
            if file is not None:
                file.size = self.isize
                file.OPflow.append(self)
                return 
            self.add_newfile(False)
            return 

        elif self.op == "CLOSE":
            file = files.get(self.inode)
            if file is not None:
                file.size = self.isize
                file.OPflow.append(self) 
                if self.inode in opening_inode:
                    opening_inode.remove(self.inode)
                    #print(f"{self.seq} remove {self.inode}")
                    delete_k = []
                    for k,v in file.overlaps.items():
                        if v.timeend == "":
                            v.timeend = self.time
                            file.overlaps_done.append(v)
                            delete_k.append(k)
                    for i in delete_k:
                        file.overlaps.pop(i)
                    delete_k = []
                    for open in opening_inode:
                        f = files[open]
                        a = f.overlaps.get(self.inode)
                        if a is not None:
                            if a.timeend == "":
                                a.timeend = self.time
                                f.overlaps_done.append(a)
                                del f.overlaps[self.inode]
            return

        elif self.op == "FSYNC" or self.op == "FDATASYNC":
            file = files.get(self.inode)
            if file is not None:
                file.size = self.isize
                file.OPflow.append(self)
                return 
            self.add_newfile(False)
            return 

        elif self.op == "WRITE":
            file = files.get(self.inode)
            if file is not None:
                file.size = self.isize
                # we assum the data in the file is valid not the fallocate
                file.OPflow.append(self)
                self.do_write(file)
                return
            self.add_newfile(True)
            return     

        elif self.op == "READ":
            file = files.get(self.inode)
            if file is not None:
                file.size = self.isize
                # we assum the data in the file is valid not the fallocate
                file.OPflow.append(self)
                for i in opening_inode:
                    if i != self.inode:
                        ol = file.overlaps.get(i)
                        if ol is None:
                            ol = overlap(i, self.time)
                            file.overlaps[i] = ol
                            #print(f"{self.seq} {self.inode} create a new for {i}")
                        ol.readsize += self.opsize
                        #assert(file.overlaps[i].readsize == ol.readsize)
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

if __name__ == "__main__":
    # set input file name
    TRACE_FILE = "test"
    if len(sys.argv) >= 2:
        TRACE_FILE = sys.argv[1]
    
    line_threshold = 1000000#float('inf')


    with open(TRACE_FILE,'r',encoding='utf8') as log_file:
        lines = log_file.readlines()
        for i, line in enumerate(lines):
            linesys = parse_trace(line)
            linesys.do_syscall()
            if i >= line_threshold:
                break
            if i != 0 and i % 100000 == 0:
                print(f"{i} lines parsed")
    for f in files.values():
        print("=========================================================================================")
        f.print_file()
        f.print_overlap()
        print("=========================================================================================")
    