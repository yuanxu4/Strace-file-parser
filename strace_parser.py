import re
import os
from re import compile as recompile
import turtle

class file_t:
    filepath = ""
    is_dir = -1
    create_time = ""
    delete_time = ""
    fd_cur = -1
    size = -1
    off = -1
    OPflow = []

    def out_file(self):
        print(f"This file is {self.filepath}")
        if self.is_dir == 1:
            print("a dir\n")
        else:
            print(f"This file's create time is {self.create_time}")
            print(f"This file's delete time is {self.delete_time}")
            print(f"This file's size is {self.size}")


class syscall:
    time = ""
    op = ""
    args = []
    retval = 0
        
    def out_syscall(self):
        print(f"This time is {self.time}")
        print(f"This sysop is {self.op}")
        print(f"This args is {self.args}")
        print(f"This retval is {self.retval}")
    
    def do_syscall(self):
        if self.op == "openat":
            #when open a dir
            if "O_DIRECTORY" in self.args[-1]:
                for file in files:
                    if file.filepath == self.args[1]:
                        file.is_dir = 1
                        file.fd_cur = self.retval
                        return 0
                    new_file = file_t()
                    new_file.filepath = self.args[1]
                    new_file.fd_cur = self.retval
                    new_file.is_dir = 1
                    new_file.OPflow.append(self)
                    files.append(new_file)
                    return 0

            for file in files:
                #open a exsit file
                if file.filepath == self.args[1]:
                    file.fd_cur = self.retval
                    file.OPflow.append(self)
                    return 0
            if "O_CREAT" in self.args[-1]:
                #create a new file
                new_file = file_t()
                new_file.filepath = self.args[1]
                new_file.fd_cur = self.retval
                new_file.create_time = self.time
                new_file.size = 0
                new_file.off = 0
                new_file.OPflow.append(self)
                files.append(new_file)
            else:
                self.out_syscall()
                print("cant open a file that not exist")
                exit(0)

        elif self.op == "close":
            for file in files:
                if file.fd_cur == int(self.args[0]):
                    file.fd_cur = -1
                    file.OPflow.append(self)
                    return 0
            self.out_syscall()
            print("cant close a file that not open")
            exit(0)

        elif self.op == "write":
            if int(self.args[-1]) != self.retval:
                self.out_syscall()
                print("write request size and reture size is not match")
                exit(0)
            for file in files:
                if file.fd_cur == int(self.args[0]):
                    if file.off == file.size:
                        file.off += self.retval
                        file.size += self.retval
                    elif file.off != file.size:
                        file.off += self.retval
                        if file.off > file.size:
                            file.size = file.off
                    file.OPflow.append(self)
                    return 0
            self.out_syscall()
            print("cant write into a file that not open")
            exit(0)
        
        elif self.op == "lseek":
            for file in files:
                if file.fd_cur == int(self.args[0]):
                    file.off = self.retval
                    file.OPflow.append(self)
                    return 0
            self.out_syscall()
            print("cant lseek change a file that not open")
            exit(0)

        elif self.op == "unlink":
            for file in files:
                if file.filepath == self.args[0]:
                    file.fd_cur = -1
                    file.delete_time = self.time
                    file.OPflow.append(self)
                    files.remove(file)
                    deleted_files.append(file)
                    return 0
            self.out_syscall()
            print("cant unlink a file that not exist")
            exit(0)

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
                if file.fd_cur == int(self.args[0]):
                    if int(self.args[3]) > file.size:
                        file.size = int(self.args[3])
                    file.OPflow.append(self)
                    return 0
            self.out_syscall()
            print("cant fallocate a file that not open")
            exit(0)
        else:
            print("not support")
            exit(0)


def parse_strace(line):
        START_RE = '(\d+\:\d+\:\d+\.\d+)[ ]+'    # match timestamp
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
    return 0


files = []
deleted_files = []
with open("trace.log",'r',encoding='utf8') as log_file:
    lines = log_file.readlines()
    for line in lines:
        linesys = parse_strace(line)
        linesys.do_syscall()
#show_files(files)
#show_files(deleted_files)
print("done")

