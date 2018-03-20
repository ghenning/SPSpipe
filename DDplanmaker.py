import os
import filterbank
import numpy as np


'''
    DDplan.py

    -l : low DM; -d : high DM; -s : subbands; -n : channels
    -f :center freq.; -b : bandwidth; -t : sample time
    -r . acceptable time resolution (ms)

    run this on one fil file for the 47T data set, and
    the processing for each file reads that output.
'''
'''

Comments Nov 2017

create DDplan
    reads info from filterbank file
    runs DDplan
        -l low DM
        -d high DM
        -s subbands (numchan/8)
        -n numchans
        -f central freq.
        -b bandwidth
        -t sample time
        -r 0.1 (cx), 1.0 (47T) [acceptable time resolution (ms) need to find out what exactly that means]
        -o outfile
read_DDplan(path)
    reads the values of DDplan
remove_DDfiles(path)
    removes DDplan files (reduce cluttering)


'''

def create_DDplan(OUTDIR,FILFILE,DDLO,DDHI):
    thefil = filterbank.FilterbankFile(FILFILE)
    numchan = thefil.nchan
    subb = int(numchan/8)
    freqs = thefil.frequencies
    central_freq = np.median(freqs)
    bandw = np.abs(freqs[0]-freqs[-1])
    samptime = thefil.tsamp

    filly = FILFILE.split('.')[0].split('/')[-1]

    DDtxt = "DDtxtfile" + filly + ".txt"
    DDpath = os.path.join(OUTDIR,DDtxt)
    DDeps = "outTrashDD" + filly
    DDout = os.path.join(OUTDIR,DDeps)

    DDcomm = "DDplan.py -l " + str(int(DDLO)) + \
            " -d " + str(int(DDHI)) + \
            " -s " + str(subb) + \
            " -n " + str(int(numchan)) + \
            " -f " + str(central_freq) + \
            " -b " + str(bandw) + \
            " -t " + str(samptime) + \
            " -r " + str(0.1) + \
            " -o " + DDout + \
            " > " + DDpath

    os.system(DDcomm)
    return DDpath


def read_DDplan(PATH):
    f = open(PATH,'r')
    lines = f.readlines()
    deleters = []
    DDresults = np.zeros([15,9])
    for i,line in enumerate(lines):
        if 'WorkFract' in line:
            DDstartpoint = i + 1

    for i,line in enumerate(lines[DDstartpoint:-1]):
        if not lines[DDstartpoint+i].split():
            break
        for j in range(len(lines[DDstartpoint].split())):
            DDresults[i,j] = float(lines[DDstartpoint+i].split()[j])

    for i,line in enumerate(DDresults):
        if not line.any():
            deleters.append(i)

    for x in reversed(deleters):
        DDresults = np.delete(DDresults,x,0)

    f.close()

    return DDresults

def remove_DDfiles(PATH): # insert path to DD txt file, removes txt file and eps file
    textfile = PATH
    extensionless = PATH.split('.')[0]
    epsfile = "outTrashDD" + extensionless.split('DDtxtfile')[-1] + ".eps"
    thepath = os.path.dirname(PATH)
    theepsfile = os.path.join(thepath,epsfile)
    #epsfile = extensionless + ".eps"
    os.system("rm " + textfile)
    print "removed DDplan file: "
    print textfile
    os.system("rm " + theepsfile)
    print "removed DDplan file: "
    print epsfile
    
   
if __name__=='__main__':
    thedir = '/data/tmp/results'
    filfile = '/data/47T135_4.fil'
    DDlo = 0
    DDhi = 4000
    x = create_DDplan(thedir,filfile,DDlo,DDhi)
    res = read_DDplan(x)
    print "Low DM:"
    print res[:,0]
    print "High DM:"
    print res[:,1]
    print "dDM:"
    print res[:,2]
    print "Downsampling:"
    print res[:,3]
    print "dsubDM:"
    print res[:,4]
    print "Number of DMs:"
    print res[:,5]
    print "DMs per call:"
    print res[:,6]
    print "Calls:"
    print res[:,7]
    print "numjobs:"
    print len(res[:,0])
