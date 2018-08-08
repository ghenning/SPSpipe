#!/usr/bin/env python
'''
#################################################
Changing header info on pffts headers

run -h to see usage

written by Laura Spitler originally
modified by Henning Hilmarsson for more general
purposes (2017)

#################################################
'''
import sys
import numpy as np
import struct
import getopt
from struct import unpack
import optparse

def header(file):
    inread=''

    while True:
        tmp=file.read(1)
        inread=inread+tmp

        flag=inread.find('HEADER_END')

        if flag != -1:
            break

    return inread

def update_headparam(head, parlist, vallist):
    how2parse={
        'nchans': ('i', 4),
        'tsamp': ('d', 8),
        'foff': ('d', 8),
        'fch1': ('d', 8),
        'tstart': ('d', 8)
        }
    n=0
    for i in parlist:
        i1=head.find(i)
        i2=i1+len(i)
        nbytes=how2parse[i][1]
        cstr=how2parse[i][0]

        val=vallist.pop(0)
        val=struct.pack(cstr, val)
#       head[i1:i2]=val
        head=head[0:i2]+val+head[i2+nbytes:]
        n+=1

    return head

def flippy(INFILE,OUTFILE,NCHAN,NSAMP,DTYPE,FLIP):
    blocksize=100    
    while 1:
        dataIn=INFILE.read(4*NCHAN*NSAMP*blocksize)
        if len(dataIn)==0: break

        if FLIP:
            print "Flipping band!!"
            #d2flip=np.fromstring(dataIn, dtype='float32')
            d2flip=np.fromstring(dataIn, dtype=DTYPE)
            dlen=d2flip.shape[0]

            d2flip.shape=(dlen/NCHAN, NCHAN)
            d2flip=np.fliplr(d2flip)
            OUTFILE.write(d2flip.flatten())
        else:
            OUTFILE.write(dataIn)

def main():
    infile = open(opts.infile,'r')
    outfile = open(opts.outfile,'w')
    head = header(infile)
    newhead = update_headparam(head, ['fch1'], [opts.freq])
    newhead = update_headparam(newhead, ['foff'], [-abs(opts.bw)])
    headlen = len(head)
    infile.seek(headlen)
    outfile.write(newhead)
    flippy(infile,outfile,opts.nchan,opts.nsamp,opts.dtype,opts.flip)

if __name__=="__main__":
    desc = "Change header parameters (frequency and channel bandwidth), and flip band if needed"
    parser = optparse.OptionParser(description=desc)
    parser.add_option('--infile',dest='infile',type='string',\
        help="Filterbank file whose header needs to be changed")
    parser.add_option('--outfile',dest='outfile',type='string',\
        help="New filterbank file with updated header")
    parser.add_option('--freq',dest='freq',type='float',\
        help="The top frequency of the band in MHz")
    parser.add_option('--bw',dest='bw',type='float',\
        help="Channel bandwidth in MHz")
    parser.add_option('--nchan',dest='nchan',type='int',\
        help="Number of channels")
    parser.add_option('--nsamp',dest='nsamp',type='int',\
        help="Number of samples")
    parser.add_option('--dtype',dest='dtype',type='string',\
        help="dtype of data (float32, unit8, etc...). Default: uint8",\
        default='uint8')
    parser.add_option('--flip',dest='flip',action='store_true',\
        help="Flip the band, if it goes from low to high, use this to flip it. Default: False",\
        default=False)
    (opts,args) = parser.parse_args()
    if opts.flip:
        mandatories = ['infile','outfile','freq','bw','nchan','nsamp','dtype']
        for i in mandatories:
            if not opts.__dict__[i]:
                print "If you want to flip the band, I need all the info"
                parser.print_help()
                exit(-1)
    else:
        mandatories = ['infile','outfile','freq','bw','nchan','nsamp']
        for i in mandatories:
            if not opts.__dict__[i]:
                print "I need --infile --outfile --freq --bw --nchan --nsamp"
                parser.print_help()
                exit(-1)
    main()
    #infile = open(opts.infile,'r')
    #outfile = open(opts.outfile,'w')
    #head = header(infile)
    #newhead = update_headparam(head, ['fch1'], [opts.freq])
    #newhead = update_headparam(newhead, ['foff'], [-abs(opts.bw)])
    #headlen = len(head)
    #infile.seek(headlen)
    #outfile.write(newhead)
    #flippy(infile,outfile,opts.nchan,opts.nsamp,opts.dtype,opts.flip)

