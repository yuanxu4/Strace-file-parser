import re
import os
from re import compile as recompile
import turtle

class file_t:
    filepath = ""
    create_time = ""
    delete_time = ""
    fd_cur = []
    size = -1
    off = -1
    OPflow = []

    def out_file(self):
        print(f"This file is {self.filepath}")
        print(f"This file's create time is {self.create_time}")
        print(f"This file's delete time is {self.delete_time}")
        print(f"This file's fd is {self.fd_cur}")
        print(f"This file's size is {self.size}")


class syscall:
    time = ""
    op = ""
    args = []
    retval = 0

    def do_err(self, msg):
        self.out_syscall()
        print(msg)
        exit(0)
        
    def out_syscall(self):
        print(f"{self.time} {self.op} {self.args} {self.retval}")
    
    def do_syscall(self):
        #when open their are four situation 
        # 1: create a new file 
        # 2: open a exist file 
        # 3: open a not exist file(create before)
        # 4: open a dirctory mkdir before or open before
        # 5: open a dirctory exist
        if self.op == "openat":
            #when open a dir
            for file in files:
                #2 open a exist file
                if file.filepath == self.args[1]:
                    if self.retval not in file.fd_cur:
                            file.fd_cur.append(self.retval)
                    file.OPflow.append(self)
                    return 0
                # create a new file
            new_file = file_t()
            new_file.fd_cur = []
            new_file.filepath = self.args[1]
            new_file.fd_cur.append(self.retval)
            #1
            if "O_CREAT" in self.args[-2]:
                new_file.create_time = self.time
            else:
                #3 if the file create before we ignore its original size only keep the size change
                new_file.create_time = "create before"
            new_file.size = 0
            new_file.off = 0
            new_file.OPflow = []
            new_file.OPflow.append(self)
            files.append(new_file)
            return 0


        elif self.op == "close":
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    file.fd_cur.remove(int(self.args[0])) 
                    file.OPflow.append(self)
                    return 0
            for file in deleted_files:
                if int(self.args[0]) in file.fd_cur:
                    file.fd_cur.remove(int(self.args[0])) 
                    file.OPflow.append(self)
                    return 0
            #show_files(deleted_files)
            self.do_err("cant close a file that not open")


        elif self.op == "write":
            if int(self.args[0]) == 1 or int(self.args[0]) == 2:
                return 0
            if int(self.args[-1]) != self.retval:
                self.do_err("write request size and reture size is not match")
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    if file.off == file.size:
                        file.off += self.retval
                        file.size += self.retval
                    elif file.off != file.size:
                        file.off += self.retval
                        if file.off > file.size:
                            file.size = file.off
                    file.OPflow.append(self)
                    return 0
            for file in deleted_files:
                if int(self.args[0]) in file.fd_cur:
                    if file.off == file.size:
                        file.off += self.retval
                        file.size += self.retval
                    elif file.off != file.size:
                        file.off += self.retval
                        if file.off > file.size:
                            file.size = file.off
                    file.OPflow.append(self)
                    return 0
            self.do_err("cant write into a file that not open")
        
        elif self.op == "lseek":
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    if self.retval < 0:
                        self.do_err("cant change the offset to the negative")            
                    file.off = self.retval
                    file.OPflow.append(self)
                    return 0
            self.do_err("cant lseek change a file that not open")

        elif self.op == "unlink":
            for file in files:
                if file.filepath == self.args[0]:
                    file.delete_time = self.time
                    file.OPflow.append(self)
                    files.remove(file)
                    deleted_files.append(file)
            # if not find the file just ignore this op
            return 0
        
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
                    if int(self.args[3]) > file.size:
                        file.size = int(self.args[3])
                    file.OPflow.append(self)
                    return 0
            for file in deleted_files:
                if int(self.args[0]) in file.fd_cur:
                    if int(self.args[3]) > file.size:
                        file.size = int(self.args[3])
                    file.OPflow.append(self)
                    return 0
            self.do_err("cant fallocate a file that not open")

        elif self.op == "rename":
            for file in files:
                if file.filepath == self.args[0]:
                    file.filepath = self.args[1]
                    file.OPflow.append(self)
                    return 0

            self.do_err("can't rename a file not exist")

        elif self.op == "mkdir":
            new_file = file_t()
            new_file.fd_cur = []
            new_file.OPflow = []
            new_file.filepath = self.args[0]
            new_file.create_time = self.time
            new_file.is_dir = 1
            new_file.OPflow.append(self)
            files.append(new_file)
            return 0
        
        elif self.op == "rmdir":
            for file in files:
                if file.filepath == self.args[0]:
                    file.delete_time = self.time
                    file.OPflow.append(self)
                    files.remove(file)
                    deleted_files.append(file)
            # if not find the file just ignore this op
            return 0


        elif self.op == "fsync" or self.op == "fdatasync":
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    file.OPflow.append(self)
                    return 0
            self.do_err("cant sync the file not open")

        elif self.op == "pread64" or self.op == "fcntl":
            for file in files:
                if int(self.args[0]) in file.fd_cur:
                    file.OPflow.append(self)
                    return 0
            self.do_err("cant sync the file not open")

        else:
            #mmap fstatfs newfstatat getdents64 ftruncate readlink access sync_file_range execve
            return 0


def parse_strace(line):
        START_RE = '\d+[ ]+(\d+\:\d+\:\d+\.\d+)[ ]+'    # match timestamp
        CALL_RE = '(\w+)\((.*)\)'    # match syscall name & parameters
        END_RE = '[ ]+= (?:(\d+)|(-\d+) (.*))'  # match return value
        newsys = syscall()
        RE = recompile(START_RE + CALL_RE + END_RE)
        match = RE.match(line)
        if not match:
            print(line[:], "Line matching failed:")
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

def show_files(files):
    for file in files:
        file.out_file()
        print("")
    return 0


files = []
deleted_files = []
with open("trace.log",'r',encoding='utf8') as log_file:
    lines = log_file.readlines()
    for line in lines:
        linesys = parse_strace(line)
        linesys.do_syscall()
show_files(files)
print("=========================================================")
show_files(deleted_files)
print("done")

