## Table of contents

- [Introduction](#introduction)
- [What's included](#whats-included)
- [Bugs and feature requests](#bugs-and-feature-requests)


## introduction

This is a strace parser to get the IO flow for each file. We can get each file 's life time and size, and also the detailed IO flow.

- You can use show_files(file) to see each files' create time delete time and size  
```text
/tmp/rocksdbtest-1003/dbbench/                     create before   -                 size: 0                   
/tmp/rocksdbtest-1003/dbbench                      14:48:35.154405 -                 size: 0                   
/tmp/rocksdbtest-1003/dbbench/LOG                  14:48:35.154465 -                 size: 131072              
/tmp/rocksdbtest-1003/dbbench/LOCK                 14:48:35.156241 -                 size: 0                   
/tmp/rocksdbtest-1003/dbbench/IDENTITY             14:48:35.156423 -                 size: 36                  
/tmp/rocksdbtest-1003/dbbench/CURRENT              14:48:35.257033 -                 size: 16                  
/tmp/rocksdbtest-1003/dbbench/000004.log           14:48:35.346005 -                 size: 1380                
/tmp/rocksdbtest-1003/dbbench/MANIFEST-000005      14:48:35.346168 -                 size: 59                  
/tmp/rocksdbtest-1003/dbbench/CURRENT              14:48:35.382863 -                 size: 16                  
/tmp/rocksdbtest-1003/dbbench/OPTIONS-000007       14:48:35.450453 -                 size: 6633                
=========================================================
/tmp/rocksdbtest-1003/dbbench/LOG                  14:48:34.767825 - 14:48:34.768700 size: 4096                
/tmp/rocksdbtest-1003/dbbench/LOCK                 14:48:34.768602 - 14:48:34.768792 size: 0                   
/tmp/rocksdbtest-1003/dbbench                      create before   - 14:48:34.768857 size: 0                   
/tmp/rocksdbtest-1003/dbbench/MANIFEST-000001      14:48:34.837803 - 14:48:35.131722 size: 13                  
/tmp/rocksdbtest-1003/dbbench/LOG                  14:48:35.153322 - 14:48:35.153770 size: 131072              
/tmp/rocksdbtest-1003/dbbench/IDENTITY             14:48:34.771448 - 14:48:35.153795 size: 36                  
/tmp/rocksdbtest-1003/dbbench/MANIFEST-000005      14:48:34.960099 - 14:48:35.153834 size: 59                  
/tmp/rocksdbtest-1003/dbbench/000004.log           14:48:34.959928 - 14:48:35.153869 size: 0                   
/tmp/rocksdbtest-1003/dbbench/CURRENT              14:48:34.871455 - 14:48:35.153998 size: 16                  
/tmp/rocksdbtest-1003/dbbench/CURRENT              14:48:34.996687 - 14:48:35.153998 size: 16                  
/tmp/rocksdbtest-1003/dbbench/LOG.old.1653594515153276 14:48:34.769061 - 14:48:35.154033 size: 131072              
/tmp/rocksdbtest-1003/dbbench/OPTIONS-000007       14:48:35.064077 - 14:48:35.154073 size: 6612                
/tmp/rocksdbtest-1003/dbbench/LOCK                 14:48:34.771270 - 14:48:35.154174 size: 0                   
/tmp/rocksdbtest-1003/dbbench                      14:48:34.768996 - 14:48:35.154233 size: 0                   
/tmp/rocksdbtest-1003/dbbench/MANIFEST-000001      14:48:35.223348 - 14:48:35.518105 size: 13  
```
- You can use out_OPflow() to get the detailed IO flow of each files
```text
/tmp/rocksdbtest-1003/dbbench/000004.log           14:48:35.346005 -                 size: 1380                
14:48:35.346005 openat     ['AT_FDCWD', '/tmp/rocksdbtest-1003/dbbench/000004.log', 'O_WRONLY|O_CREAT|O_TRUNC|O_CLOEXEC', '0644']                             7         
14:48:35.346042 fcntl      ['7', 'F_GETFD']                                                                                                                   0         
14:48:35.346062 fcntl      ['7', 'F_SETFD', 'FD_CLOEXEC']                                                                                                     0         
14:48:35.346124 fcntl      ['7', '0x40c/*F_???*/', '0x7fff2b0b7eec']                                                                                          0         
14:48:35.522208 fallocate  ['7', 'FALLOC_FL_KEEP_SIZE', '0', '73819750']                                                                                      0         
14:48:35.522357 write      ['7', '\\311/\\326\\375\\203\\0\\1\\1\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\000000...', '138']             138       
14:48:35.522513 write      ['7', 'r4\\200(\\203\\0\\1\\2\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\001000...', '138']                     138       
14:48:35.522551 write      ['7', 'Z\\2\\17\\34\\203\\0\\1\\3\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\002000...', '138']                 138       
14:48:35.522578 write      ['7', '(\\16\\v\\240\\203\\0\\1\\4\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\003000...', '138']                138       
14:48:35.522602 write      ['7', '\\353a\\376\\202\\203\\0\\1\\5\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\004000...', '138']             138       
14:48:35.522626 write      ['7', '\\304\\2L\\3\\203\\0\\1\\6\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\005000...', '138']                 138       
14:48:35.522661 write      ['7', '\\fc\\f\\226\\203\\0\\1\\7\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\006000...', '138']                 138       
14:48:35.522683 write      ['7', '\\225b\\273\\225\\203\\0\\1\\10\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\007000...', '138']            138       
14:48:35.522705 write      ['7', '\\33\\327\\264\\305\\203\\0\\1\\t\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\010000...', '138']          138       
14:48:35.522726 write      ['7', '\\360\\273\\216\\v\\203\\0\\1\\n\\0\\0\\0\\0\\0\\0\\0\\1\\0\\0\\0\\1\\20\\0\\0\\0\\0\\0\\0\\0\\t000...', '138']             138       
14:48:35.523783 ftruncate  ['7', '1380']                                                                                                                      0         
14:48:35.523839 close      ['7']                                                                                                                              0        
```

## What's syscall included

- [openat]: I try to find the file in the files list, if find the file in same name, then add the fd in to fd_cur.
        if the file not in the list, we  check if the flag have O_CREAT, if have we set the create time, if not we set the create time into "create before", then set the fd

- [close]:  I find the file in the files list and deleted_files list with the fd, then deleted the fd from the fd_cur

- [write]:  I try to find the file with the fd in files and deleted_files list, then check the offset, if the offset is same with file size I just add the retval to both.
        or we just add the retval to the offset. then check if offset larger the size, we make size equal to the offset. That is to say the offset is always smaller than size. 

- [lseek]:  I just change the offset to the retval. and if the offset is larger than the size, make size equal to the offset

- [unlink]: I just set the delete time of the file, and remove the file from the files list and append into the deleted_files list

- [fallocate]: I just check if the allocate size is larger than the file size, if it is ,then make the file size equal to the allocate size and not change the offset

- [rename]: I just find the same name file in the files list, and then change the name of it

- [mkdir]: create a file with and set the create time 

- [rmdir]: find the dir name and than delete it and set the delete time

- [fsync and fdatasync]: I just add it into the OPflow

- [pread64 and fcntl]: I just add it into the OPflow, because the pread64 is not change the seek pointer(offset)

- [read]: I add the retval to the off(seek pointer)

- [ftruncate]: I just change the file size to the args[2] the length argument, and check is the offset(seek pointer) is larger than the size, make the offset equal with the size

---------------------not support-------------------------------
- mmap fstatfs newfstatat getdents64 readlink access sync_file_range execve 

## Bugs and feature requests

1. strace may delete a file then close it
2. it can open a file for two times so the file can have a lot of fd
3. can write into a file after unlink it 
4. can fallocate a file after unlink it

