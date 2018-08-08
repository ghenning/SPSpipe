import numpy as np
import os
import filterbank
from groupie import groupie
import rawdata
import waterfaller

'''
    DOWNSAMPLING IS GIVING 15 not 16, SEE CALCULATIONS AND FIX!!!
'''

fil = '/data/sbeam_8bit_FRBs.fil'
spdir = '/data/results2/sbeam_8bit_FRBs/prepsub/'
grpdir = '/data/results2/sbeam_8bit_FRBs/'

spdir_files = []
for (dirpath,dirnames,filenames) in os.walk(spdir):
    spdir_files.extend(filenames)
    break

sp_files = []
for i in range(len(spdir_files)):
    tmpfilename = ['.'.join(spdir_files[i].split('.')[0:-1]),spdir_files[i].split('.')[-1]]
    if (tmpfilename[-1]=='singlepulse'):
        sp_files.append(tmpfilename[0])


def giantsps(FIL,SPFILES,SPDIR,GRPDIR):
    sampsize = filterbank.FilterbankFile(FIL).dt
    rawdatafile = rawdata.initialize_rawdata(FIL)
    megaspsfile = os.path.join(GRPDIR,"goodsps.txt")
    ff = open(megaspsfile,'w')
    headerstring = "# DM \t Sigma \t Time(s) \t Sample \t Downfact \t Downsamp \n"
    ff.write(headerstring)
    ff.close()
    for y in range(len(SPFILES)):
        if (os.stat(SPDIR + SPFILES[y] + ".singlepulse").st_size==0): continue
        spdata = np.loadtxt(SPDIR + SPFILES[y] + ".singlepulse")
        if not spdata.any(): continue
        if spdata.ndim == 1:
            spdata = np.reshape(spdata,(1,len(spdata)))
        with open(SPDIR + SPFILES[y] + ".inf",'r') as inffile:
            lines = inffile.readlines()
            for i,line in enumerate(lines):
                if "Width of each" in line:
                    downsampline = line
        current_ds = int(float(downsampline.split()[-1])/sampsize) #WHY AM I GETTING 15 INSTEAD OF 16???
        for n in range(len(spdata[:,0])):
            ff = open(megaspsfile,'a')
            if (spdata[n,1]>=10.0 and not groupie(spdata[n,2],spdata[n,0],GRPDIR)):# AND NOT IN GROUP 2!!! and not groupie(spdata[n,2],spdata[n,0],GRPDIR)):
                DM = spdata[n,0]; Sig = spdata[n,1]; Tim = spdata[n,2]
                Samp = spdata[n,3]; Downf = spdata[n,4]; Downs = current_ds
                ff.write("%.1f \t %.2f \t %f \t %d \t %d \t %d \n" % (DM, Sig, Tim, Samp, Downf, Downs))
            #ff = open(megaspsfile,'a')
            #ff.write("%.1f \t %.2f \t %f \t %d \t %d \t %d \n" % (DM, Sig, Tim, Samp, Downf, Downs))
            ff.close()
    goodsps = np.loadtxt(megaspsfile)
    goodsps = goodsps[goodsps[:,2].argsort()]
    megaspsfile_sorted = os.path.join(GRPDIR,"goodsps_sorted.txt")
    head = "DM \t Sigma \t Time(s) \t Sample \t Downfact \t Downsamp"
    formt = "%.1f \t %.2f \t %f \t %d \t %d \t %d"
    np.savetxt(megaspsfile_sorted,goodsps,fmt = formt, header = head)
    waterfall_cands = np.zeros((1,6))
    elecounter = 0
    while elecounter<len(goodsps):
        timgrp, = np.where(abs(goodsps[elecounter:,2]-1.)<=goodsps[elecounter,2])
        timgrp += elecounter
        #elecounter = timgrp[-1] + 1
        maxval, = np.where(goodsps[timgrp,1]==goodsps[timgrp,1].max())
        maxval += elecounter
        # waterfall maxval!
        waterfall_cands = np.append(waterfall_cands,goodsps[maxval],axis=0)
        elecounter = timgrp[-1] + 1
    waterfall_cands = np.delete(waterfall_cands,0,0)
    o = os.path.join(GRPDIR,"waterfall_cands.txt")
    np.savetxt(o,waterfall_cands,fmt = formt, header = head)
    waterfall_res = np.zeros((1,13))
    # FIND MASK!!! found it
    maskbase = os.path.splitext(os.path.basename(FIL))[0]
    MASK = os.path.join(GRPDIR,maskbase + "_rfifind.mask")
    for i in range(len(waterfall_cands)):
        DM = waterfall_cands[i,0]
        downsamp = waterfall_cands[i,5]
        width = waterfall_cands[i,4] * downsamp
        begin = waterfall_cands[i,2] - (.5 * width * sampsize)
        dur = width * sampsize
        dur_median = .1
        begin2 = waterfall_cands[i,2] -.5 * dur_median
        data, bins, nbins, start = waterfaller.waterfall(rawdatafile, \
            begin, dur, dm = DM, mask=True, maskfn=MASK) # 
        data2, bins2, nbins2, start2 = waterfaller.waterfall(rawdatafile, \
            begin2, dur_median, dm = DM, mask=True, maskfn=MASK)
        I = np.empty_like(data.data[:,0:nbins])
        #bits = 1
        bits = 8
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
        extended_cand = np.append(waterfall_cands[i,:],[m_I, I_moms[0], I_moms[1], I_moms[2], I_moms[3], kurtosis, skewness])
        extended_cand.shape = (1,13)
        #print "extended cand"
        #print extended_cand
        #print "shape extended_cand and waterfall_res:"
        #print np.shape(extended_cand)
        #print np.shape(waterfall_res)
        waterfall_res = np.append(waterfall_res,extended_cand,axis=0)
    waterfall_res = np.delete(waterfall_res,0,0)
    o2 = os.path.join(GRPDIR,"waterfall_result.txt")
    head2 = "DM \t Sigma \t Time(s) \t Sample \t Downfact \t Downsamp \t m_I \t I1 \t I2 \t I3 \t I4 \t kurt \t skew"
    formt2 = "%.1f \t %.2f \t %f \t %d \t %d \t %d \t %.3f \t %.2f \t %.2f \t %.2f \t %.2f \t %.3f \t %.3f"
    np.savetxt(o2,waterfall_res,fmt = formt2, header = head2)
#def PROCESS_CAND(): # make this the waterfaller part later on (more fancy and handy)
    
    '''
    what's next?
    find groups of SPSs, how exactly?
    y = np.where(a[:,1]==a[x,1].max())
    x = np.where(abs([a,2]-1.)<=a[0,2])
    xx, = np.where(abs(a[:,2]-1.)<=a[0,2]) # can iterate through xx, not x, e.g. xx[-1]
    # goodsps[y] is where the max value is in that time group, waterfall that bastard.
    a is goodsps

    '''
    #the_thing = np.loadtxt(megaspsfile)
    #the_thing = the_thing[the_thing[:,2].argsort()]
    #ff = open(megaspsfile,'w')
    #ff.write(headerstring)
    #ff.write(the_thing)
    #ff.close()

giantsps(fil,sp_files,spdir,grpdir)


