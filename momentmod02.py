# coding = utf-8

# import stuff
import numpy as np
import waterfaller
import rawdata
import filterbank
import os
import sys
from groupie import groupie,groupie2


'''
    trying to redo the momentmod.py with some changes:

    i) do high S/N events outside of groupes

    ii) if DM and time is within group (and possibly S/N),
    take event in singlepulse file closest to central group
    time and do calculations

    NB: done writing the first point, need to find a good way
    to do the second point. FIXED!
    first check if any time and dm is within groups?
    iterate through groups, if time and dm within a group, then
    take event closest to the central group time and do calculations
'''
'''

singlepluse(filterbank file, singlepulse files, single pulse dir, groupdir)
    read sample size from filterbank 
    if any of the single pulses in a single pulse search file is above threshold (e.b. 8.0)
    or that there are high rank groups, create a new singlepulse file.
    finds out the downsampling and finds the maskfile
    iterate through single pulses, if its above S/N threshold or within a group,
    it goes through the waterfaller process

process_stuff(singlepulse dir, new singlepulse dir, single pulse file, downsampling,
                sample size, "raw data file", mask)
    width = downfact * downsampling
    begin = time -.5 * width * sampsize
    duration = width * sample size
    waterfall that stuff
    duration_median = 0.1 
    waterfall the duration of median, is it too large? might cause code to be too slow
    If number of bits is 1 or 8
        1: mean over median data and number of bins
        subtract mean from data
        8: median of median data and number of bins
        divide data by median and subtract 1
        if median value is 0 somewhere, I change it to 1
    calculate moments and modulation index (and skewness and kurtosis)
    see Laura's paper for equations


'''
def singleplus(FIL,SPFILES,SPDIR,GRPDIR):
    sampsize = filterbank.FilterbankFile(FIL).dt # READ SAMPLE SIZE FROM FILTERBANK
    rawdatafile = rawdata.initialize_rawdata(FIL) # INITIALIZE FOR WATERFALLER
    NEWSPDIR = SPDIR + "_NEWSPs/" # CREATE DIR FOR JUICY EVENTS
    os.system("mkdir " + NEWSPDIR)
    for y in range(len(SPFILES)):
        print SPFILES[y]
        #print GRPDIR
        # IF SINGLEPULSE FILE IS EMPTY OR HAS ONLY ONE LINE, MAKES SURE THIS DOESN'T CRASH
        if (os.stat(SPDIR + SPFILES[y] + ".singlepulse").st_size == 0): continue
        spdata = np.loadtxt(SPDIR + SPFILES[y] + ".singlepulse",skiprows=1)
        if not spdata.any(): continue
        if spdata.ndim == 1:
            spdata = np.reshape(spdata,(1,len(spdata)))
        # IF ANYTHING WORTHY IS IN THE SINGLEPULSE FILE, CREATE NEW SINGLEPULSE FILE
        if any(SNval >= 8.0 for SNval in spdata[:,1]) or groupie2(spdata[:,2],spdata[0,0],GRPDIR)[0]:
            ff = open(NEWSPDIR + "NEW" + SPFILES[y] + ".singlepulse",'w')
            astring = "# DM\t Sigma\t Time(s)\t Sample\t Downfact\t m_I\t I1\t I2\t I3\t I4\t kurt\t skew\n"
            ff.write(astring)
            ff.close()
            with open(SPDIR + SPFILES[y] + ".inf",'r') as inffile:
                lines = inffile.readlines()
                for i,line in enumerate(lines):
                    if "Width of each" in line:
                        downsampline = line # FIND OUT THE DOWNSAMPLING FROM THE INF FILE
            current_ds = float(downsampline.split()[-1])/sampsize # DOWNSAMPLING
            maskbase = os.path.splitext(os.path.basename(FIL))[0]
            mask = os.path.join(GRPDIR,maskbase + "_rfifind.mask")
            for n in range(len(spdata[:,0])): # HIGH SN EVENTS OUTSIDE GROUPS PROCESSED
                if (spdata[n,1]>=8.0 and not groupie(spdata[n,2],spdata[n,0],GRPDIR)):
                    PROCESS_STUFF(SPDIR,NEWSPDIR,SPFILES[y],spdata[n,:],current_ds,sampsize,rawdatafile,mask)
            if (groupie2(spdata[:,2],spdata[0,0],GRPDIR)[0]): # GOOD RANK GROUPS PROCESSED
                central_times = groupie2(spdata[:,2],spdata[0,0],GRPDIR)[1]
                for timele in central_times: # FIND EVENT CLOSEST TO CENTRAL TIME OF GROUP
                    idx = (np.abs(spdata[:,2]-timele)).argmin()
                    if (spdata[idx,1]<7): continue # IF THE SN IS TOO LOW, WE DON'T WANT IT
                    PROCESS_STUFF(SPDIR,NEWSPDIR,SPFILES[y],spdata[idx,:],current_ds,sampsize,rawdatafile,mask)

# THIS "PROCESSES" STUFF, I.E. UTILIZES WATERFALLER.PY TO GET DATA AND COMPUTE
# THE MOMENTS AND MODULATION INDEX AND THEN WRITES IT TO THE NEW SINGLEPULSE FILE
def PROCESS_STUFF(SPDIR,NEWSPDIR,SPFILE,SPDATALINE,DOWNSAMP,SAMPSIZE,RAWDATAFILE,MASK):
    ff = open(NEWSPDIR + "NEW" + SPFILE + ".singlepulse",'a')
    ff.write("  ")
    ff.write("%f %f %f %d %d " % (SPDATALINE[0],SPDATALINE[1],SPDATALINE[2],SPDATALINE[3],SPDATALINE[4]))
    width = SPDATALINE[4] * DOWNSAMP
    begin = SPDATALINE[2] - (.5 * width * SAMPSIZE)
    dur = width * SAMPSIZE
    data, bins, nbins, start = waterfaller.waterfall(RAWDATAFILE, \
            begin, dur, dm=SPDATALINE[0],mask=True,maskfn=MASK)
    dur_median = .1
    begin2 = SPDATALINE[2] - .5 * dur_median
    data2, bins2, nbins2, start2 = waterfaller.waterfall(RAWDATAFILE, \
            begin2, dur_median, dm=SPDATALINE[0],mask=True,maskfn=MASK)
    I = np.empty_like(data.data[:,0:nbins])
    #bits = 1
    bits = 8 # change this so because the data I'm working on is 8-bit
    if (bits == 1):
        onebit_mean = np.mean(data2.data[:,0:nbins2],axis=1)
        I = data.data[:,0:nbins]
        onebit_mean.shape = (len(onebit_mean),1)
        I -= onebit_mean
    else:
        medi = np.median(data2.data[:,0:nbins2],axis=1)
        I = data.data[:,0:nbins]
        medi.shape = (len(medi),1)
        medi[np.where(medi==0.)]=1.
        I /= medi
        I -= 1 
    one = sum(I.sum(1)); two = sum(I.sum(1)**2)
    three = sum(I.sum(1)**3); four = sum(I.sum(1)**4)
    I_moms = np.array([one,two,three,four])/float(data.numchans)
    m_I = np.sqrt((I_moms[1] - I_moms[0]**2)/I_moms[0]**2)
    kurtosis = I_moms[3]/I_moms[1]**2
    skewness = I_moms[2]/I_moms[1]**(1.5)
    ff.write("%.4f \t %.4e \t %.4e \t %.4e \t %.4e \t %.4f \t %.4f" \
            % (m_I, I_moms[0], I_moms[1], I_moms[2], I_moms[3], kurtosis, skewness))
    ff.write("\n")
    ff.close()

if __name__=="__main__":
    filt = sys.argv[1]
    singlepulsedir = sys.argv[2]
    grpdir = sys.argv[3]
    spdir_files = []
    for (dirpath,dirnames,filenames) in os.walk(singlepulsedir):
        spdir_files.extend(filenames)
        break
    spfiles = []
    for i in range(len(spdir_files)):
        tmpfilename = ['.'.join(spdir_files[i].split('.')[0:-1]),spdir_files[i].split('.')[-1]]
        if (tmpfilename[-1]=='singlepulse'):
            spfiles.append(tmpfilename[0])
    singleplus(filt,spfiles,singlepulsedir,grpdir)



'''for n in range(len(spdata[:,0])):
    if (spdata[n,1]>=15.0 and not groupie(spdata[n,2],GRPDIR)):
        ff.write("  ")
        ff.write("%f %f %f %d %d " % (spdata[n,0],spdata[n,1],spdata[n,2],spdata[n,3],spdata[n,4]))
        with open(SPDIR + SPFILES[y] + ".inf",'r') as inffile:
            lines = inffile.readlines()
            for i,line in enumerate(lines):
                if "Width of each" in line:
                    downsampline = line
        current_ds = float(downsampline.split()[-1])/sampsize
        print "***Data parameters***"
        print "Current downsample: ", current_ds
        print "Sample time: ", sampsize
        width = spdata[n,4] * current_ds
        begin = spdata[n,2] - (.5 * width * sampsize)
        print "Calculating for event at %f with S/N %f" % (spdata[n,2],spdata[n,1])
        dur = width * sampsize
        data, bins, nbins, start = waterfaller.waterfall(rawdatafile, \
                begin, dur, dm=spdata[n,0])
        print "***Narrow window parameters***"
        print "bins, nbins, start", bins, nbins, start
        print "data shape", data.data.shape
        print "begin, dur", begin, dur
        dur_median = .1
        begin2 = spdata[n,2] - 0.5 * dur_median
        data2, bins2, nbins2, start2 = waterfaller.waterfall(rawdatafile, \
                begin2, dur_median, dm=spdata[n,0])
        print "***Wider window parameters***"
        print "bins, nbins, start", bins2, nbins2, start2
        print "d2 shape", data2.data.shape
        print "begin, dur median", begin2, dur_median
        I = np.empty_like(data.data[:,0:nbins])
        bits = 1
        if (bits == 1):
            onebit_mean = np.mean(data2.data[:,0:nbins2],axis=1)
            I = data.data[:,0:nbins]
            onebit_mean.shape=(len(onebit_mean),1)
            I -= onebit_mean
        else:
            medi = np.median(data2.data[:,0:nbins2],axis=1)
            I = data.data[:,0,nbins]
            medi.shape=(len(medi),1)
            I /= medi
            I -= 1
        print "I shape ", I.shape
        one = sum(I.sum(1)); two = sum(I.sum(1)**2)
        three = sum(I.sum(1)**3); four = sum(I.sum(1)**4)
        print "mean(I.sum(1))", np.mean(I.sum(1))
        print "one ", one
        I_moms = np.array([one,two,three,four])/float(data.numchans)
        print float(data.numchans)
        print "%.4e" % I_moms[0]
        m_I = np.sqrt((I_moms[1] - I_moms[0]**2)/I_moms[0]**2)
        kurtosis = I_moms[3]/I_moms[1]**2
        skewness = I_moms[2]/I_moms[1]**(1.5)
        ff.write("%.4f \t %.4e \t %.4e \t %.4e \t %.4e \t %.4f \t %.4f" \
                % (m_I, I_moms[0], I_moms[1], I_moms[2], I_moms[3], kurtosis, skewness))
        ff.write("\n")
if (groupie2(spdata[:,2],spdata[0,0],GRPDIR)[0]): 
    print "AN EVENT IN THIS SINGLEPULSE FILE IS IN A GROUP"
    central_times = groupie2(spdata[:,2],spdata[0,0],GRPDIR)[1]
    print "NUMBER OF GROUPS", len(central_times)
    xxx = 0
    for timele in central_times:
        idx = (np.abs(spdata[:,2]-timele)).argmin()
        #print "PERFORM STUFF ON EVENT WITH INDEX", idx
        # spdata[idx,bla] etc...
        xxx += 1
    print "NUMBER OF EVENTS IN A GROUP FOR THIS FILE", xxx
#ff.close()'''
# write the waterfaller stuff as a def I can call
