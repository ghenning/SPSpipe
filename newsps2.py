import numpy as np
import os
import filterbank
import rawdata
import waterfaller
from groupie import groupie
import plotmaster

def get_spsfiles(DIR):
    spdir_files = []
    for (dirpath,dirnames,filenames) in os.walk(spdir):
        spdir_files.extend(filenames)
        break
    sp_files = []
    for i in range(len(spdir_files)):
        tmpfilename = ['.'.join(spdir_files[i].split('.')[0:-1]),spdir_files[i].split('.')[-1]]
        if (tmpfilename[-1]=='singlepulse'):
            sp_files.append(tmpfilename[0])
    return sp_files

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
        if spdata.ndim==1:
            spdata = np.reshape(spdata,(1,len(spdata)))
        with open(SPDIR + SPFILES[y] + ".inf",'r') as inffile:
            lines = inffile.readlines()
            for i,line in enumerate(lines):
                if "Width of each" in line:
                    downsampline = line
        current_ds = int(float(downsampline.split()[-1])/sampsize)
        for n in range(len(spdata[:,0])):
            ff = open(megaspsfile,'a')
            if (spdata[n,1]>=5.0 and not groupie(spdata[n,2],spdata[n,0],GRPDIR)):
                DM = spdata[n,0]; Sig = spdata[n,1]; Tim = spdata[n,2]
                Samp = spdata[n,3]; Downf = spdata[n,4]; Downs = current_ds
                ff.write("%.1f \t %.2f \t %f \t %d \t %d \t %d \n" % (DM, Sig, Tim, Samp, Downf, Downs))
            ff.close()
    goodsps = np.loadtxt(megaspsfile)
    if goodsps.any():
        goodsps = goodsps[goodsps[:,2].argsort()]
    else:
        goodsps = np.zeros((1,6))
    megaspsfile_sorted = os.path.join(GRPDIR,"goodsps_sorted.txt")
    head = "DM \t Sigma \t Time(s) \t Sample \t Downfact \t Downsamp"
    formt = "%.1f \t %.2f \t %f \t %d \t %d \t %d"
    np.savetxt(megaspsfile_sorted,goodsps,fmt = formt, header = head)
    return sampsize,rawdatafile

def gullfoss(FIL,RAWDATAFILE,GRPDIR,SAMPSIZE):
    megaspsfile = os.path.join(GRPDIR,"goodsps_sorted.txt")
    goodsps = np.loadtxt(megaspsfile)
    if not goodsps.any():
        print "######################"
        print "No good single pulses"
        print "######################"
        return 0
    waterfall_cands = np.zeros((1,6))
    elecounter = 0
    while elecounter<len(goodsps):
        timgrp, = np.where(abs(goodsps[elecounter:,2]-2.)<=goodsps[elecounter,2])
        timgrp += elecounter
        try:
            maxval, = np.where(goodsps[timgrp,1]==goodsps[timgrp,1].max())
        except ValueError:
            added_time = int(2/SAMPSIZE)
            elecounter += added_time
            ###elecounter = timgrp[-1] + 1
            continue
            ###maxval = 0
            ###pass
        maxval += elecounter
        waterfall_cands = np.append(waterfall_cands,goodsps[maxval],axis=0)
        elecounter = timgrp[-1] + 1
    waterfall_cands = np.delete(waterfall_cands,0,0)
    o = os.path.join(GRPDIR,"waterfall_cands.txt")
    head = "DM \t Sigma \t Time(s) \t Sample \t Downfact \t Downsamp"
    formt = "%.1f \t %.2f \t %f \t %d \t %d \t %d"
    np.savetxt(o,waterfall_cands,fmt = formt, header = head)
    waterfall_res = np.zeros((1,13))
    maskbase = os.path.splitext(os.path.basename(FIL))[0]
    mask = os.path.join(GRPDIR,maskbase + "_rfifind.mask")
    for i in range(len(waterfall_cands)):
        DM = waterfall_cands[i,0]
        downsamp = waterfall_cands[i,5]
        width = waterfall_cands[i,4] * downsamp
        begin = waterfall_cands[i,4] - (.5 * width * SAMPSIZE)
        dur = width * SAMPSIZE
        dur_median = .1
        begin2 = waterfall_cands[i,2] - .5 * dur_median
        data, bins, nbins, start = waterfaller.waterfall(RAWDATAFILE, \
            begin, dur, dm = DM, mask=True, maskfn=mask)
        data2, bins2, nbins2, start2 = waterfaller.waterfall(RAWDATAFILE, \
            begin2, dur_median, dm = DM, mask=True, maskfn=mask)
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
        waterfall_res = np.append(waterfall_res,extended_cand,axis=0)
    waterfall_res = np.delete(waterfall_res,0,0)
    o2 = os.path.join(GRPDIR,"waterfall_result.txt")
    head2 = "DM \t Sigma \t Time(s) \t Sample \t Downfact \t Downsamp \t m_I \t I1 \t I2 \t I3 \t I4 \t kurt \t skew"
    formt2 = "%.1f \t %.2f \t %f \t %d \t %d \t %d \t %.3f \t %.3e \t %.3e \t %.3e \t %.3e \t %.3f \t %.3f"
    np.savetxt(o2,waterfall_res,fmt = formt2, header = head2)
    return len(waterfall_cands)

'''fil = '/data/sbeam_8bit_FRBs.fil'
spdir = '/data/results2/sbeam_8bit_FRBs/prepsub/'
grpdir = '/data/results2/sbeam_8bit_FRBs/'

the_files = get_spsfiles(spdir)

SAMPSIZE, RAWDATAFILE = giantsps(fil,the_files,spdir,grpdir)

gullfoss(fil,RAWDATAFILE,grpdir,SAMPSIZE)

plotmaster.gathersps2(spdir,grpdir)

plotmaster.plotstuff(grpdir,fil)
'''
