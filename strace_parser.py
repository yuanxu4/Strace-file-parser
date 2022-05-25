import re
import os

class file:
    filepath = ""
    is_dir = -1
    create_time = ""
    delete_time = ""
    fd_cur = -1
    size = -1
    off = -1
    IOflow = []

    def __init__(self, f, c, d, fd, s, o):
        self.filepath = f
        self.create_time = c
        self.delete_time = d
        self.fd_cur = fd
        self.size = s
        self.off = o

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
'''
    def get_open_arg(self, args):
        self.file = args[1]
        self.flags_create = "O_CREATE" in args[2]
    
    def get_close_arg(self, args):
        self.fd = int(args[0])

    def get_write_arg(self, args):
        self.fd = int(args[0])
        self.change_size = int(args[2])

    def get_unlink_arg(self, args):
        self.file = args[0]
'''
        

    def out_syscall(self):
        print(f"This sysop is {self.op}")
        print(f"This fd is {self.fd}")
        print(f"This file is {self.file}")
        print(f"This time is {self.time}")
        print(f"This retval is {self.retval}")
        print(f"This flags for create is {self.flags_create}")
        print(f"This flags for lseek is {self.flags_lseek}")
    



    


def parse_command(line):
    # Find timestamp, format HH:MM:SS, and remove from line
    new_line = syscall()
    timestamp = re.findall('\d{2}:\d{2}:\d{2}.\d{6}',line)[0]
    new_line.time = timestamp
    #print(f"timestamp: {timestamp} \n")
    line = line.replace(timestamp,'').strip()
    if "()" in line:
        command,rest = line.split('()',1)
        features = []
    else:
        command = re.findall('.+[(].+[)]',line)[0].strip()
        rest = line.replace(command,'')
        command,features = command.split('(',1)
        features = [x.strip() for x in re.sub('"|\]|\[|[*]','',features).split(',')]
        features[-1] = features[-1].replace(')','')
    #return_code = "return-code_%s" %rest.replace('=','',1).strip()
    new_line.op = command
    '''
    #for different operation use different assign
    if(new_line.op == "openat"):
        new_line.get_open_arg(features)
    elif new_line.op == "close":
        new_line.get_close_arg(features)
    elif new_line.op == "unlink":
        new_line.get_unlink_arg(features)
    elif new_line.op == "write":
        new_line.get_write_arg(features)
    '''
    new_line.retval = int(rest.replace('=','',1).strip())
    new_line.out_syscall()
    #print(f"feature {features} \n")
    return features

files = []
with open("trace.log",'r',encoding='utf8') as log_file:
    lines = log_file.readlines()
    for line in lines:
        parse_command(line)

print("done")

