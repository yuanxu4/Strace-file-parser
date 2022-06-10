import sys
import numpy as np

files = {}
opening_inode = []

class overlap:
    def __init__(self, i, t):
        self.timestart = t
        self.timeend = 0.0
        self.readsize = 0
        self.writesize = 0
        self.inode = i
    inode = -1
    timestart = 0.0
    timeend = 0.0
    readsize = -1
    writesize = -1

class file_t:
    def __init__(self, i, s):
        self.inode = i
        self.size = s
        self.overlaps = {}
        self.overlaps_done = []
        self.seq = 0

    inode = -1
    size = -1
    overlaps = {}
    overlaps_done = []
    seq = 0

    def print_file(self):
        print("===============================================")
        print(f"inode: {self.inode:<15} size: {self.size:<10}")

    def print_overlap(self):
        for i in self.overlaps_done:
            print(f"inode:{i.inode:<15} t:{i.timestart:<17}-{i.timeend:<17}  ws:{i.writesize:<10}  rs:{i.readsize:<10}")

class syscall:
    seq = -1
    time = 0.0
    op = -1
    inode = -1
    isize = -1
    off = -1
    opsize = -1
    
    def do_rw(self, file_ : file_t, rw: int):
        if file_.inode in useful_files:
            for i in opening_inode:
                if i != self.inode:
                    ol = file_.overlaps.get(i)
                    if ol is None:
                        ol = overlap(i, self.time)
                        file_.overlaps[i] = ol
                    if rw == 1:
                        ol.writesize += self.opsize
                    elif rw == 0:
                        ol.readsize += self.opsize

    # "OPEN": "0", "CLOSE": "1", "READ": "2", "WRITE": "3","FSYNC":"4", "FDATASYNC":"5"
    def add_newfile(self):
        new_file = file_t(self.inode, self.isize)
        new_file.seq += 1
        files[self.inode] = new_file
        opening_inode.append(self.inode)
  #@profile
    def do_syscall(self):
        file = files.get(self.inode)
        if file is None:
            if self.op == 1:
                return
            self.add_newfile()
            file = files.get(self.inode)
        if self.op == 0:
            file.size = self.isize
            file.seq += 1
            if file.seq == 1:
                assert(self.inode not in opening_inode)
                opening_inode.append(self.inode)
            return 

        elif self.op == 1:
            file.size = self.isize
            file.seq -= 1
            if file.seq == 0:
                assert(self.inode in opening_inode)
                opening_inode.remove(self.inode)
                delete_k = []
                for k,v in file.overlaps.items():
                    assert(v.timeend == 0.0)
                    v.timeend = self.time
                    file.overlaps_done.append(v)
                    delete_k.append(k)
                for i in delete_k:
                    file.overlaps.pop(i)
                for open in opening_inode:
                    f = files[open]
                    a = f.overlaps.get(self.inode)
                    if a is not None:
                        assert(a.timeend == 0.0)
                        a.timeend = self.time
                        f.overlaps_done.append(a)
                        del f.overlaps[self.inode]
            return
        elif self.op == 4 or self.op == 5:
            file.size = self.isize
            return 
        elif self.op == 3:
            file.size = self.isize
            self.do_rw(file, 1)
            return 
        elif self.op == 2:
            file.size = self.isize
            self.do_rw(file,0)
        return   

def parse_trace(line):
    newsys = syscall()
    newsys.seq = int(line[0])
    newsys.time = float(line[1])
    newsys.op = int(line[2])
    newsys.inode = int(line[3])
    newsys.isize = int(line[4])
    newsys.off = int(line[5])
    newsys.opsize = int(line[6])
    return newsys

if __name__ == "__main__":
    # set input file name
    TRACE_FILE = "../all_trace.npy"    
    line_threshold = 10000000#float('inf')
    # get the intersectin of three filter
    TRACE_FILE1 = "../overlap_files_20"
    TRACE_FILE2 = "../rsize_file"
    TRACE_FILE3 = "../wsize_file"
    with open(TRACE_FILE1,'r',encoding='utf8') as log1:
        with open(TRACE_FILE2,'r',encoding='utf8') as log2:
            with open(TRACE_FILE3,'r',encoding='utf8') as log3:
                lines1 = log1.readlines()
                lines2 = log2.readlines()
                lines3 = log3.readlines()
                useful_files = set([int(f) for f in set(lines1).intersection(lines2).intersection(lines3)])
    print(useful_files)
    all_traces = np.load(TRACE_FILE)
    # traces_useful = np.array(([ i for i in all_traces if int(i[3]) in useful_files]))
    # print(f"the total lines is {len(all_traces)}")
    for i, line in enumerate(all_traces):
        sys_call = parse_trace(line)
        sys_call.do_syscall()
        if i >= line_threshold:
            break
        # if i != 0 and i % 100000 == 0:
        #     print(f"{i} lines finished")
    for f in files.values():
        if len(f.overlaps_done) > 1:
            print("=" * 50)
            f.print_file()
            f.print_overlap()
    