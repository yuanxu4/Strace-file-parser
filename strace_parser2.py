import re
import os
from re import compile as recompile
import turtle
import sys
import numpy as np
import math
from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import datetime
LEVEL_0 = 0
LEVEL_1 = 1
LEVEL_2 = 2
# get the file overwrite overlap and access overlap 
# MODE 1 is get file overwrite and MODE 0 is get file access overlap
PARSE_MODE = 0
files = []
deleted_files = []
open_files = []

class overlap:
    def __init__(self, fp, t):
        self.filepath = fp
        self.timestart = t
        self.timeend = ""
        self.readsize = 0
        self.writesize = 0
    filepath = ""
    timestart = ""
    timeend = ""
    readsize = -1
    writesize = -1

class file_t:
    def __init__(self,path, ct):
        self.filepath = path
        self.create_time = ct
        self.delete_time = ""
        self.fd_cur = []
        self.size = 0
        self.off = 0
        self.overlaps = {}
        self.overlaps_done = []


    filepath = ""
    create_time = ""
    delete_time = ""
    fd_cur = []
    overlaps = {}
    overlaps_done = []
    size = -1
    off = -1

    def print_file(self):
        print("="*50)
        print(f"filepath: {self.filepath:<15} size: {self.size:<10}")

    def print_overlap(self):
        for i in self.overlaps_done:
            print(f"inode:{i.filepath:<15} t:{i.timestart:<17}-{i.timeend:<17}  ws:{i.writesize:<10}  rs:{i.readsize:<10}")

    def out_file(self):
        print(f"{self.filepath : <50} {self.create_time:<15} - {self.delete_time:<15} size: {self.size:<20}")
        #print(f"{self.create_time:<15} - {self.delete_time:<15} size: {self.size:<20}")
        # if file_importance(self) == LEVEL_2:
        #     self.analyze_bandwidth()

    def analyze_bandwidth(self):
        granularity = 0.1 # 0.1 seconds
        workload_start = dt.strptime(self.OPflow[0].time,'%H:%M:%S.%f')
        workload_end = dt.strptime(self.OPflow[-1].time,'%H:%M:%S.%f')
        workload_length = (workload_end - workload_start).total_seconds()
        timesteps = math.ceil(workload_length / granularity)
        all_reads = list(filter(lambda op : op.op == "read", self.OPflow))
        all_writes = list(filter(lambda op : op.op == "write", self.OPflow))
        read_bw = np.zeros(timesteps)
        write_bw = np.zeros(timesteps)
        for read in all_reads:
            timestep = int((dt.strptime(read.time,'%H:%M:%S.%f') - workload_start).total_seconds() / granularity)
            read_bw[timestep] += read.size
        
        for write in all_writes:
            timestep = int((dt.strptime(write.time,'%H:%M:%S.%f') - workload_start).total_seconds() / granularity)
            write_bw[timestep] += write.size

        read_bw /= granularity
        write_bw /= granularity
        print(f"READ BW: {read_bw}")

        t = mdates.drange(workload_start,workload_end,datetime.timedelta(seconds=0.1))
        # plt.xlabel('T/0.1 sec')
        # plt.ylabel('Bandwith/ Byte/sec')
        # plt.title('read bw')
        # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
        # plt.plot(t,read_bw)
        # plt.gcf().autofmt_xdate()
        # plt.savefig(f'{self.filepath}Writebw.pdf')
        print(f"WRITE BW: {write_bw}")
        fig = plt.figure(figsize=(20, 4))
        plt.xlabel("T/0.1 sec")
        plt.ylabel("Bandwith/ Byte/sec")
        pt = self.filepath.replace("/tmp/rocksdbtest-1003/dbbench/", "")
        plt.title(f"{pt}:{self.create_time}")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
        plt.plot(t, write_bw)
        plt.gcf().autofmt_xdate()
        plt.savefig(fig)
        plt.close(fig)

class syscall:
    time = ""
    op = ""
    args = []
    retval = 0

    @property
    def size(self):
        if self.op == "write" or self.op == "read":
            return self.retval
        else:
            return -1

    def do_err(self, msg):
        self.out_syscall()
        print(msg)
        exit(0)
        
    def out_syscall(self):
        print(f"{self.time :<15} {self.op:<10} {str(self.args):<50} {self.retval:<10}")
    
    def mknewfile(self):
        if self.op == "openat":
            new_file = file_t(self.args[1],self.time)
            new_file.fd_cur = []
            new_file.fd_cur.append(self.retval)
            open_files.append(self.args[1])
        elif self.op == "mkdir":
            new_file = file_t(self.args[0],self.time)
        files.append(new_file)

    def rmfile(self):
        for file in files:
            if file.filepath == self.args[0]:
                file.delete_time = self.time
                files.remove(file)
                deleted_files.append(file)

    
    def do_rw(self, file_ : file_t, rw: int):
        for i in open_files:
            if i != file_.filepath:
                ol = file_.overlaps.get(i)
                if ol is None:
                    ol = overlap(i, self.time)
                    file_.overlaps[i] = ol
                if rw == 1:
                    ol.writesize += self.retval
                elif rw == 0:
                    ol.readsize += self.retval
        


    def do_syscall(self):
        if self.op == "openat":
            for file in files:
                #open a exist file
                if file.filepath == self.args[1]:
                    assert(self.retval not in file.fd_cur)
                    file.fd_cur.append(self.retval)
                    if PARSE_MODE == 1:
                        open_files.append(self.args[1])
                    return 
                else:
                    if "O_CREAT" in self.args[-2]:
                        self.mknewfile()
            return 

        elif self.op == "close":
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    file.fd_cur.remove(int(self.args[0]))
                    if file.filepath in open_files:
                        open_files.remove(self.inode)
                        for v in file.overlaps.values():
                            assert(v.timeend == "")
                            v.timeend = self.time
                            file.overlaps_done.append(v)
                        file.overlaps = {}
                        for open in open_files:
                            for f in files:
                                if f.filepath == open:
                                    a = f.overlaps.get(file.filepath)
                                    if a is not None:
                                        assert(a.timeend == "")
                                        a.timeend = self.time
                                        f.overlaps_done.append(a)
                                        del f.overlaps[self.inode] 
                                    return 
            return

        elif self.op == "write":
            if int(self.args[0]) == 1 or int(self.args[0]) == 2:
                return 0
            if int(self.args[-1]) != self.retval:
                self.do_err("write request size and reture size is not match")
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    self.do_rw(file, 1)
                    if file.off == file.size:
                        file.off += self.retval
                        file.size += self.retval
                    elif file.off != file.size:
                        file.off += self.retval
                        if file.off > file.size:
                            file.size = file.off
                    return         
            return 

        elif self.op == "pread64":
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    self.do_rw(file, 0)
                    return 

        elif self.op == "read":
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    self.do_rw(file, 0)
                    file.off += self.retval
            return

        elif self.op == "lseek":
            for file in files:
                if int(self.args[0]) in file.fd_cur:          
                    file.off = self.retval
                    if file.off > file.size:
                        file.size = file.off
            return 

        elif self.op == "unlink" or self.op == "mkdir":
            self.rmfile()
            return 
        
        # elif self.op == "fsync" | self.op == "fdatasync" | self.op == "pread64" | self.op == "fcntl" | self.op == "newfstatat" | self.op == "fstatfs":
        #     for file in files:
        #         if file.fd_cur == int(self.args[0]):
        #             file.OPflow.append(self)
        #             return 0
        #     self.out_syscall()
        #     print("cant fsync a file that not exist")
        #     exit(0)
        elif self.op == "fallocate":
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    assert(int(self.args[3]) > file.size)
                    file.size = int(self.args[3])
            return

        elif self.op == "rename":
            for file in files:
                if file.filepath == self.args[0]:
                    file.filepath = self.args[1]
            return 

        elif self.op == "mkdir":
            self.mknewfile()
            return 
        
        elif self.op == "ftruncate":
            for file in files:
                if int(self.args[0]) in file.fd_cur:  
                        file.size = int(self.args[1])
                        file.OPflow.append(self)
                        if file.off > file.size:
                            file.off = file.size
            return
              

        else:
            #mmap fstatfs newfstatat getdents64 readlink access sync_file_range execve
            return 


def parse_strace(line):
        START_RE = '\d+[ ]+(\d+\:\d+\:\d+\.\d+)[ ]+'    # match timestamp
        CALL_RE = '(\w+)\((.*)\)'    # match syscall name & parameters
        END_RE = '[ ]+= (?:(\d+)|(-\d+) (.*))'  # match return value
        newsys = syscall()
        RE = recompile(START_RE + CALL_RE + END_RE)
        match = RE.match(line)
        if not match:
            print(line + "Line matching failed")
            exit(0)
        groups = match.groups()
        #print(groups)
        newsys.time = groups[0]
        newsys.op = groups[1]
        newsys.args = groups[2].replace(" ", "").replace("\"", "").split(",")
        newsys.retval = groups
        if groups[3] is not None:
            newsys.retval = int(groups[3])
        #newsys.out_syscall()
        return newsys

def file_importance(file):
    filename = file.filepath
    if "/tmp/rocksdbtest-1003/dbbench" not in file.filepath:
        return LEVEL_0
    elif ".log" in filename or ".sst" in filename:
        return LEVEL_2
    else:
        return LEVEL_1


def show_files(files):
    for file in files:
        file.out_file()
        print("")
    return 0

def clean_files(f):
    for file in reversed(f):
        if file_importance(file) == LEVEL_0:
            f.remove(file)
            print(f"removed {file.filepath}")
            

if __name__ == "__main__":
    # set input file name
    TRACE_FILE = "trace2"
    if len(sys.argv) >= 2:
        TRACE_FILE = sys.argv[1]
    
    # set threshold for line number
    line_threshold = float('inf')
    

    with open(TRACE_FILE,'r',encoding='utf8') as log_file:
        lines = log_file.readlines()
        for i, line in enumerate(lines):
            linesys = parse_strace(line)
            linesys.do_syscall()
            if i >= line_threshold:
                break
            if i != 0 and i % 100000 == 0:
                print(f"{i} lines parsed")

    for f in files:
        if len(f.overlaps_done) > 1:
            f.print_file()
            f.print_overlap()

    # clean_files(files)
    # print("===================ACTIVE FILES============================")
    # show_files(files)
    # print("===================DELETED FILES============================")
    # show_files(deleted_files)

    # fnamesc = []
    # createtimes = []
    # fnamesd = []
    # deletetimes = []
    # #add create time into list
    # for file in files:
    #     if file_importance(file) == LEVEL_2:
    #         fnamesc.append(file.filepath.replace("/tmp/rocksdbtest-1003/dbbench/", ""))
    #         createtimes.append(file.create_time)
    # for file in deleted_files:
    #     if file_importance(file) == LEVEL_2:
    #         fnamesc.append(file.filepath.replace("/tmp/rocksdbtest-1003/dbbench/", ""))
    #         createtimes.append(file.create_time)
    # #add delete file into list 
    # for file in deleted_files:
    #     if file_importance(file) == LEVEL_2:
    #         fnamesd.append(file.filepath.replace("/tmp/rocksdbtest-1003/dbbench/", ""))
    #         deletetimes.append(file.delete_time)

    

    # # Convert strings (e.g. 18:30:29.293920) to datetime
    # createtimes = [dt.strptime(d, "%H:%M:%S.%f") for d in createtimes]
    # deletetimes = [dt.strptime(d, "%H:%M:%S.%f") for d in deletetimes]

    # # Choose some nice levels
    # createlevels = np.tile([12,11,10,9,8, 7,6,5,4, 3,2, 1],
    #                 int(np.ceil(len(createtimes)/12)))[:len(createtimes)]

    # deletelevels = np.tile([-12,-11,-10,-9,-8, -7,-6,-5,-4, -3,-2, -1],
    #                 int(np.ceil(len(deletetimes)/12)))[:len(deletetimes)]

    # # Create figure and plot a stem plot with the date
    # fig, ax = plt.subplots(figsize=(60, 4), constrained_layout=False)
    # ax.set(title="file time line")

    # ax.vlines(createtimes, 0, createlevels, color="tab:red")  # The vertical stems.
    # ax.vlines(deletetimes, 0, deletelevels, color="tab:blue")  # The vertical stems.
    # ax.plot(createtimes, np.zeros_like(createtimes), "-o",
    #         color="k", markerfacecolor="w")  # Baseline and markers on it.
    # ax.plot(deletetimes, np.zeros_like(deletetimes), "-o",
    #         color="k", markerfacecolor="w")  # Baseline and markers on it.

    # # annotate lines
    # for d, l, r in zip(createtimes, createlevels, fnamesc):
    #     ax.annotate(r, xy=(d, l),
    #                 xytext=(-3, np.sign(l)*3), textcoords="offset points",
    #                 horizontalalignment="right",
    #                 verticalalignment="bottom" if l > 0 else "top")
    # for d, l, r in zip(deletetimes, deletelevels, fnamesd):
    #     ax.annotate(r, xy=(d, l),
    #                 xytext=(-3, np.sign(l)*3), textcoords="offset points",
    #                 horizontalalignment="right",
    #                 verticalalignment="bottom" if l > 0 else "top")

    # # format xaxis with 4 month intervals
    # # ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    # ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    # plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    # # remove y axis and spines
    # ax.yaxis.set_visible(False)
    # ax.spines[["left", "top", "right"]].set_visible(False)

    # ax.margins(y=0.1)
    # plt.savefig("timeline.pdf")
    # plt.close()