
import os
import string
import turtle
import sys
import numpy as np
import math

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