#!/usr/bin/env python

import os
import subprocess
import filterbank

def bash_command(cmd):
    subprocess.call(['/bin/bash','-c',cmd])

files = os.listdir(os.getcwd())

band0 = [f for f in files if f.endswith("FB0.fil")]
print band0

band1 = [f for f in files if f.endswith("FB1.fil")]
print band1

for i in band0:
    newname = i.split('.')[0] + "_NEWHEAD." + i.split('.')[-1]
    filfile = filterbank.FilterbankFile(i)
    N = filfile.N
    #comm = "python fix_pffts_header.py --infile %s --outfile %s \
        #--freq 7299.510695 --bw -0.976562 --nchan 2048 --nsamp %s --dtype uint8 \
        #--flip" % (i,newname,str(N))
    comm = "python fix_pffts_header.py --infile %s --outfile %s \
        --freq 6000 --bw -0.976562 --nchan 2048 --nsamp %s --dtype uint8 \
        --flip" % (i,newname,str(N))
    print "fixing header of " + i
    bash_command(comm)
    print "fixed header, new file is " + newname

for i in band1:
    newname = i.split('.')[0] + "_NEWHEAD." + i.split('.')[-1]
    filfile = filterbank.FilterbankFile(i)
    N = filfile.N
    #comm = "python fix_pffts_header.py --infile %s --outfile %s \
        #--freq 9300 --bw -0.976562 --nchan 2048 --nsamp %s --dtype uint8" % (i,newname,str(N))
    comm = "python fix_pffts_header.py --infile %s --outfile %s \
        --freq 8000 --bw -0.976562 --nchan 2048 --nsamp %s --dtype uint8" % (i,newname,str(N))
    print "fixing header of " + i
    bash_command(comm)
    print "fixed header, new file is " + newname
