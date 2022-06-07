
import sys
import os
import numpy as np
import re

if __name__ == "__main__":
    # set input file name
    TRACE_DIR = "../gsf-filesrv/"
    if len(sys.argv) >= 2:
        TRACE_FILE = sys.argv[1]
    line_threshold = 100#float('inf')

    openfiles = [f for f in os.listdir(TRACE_DIR)]

    lines = []
    print("Starting adding lines...")
    for i, f in enumerate(openfiles):
        with open(TRACE_DIR + f,'r',encoding='utf8') as log_file:
            lines += log_file.readlines()
            log_file.close()
        print(f"done file {i} " + f)
    print(f"The lines length is {len(lines)}")

    rep = {"OPEN": "0", "CLOSE": "1", "READ": "2", "WRITE": "3","FSYNC":"4", "FDATASYNC":"5"," HIT":""," MISS":""} 
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    pattern = re.compile("|".join(rep.keys()))

    print("Start adding the line into narrary")
    all_trace = np.zeros((min(len(lines),line_threshold),7))
    print(f"create a numpy array with shape:{all_trace.shape} type:{all_trace.dtype}")
    for i,l in enumerate(lines):
        l = pattern.sub(lambda m: rep[re.escape(m.group(0))], l)
        args = l.split()
        args = (args + 7 * ["0"])[:7]
        all_trace[i] = args
        if i >= line_threshold - 1:
                break
        if i != 0 and i % 1000000 == 0:
            print(f"{i} lines added")

