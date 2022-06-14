# import profile
from re import compile as recompile
from datetime import datetime as dt
# from typing import Callable, Dict
import numpy as np
import sys

global inode_cur
inode_cur = 0

class file_t:
    def __init__(self,fp,inode):
        self.inode = inode
        self.filepath = fp
        self.size = 0
        self.off = 0
    inode = -1
    filepath = ""
    fd_cur = []
    size = -1
    off = -1
# "OPEN": "0", "CLOSE": "1", "READ": "2", "WRITE": "3","FSYNC":"4", "FDATASYNC":"5"
class syscall:
    time = 0.0
    op = ""
    args = []
    retval = 0
    def mknewfile(self):
        global inode_cur
        new_file = file_t(self.args[1],inode_cur)
        inode_cur += 1
        fd_filepath[self.retval] = self.args[1]
        # is this two file the same 
        filepath_files[self.args[1]] = new_file
        files.append(new_file)
        return new_file
    # @profile
    def do_syscall(self):
        global all_traces
        if self.op == "write":
            if self.args[0] == "1" or self.args[0] == "0":
                return
            file = filepath_files.get(fd_filepath.get(int(self.args[0])))
            if file is not None:
                file.off += self.retval
                if file.off > file.size:
                    file.size = file.off
                all_traces.append([0,self.time,2,file.inode,file.size,file.off,self.retval])
                # all_traces = np.vstack([all_traces,[0,self.time,2,file.inode,file.size,file.off,self.retval]])
        elif self.op == "read" or self.op == "pread64":
            if self.args[0] == "1" or self.args[0] == "0":
                return
            file = filepath_files.get(fd_filepath.get(int(self.args[0])))
            if file is not None:
                if self.op == "read":
                    file.off += self.retval
                all_traces.append([0,self.time,2,file.inode,file.size,file.off,self.retval])
                # all_traces = np.vstack([all_traces,[0,self.time,2,file.inode,file.size,file.off,self.retval]])
        elif self.op == "openat":
            file = filepath_files.get(self.args[1])
            if file is not None:
                fd_filepath[self.retval] = self.args[1]
            else:
                file = self.mknewfile()
            all_traces.append([0,self.time,0,file.inode,file.size,0,0])
            # all_traces = np.vstack([all_traces,[0,self.time,0,file.inode,file.size,0,0]])
            return 
        elif self.op == "close":
            file = filepath_files.get(fd_filepath.get(int(self.args[0])))
            if file is not None:
                fd_filepath.pop(int(self.args[0]))
                all_traces.append([0,self.time,1,file.inode,file.size,0,0])
                # all_traces = np.vstack([all_traces,[0,self.time,1,file.inode,file.size,0,0]])
        elif self.op == "ftruncate":
            file = filepath_files.get(fd_filepath.get(int(self.args[0])))
            if file is not None:
                file.size = int(self.args[1])
        elif self.op == "lseek":
            file = filepath_files.get(fd_filepath.get(int(self.args[0])))
            if file is not None:
                file.off = self.retval
        elif self.op == "rename":
            file = filepath_files.get(self.args[0])
            if file is not None:
                file.filepath = self.args[1]
                for k,v in fd_filepath.items():
                    if v ==self.args[0]:
                        fd_filepath[k] = self.args[1]
        return

# def do_syscall_rename():
#     global all_tracess
#     file = filepath_files.get(self.args[0])
#     if file is not None:
#         file.filepath = self.args[1]
#         for k,v in fd_filepath.items():
#             if v ==self.args[0]:
#                 fd_filepath[k] = self.args[1]

# do_syscall_dict: Dict[str, Callable] = {
#     "rename": do_syscall_rename
# }  

# do_syscall_dict[self.op]()
    
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
        newsys.time = dt.strftime(dt.strptime(groups[0],'%H:%M:%S.%f').replace(2022),"%s.%f")
        newsys.op = groups[1]
        newsys.args = groups[2].replace(" ", "").replace("\"", "").split(",")
        newsys.retval = groups
        if groups[3] is not None:
            newsys.retval = int(groups[3])
        #newsys.out_syscall()
        return newsys

if __name__ == "__main__":
    # fd : fn
    fd_filepath = {}
    # fn : file
    filepath_files = {}
    files = []
    delete_files = []
    global all_traces
    all_traces = [] #np.zeros((1,7))

    # set input file name
    TRACE_FILE = "../trace2"
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
            if i != 0 and i % 10000 == 0:
                print(f"{i} lines parsed")
    all_traces = np.array((all_traces))    
    for i in range(1000):
        print(all_traces[i])        
    # all_traces = all_traces[1:]
    # print(all_traces)
    with open('../all_trace2.npy', 'wb') as npfile:
        np.save(npfile,all_traces)