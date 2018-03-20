# coding = utf-8
'''

Comments Nov 2017

reads NEW sps files and creates EventSummary.txt

NB: SN THRESHOLD, MIGHT BE WHY REPEATER WAS BLUE, ADD IT AS ONE OF THE INPUTS???
    NEED TO ADJUST/FIX

'''
'''
    READS THE NEWsinglepulse FILES AND CREATES A NEW
    FILE CALLED EventSummary.txt 
    IT READS THE NUMBER OF CHANNELS FROM THE FILTERBANK TO
    COMPUTE THE MODULATION INDEX THRESHOLD:

    m_IT = sqrt(NCHAN)/SNthresh

    WHERE SNthresh IS A S/N THRESHOLD THAT WE CHOOSE

    THE EventSummary.txt FILE COLLECTS ALL THE EVENTS FROM 
    THE NEWsinglepulse FILES THAT HAVE MODULATION INDEXES 
    BELOW THE THRESHOLD

'''

import numpy as np
import filterbank
import os
import sys

def spsum(FIL,NEWSPDIR,OUTDIR,SORTER):
    allevents = np.zeros((1,12))
    numchan = filterbank.FilterbankFile(FIL).nchan # number of channels
    SNthresh = 10. # SIGNAL TO NOISE THRESHOLD
    m_IT = np.sqrt(numchan)/SNthresh # modulation index threshold
    dot = '.' # define dot to make life easier in the code below
    newspdir_files = []
    for (dirpath,dirnames,filenames) in os.walk(NEWSPDIR):
        newspdir_files.extend(filenames)
        break
    newsp_files = []
    for i in range(len(newspdir_files)):
        tmpfilename = [dot.join(newspdir_files[i].split(dot)[0:-1]),newspdir_files[i].split(dot)[-1]]
        if (tmpfilename[-1]=='singlepulse'):
            newsp_files.append(tmpfilename[0])
    for y in range(len(newsp_files)):
        newspdata = np.loadtxt(NEWSPDIR + newsp_files[y] + ".singlepulse",skiprows=1)
        if not newspdata.any(): continue
        if newspdata.ndim == 1:
            newspdata = np.reshape(newspdata,(1,len(newspdata)))
        allevents = np.append(allevents,newspdata,axis=0)
    allevents = np.delete(allevents,0,0) # delete the zeros at the beginning
    if allevents.ndim == 1:
        allevents = np.reshape(allevents,(1,len(allevents))) # if only one line
    cutevents = np.zeros((1,12))
    for i in range(len(allevents[:,0])):
        m = allevents[i,5]
        if (m <= m_IT): # if modulation index is below threshold, add to list of events
            print "success"
            tmpline = np.reshape(allevents[i],(1,len(allevents[i])))
            cutevents = np.append(cutevents,tmpline,axis=0)
    cutevents = np.delete(cutevents,0,0) # delete zeros at beginning
    if cutevents.ndim == 1:
        cutevents = np.reshape(cutevents,(1,len(cutevents))) # if only one line
    if (SORTER.lower()=="t" or "time"):#"dm"):
        sortingno = 2 #0
    elif (SORTER.lower()=="sn" or "s/n"):
        sortingno = 1
    elif (SORTER.lower()=="dm"): #"t" or "time"):
        sortingno = 0
    elif (SORTER.lower()=="m" or "m_i"):
        sortingno = 5
    else: sortingno = 2
    cutevents = cutevents[cutevents[:,sortingno].argsort()]
    # for some reason the elif statements only give us one and zero...
    print sortingno
    print SORTER
    with open(OUTDIR + "EventSummary.txt",'w') as sumfile:
        astring = "# DM\t Sigma\t Time(s)\t Sample\t Downfact\t m_I\t I1\t I2\t I3\t I4\t kurt\t skew\n"
        sumfile.write(astring)
        for i in range(len(cutevents[:,0])):
            sumfile.write("  ")
            sumfile.write("%7.2f %7.2f %13.6f %10d %3d %.4f %.4e %.4e %.4e %.4e %.4f %.4f \n" \
                    % (cutevents[i,0], cutevents[i,1], cutevents[i,2], cutevents[i,3], cutevents[i,4], \
                    cutevents[i,5], cutevents[i,6], cutevents[i,7], cutevents[i,8], cutevents[i,9], \
                    cutevents[i,10], cutevents[i,11]))
    return len(cutevents[:,0])

if __name__=="__main__":
    FIL = sys.argv[1]
    NEWSPDIR = sys.argv[2]
    OUTDIR = sys.argv[3]
    #SORTER = sys.argv[4]
    SORTER = "t"
    spsum(FIL,NEWSPDIR,OUTDIR,SORTER)
