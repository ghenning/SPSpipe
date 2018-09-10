
import sys
import numpy as np
import struct
import getopt
from struct import unpack
import optparse
import matplotlib.pyplot as plt

def header(file):
    inread = ''
    while True:
        tmp=file.read(1)
        inread = inread + tmp
        flag = inread.find('HEADER_END')
        if flag != -1:
            break
    return inread

def update_headparam(head, parlist, vallist):
    how2parse = {
        'nchans': ('i',4),
        'tsamp': ('d',8),
        'foff': ('d',8),
        'fch1': ('d',8),
        'tstart': ('d',8)
        }
    n = 0
    for i in parlist:
        i1 = head.find(i)
        i2 = i1 + len(i)
        nbytes = how2parse[i][1]
        cstr = how2parse[i][0]

        val = vallist.pop(0)
        val = struct.pack(cstr, val)
        head = head[0:i2] + val + head[i2+nbytes:]
        n += 1
    return head

def flippy(INFILE1,INFILE2,OUTFILE,NCHAN,NSAMP,DTYPE,FLIP):
    blocksize = 10000
    while 1:
        dataIn1 = INFILE1.read(4*NCHAN*blocksize)
        dataIn2 = INFILE2.read(4*NCHAN*blocksize)
        data2fix1 = np.fromstring(dataIn1, dtype=DTYPE)
        data2fix2 = np.fromstring(dataIn2, dtype=DTYPE)
        if len(dataIn1) == 0: break
        FB0 = level_bandpass(data2fix2,NCHAN)
        FB0 = np.fliplr(FB0)
        FB1 = level_bandpass(data2fix1,NCHAN)
        total = np.hstack((FB1,FB0))
        OUTFILE.write(total.flatten())
        '''if FLIP:
            FB0 = level_bandpass(data2fix,NCHAN)
            FB0 = np.fliplr(FB0)
            # DON'T WRITE YET
        else:
            FB1 = level_bandpass(data2fix,NCHAN)
            # DON'T WRITE YET '''

def level_bandpass(DATA,NCHAN):
    DATA = DATA.astype('float32')
    dlen = DATA.shape[0]
    DATA.shape = (dlen/NCHAN,NCHAN)
    # laura's version
    med_spec = np.median(DATA,axis=0)
    std_spec = np.std(DATA,axis=0)
    #flatten
    DATA /= med_spec
    med_flat = np.median(DATA, axis=0)
    std_flat = np.std(DATA, axis=0)
    # calc channel weights, deal with crappy channels
    izero = np.where(med_spec==0)[0]
    ilow = np.where(std_spec<0.5)[0]
    # default weight = 1
    weights = np.ones(NCHAN)
    # if std dev is lower than expected for 1-bit noisy data
    # set weight to stddev
    weights[ilow] = std_spec[ilow]
    weights[izero] = 0
    # apply weights
    DATA *= weights

    med_wght = np.median(DATA, axis=0)
    std_wght = np.std(DATA, axis=0)

    # scale and recast
    scale = 32; offset = 32
    DATA *= scale
    DATA += offset

    med_scale = np.median(DATA, axis=0)
    std_scale = np.std(DATA, axis=0)

    #dflatout = np.cast['uint8'](DATA)

    '''plt.subplot(211)
    plt.plot(med_spec)
    plt.plot(std_spec)
    plt.subplot(212)
    plt.plot(med_flat,'r-')
    plt.plot(std_flat, 'g-')
    plt.plot(med_scale, 'm-')
    plt.plot(std_scale, 'c-')
    plt.show()'''

    # old
    '''bp = np.median(DATA,axis=0)
    np.place(bp, bp == 0, 1)
    DATA /= bp
    DATA *= 32
    DATA += 8'''
    DATA = DATA.astype('uint8')
    return DATA #dflatout #DATA


def main():
    infile1 = open(opts.infile1,'r')
    infile2 = open(opts.infile2,'r')
    outfile = open(opts.outfile,'w')
    head = header(infile1)
    newhead = update_headparam(head, ['fch1'], [8000]) # hardcoded for now
    newhead = update_headparam(newhead, ['foff'], [-abs(opts.bw)])
    newhead = update_headparam(newhead, ['nchans'], [4096]) #hardcoded for now
    headlen = len(head)
    infile1.seek(headlen)
    infile2.seek(headlen)
    outfile.write(newhead)
    flippy(infile1,infile2,outfile,opts.nchan,opts.nsamp,opts.dtype,opts.flip)
    infile1.close()
    infile2.close()
    outfile.close()
    
if __name__=="__main__":
    desc = "Change header parameters (frequency and channel bandwidth), and flip band if needed"
    parser = optparse.OptionParser(description=desc)
    parser.add_option('--infile1',dest='infile1',type='string',\
        help="UPPER BAND: Filterbank file whose header needs to be changed")
    parser.add_option('--infile2',dest='infile2',type='string',\
        help="LOWER BAND: Filterbank file whose header needs to be changed")
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
        mandatories = ['infile1','outfile','freq','bw','nchan','nsamp','dtype']
        for i in mandatories:
            if not opts.__dict__[i]:
                print "If you want to flip the band, I need all the info"
                parser.print_help()
                exit(-1)
    else:
        mandatories = ['infile1','outfile','freq','bw','nchan','nsamp']
        for i in mandatories:
            if not opts.__dict__[i]:
                print "I need --infile1 --outfile --freq --bw --nchan --nsamp"
                parser.print_help()
                exit(-1)
    main()

