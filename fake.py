#!/usr/bin/env python

'''



'''

import os
import numpy as np
import optparse
import filterbank
import sys
import matplotlib.pyplot as plt

def Gaussian(x,FWHM,b,a):
    c = FWHM / (2*np.sqrt(2*np.log(2)))
    I = a * np.exp(-1. * (x - b)**2 / (2.*c**2))
    return I

def onebittophat(x,FWHM,b,SN):
    II = np.zeros_like(x)
    sn = min(.07 * SN,1.)
    y = 1. - sn
    print "sn %f" % sn
    print "y %f" % y
    ones_zeros = np.array([0]*int(y*FWHM) + [1]*int(sn*FWHM))
    print "len ones zeros %f" % len(ones_zeros)
    print "len to insert %f" % len(II[b-int(FWHM/2):b-int(FWHM/2)+len(ones_zeros)])
    np.random.shuffle(ones_zeros)
    II[b-int(FWHM/2):b-int(FWHM/2)+len(ones_zeros)]=ones_zeros
    #II[b-int(FWHM/2):b+int(FWHM/2)]=1
    #return filterbank.unpack_1bit(II)
    return II

def dispdelay(DM,lowfreq,hifreq):
    Dconst = 4.1488e3
    return DM * Dconst * (1./lowfreq**2 - 1./hifreq**2)

def status(n1,n2):
    prog = 100.*n1/n2
    sys.stdout.write("Progress: %3.3f \r" % prog)
    sys.stdout.flush()

def mod_eight(number):
    if np.mod(number,8) == 0 : return number
    else: return number + (8-np.mod(number,8))
    #x = np.mod(number,8)
    #y = 8 - np.mod(number,8)
    #return x + y

def main():
    fb = filterbank.FilterbankFile(opts.inputfb)
    totsamps = fb.N
    #gauss = Gaussian(np.arange(opts.width),opts.FWHM,opts.b,opts.a)
    #mr_hat = onebittophat(np.arange(opts.width),opts.FWHM,opts.b)
    Dconst = 4.1488e3
    freqhi = fb.frequencies.max(); freqlo = fb.frequencies.min()
    tdelay = dispdelay(opts.DM,freqlo,freqhi)
    binsweep = int(tdelay/fb.dt)
    width = int(np.ceil(opts.width/fb.dt))
    fwhm = int(np.ceil(opts.FWHM/fb.dt))
    #if opts.onebit: fwhm = int(np.ceil(opts.width/fb.dt))
    peak_center = int(np.ceil(.5*opts.width/fb.dt))
    #peak_center = int(np.ceil(opts.b/fb.dt))
    Binsert = int(opts.Tinsert/fb.dt) + width/2
    '''if opts.onebit:
        tdelay *= 8
        binsweep *= 8
        width *= 8
        fwhm *= 8
        peak_center *= 8
        Binsert *= 8'''
    print "freqhi %f freqlo %f " % (freqhi,freqlo)
    print "tedlay %f " % tdelay
    print "binsweep %f " % binsweep
    print "binsert %f " % Binsert
    topdownfreqs = np.sort(fb.frequencies)[::-1]
    [nsamps, nchans] = np.shape(fb.get_spectra(Binsert-width/2,Binsert+binsweep+width/2))
    outputfb = os.path.splitext(opts.inputfb)[0] + "_FRB" + os.path.splitext(opts.inputfb)[1]
    if opts.onebit:
        outfil = filterbank.create_filterbank_file(outputfb,fb.header,nbits=1,mode='append')
    else:
        outfil = filterbank.create_filterbank_file(outputfb,fb.header,nbits=fb.nbits,mode='append')
    #fb_spec = np.copy(fb.get_spectra(Binsert-opts.width/2,Binsert
    ### decide how many samples to get for each iteration
    startbin = 0
    #endbin = 5000 
    endbin = 4*binsweep
    if opts.onebit:
        endbin = mod_eight(4*binsweep)    
    '''if opts.onebit:
        endbin = binsweep
    else:
        endbin = 4*binsweep'''
    #if np.mod(endbin,8) != 0:
    #    print "bin range not divisble by 8"
    #    endbin = mod_eight(endbin)
    #    print "bin range now divisible by 8"
    sampread = 1
    print "Total number of samples: %.f" % totsamps
    status(startbin,totsamps)
    #prog = 100.*startbin/totsamps
    #sys.stdout.write("Progress: %3.3f \r" % prog)
    #sys.stdout.flush()
    while sampread:
        #print "startbin: %.f" % startbin
        #print "endbin: %.f" % endbin
        #print "enbin - startbin: %.f" % (endbin-startbin)
        #print "mod endbin-startbin, 8: %.f" % (np.mod(endbin-startbin,8))
        spec = fb.get_spectra(startbin,endbin)
        [samples,channels] = np.shape(spec)
        #print "samples %f " % samples
        #print "channels %f " % channels
        #print np.shape(spec)
        #bla = filterbank.pack_1bit(spec.flatten())
        #print np.shape(bla)
        #break
        sampread = spec.shape[0]
        if (startbin <= Binsert < endbin):
            print "inserting pulse (or trying...)"
            if endbin - Binsert < binsweep:
                if opts.onebit: endbin += mod_eight(binsweep)
                else: endbin += binsweep
                #if np.mod(endbin,8) != 0:
                #    print "endbin not divisble by 8"
                #    endbin = mod_eight(endbin)
                #    print "endbin now divisible by 8"
                spec = fb.get_spectra(startbin,endbin)
                [samples,channels] = np.shape(spec)
                sampread = spec.shape[0]
            ### INSERT PULSE AND MAKE SURE IT FITS THE GAP
            std = np.std(spec,axis=0) # should get 512 (numchans)
            RMS = np.sum(std)/len(std)
            #scale_fac = opts.SN*RMS/nchans
            scale_fac = opts.SN*RMS
            if opts.onebit: scale_fac = opts.SN*RMS
            tmpbinsert = Binsert - startbin
            print "len std %f " % len(std)
            print "rms %f " % RMS
            print "scale fac %f " % scale_fac
            print "tmpbinsert01 %.f " % tmpbinsert
            spec_T = np.transpose(spec)
            #if endbin - Binsert < binsweep: #opts.width:
            #    tmpbinsert = sampread - binsweep #opts.width
            for i in range(nchans):
                tempdelay = dispdelay(opts.DM,topdownfreqs[i],freqhi)
                tempbin = tmpbinsert + int(tempdelay/fb.dt)
                #print "tempbin %.f" % tempbin
                #print "tempdelay %f " % tempdelay
                #print "tempbin %f " % tempbin
                if opts.onebit:
                    #continue
                    #spec_T[i,:] = filterbank.pack_1bit(spec_T[i,:])
                    print "parameters"
                    print "len width %f" % width
                    print "fwhm %f" % fwhm
                    print "peak center %f" % peak_center
                    print "sclae fac %f" % scale_fac
                    print np.arange(width)
                    mr_hat = onebittophat(np.arange(width),fwhm,peak_center,scale_fac)
                    #mr_hat = filterbank.unpack_1bit(mr_hat)
                    #print "shape "
                    #print np.shape(spec_T[i,:][tempbin:tempbin+opts.width])
                    #print np.shape(mr_hat)
                    #print "temp bin %.f" % tempbin
                    #print np.shape(spec_T[i,:])
                    #print "binsert %.f " % Binsert
                    #print "startbin %.f " % startbin
                    #print "endbin %.f " % endbin
                    ###spec_T[i,:][tempbin:tempbin+opts.width*8] += mr_hat
                    #np.add(spec_T[i,:][tempbin:tempbin+width],mr_hat)
                    spec_T[i,:][tempbin:tempbin+width] = spec_T[i,:][tempbin:tempbin+width] + mr_hat
                    spec_T[i,:][tempbin:tempbin+width] = np.where(spec_T[i,:][tempbin:tempbin+width]>1,1,spec_T[i,:][tempbin:tempbin+width])
                    #spec_T[i,:][tempbin:tempbin+width] += mr_hat
                    #spec_T[i,:][tempbin:tempbin+width] = 0
                    #spec_T[i,:][tempbin:tempbin+opts.width] = spec_T[i,:][tempbin:tempbin+opts.width] + mr_hat
                    #np.add(spec_T[i,:][tempbin:tempbin+opts.width],mr_hat)
                    #spec_T[i,:][tempbin:tempbin+opts.width] = np.where(spec_T[i,:][tempbin:tempbin+opts.width]>1,1,spec_T[i,:][tempbin:tempbin+opts.width]) 
                else:
                    #print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                    bla = np.median(spec_T[i,:])
                    #gauss = Gaussian(np.arange(width),fwhm,peak_center,bla*opts.SN)
                    ''' SHIT MIX TO MAKE IT WORK '''
                    ''' START OF SHITMIX '''
                    available_width = len(spec_T[i,:][tempbin:tempbin+width])
                    if width > available_width: width = available_width
                    ''' END OF SHITMIX '''
                    gauss = Gaussian(np.arange(width),fwhm,peak_center,scale_fac)
                    #gauss = Gaussian(np.arange(opts.width),opts.FWHM,opts.b,scale_fac)
                    #spec_T[i,:][tempbin:tempbin+opts.width] = gauss
                    #np.add(spec_T[i,:][tempbin:tempbin+opts.width],gauss)
                    #np.add(spec_T[i,:][tempbin:tempbin+width],gauss)
                    print "tempbin %.f" % tempbin
                    print "len spec %.f" % len(spec_T[i,:])
                    print "width %.f " % width
                    print "binsweep %.f" % binsweep
                    print "binsert %.f" % tmpbinsert
                    print "tmpbin + width %.f " % (tempbin + width)
                    print "tmpbin rest %.f " % (len(spec_T[i,:][tempbin:tempbin+width]))
                    print "available width %.f" % (len(spec_T[i,:][tempbin:]))
                    spec_T[i,:][tempbin:tempbin+width] = spec_T[i,:][tempbin:tempbin+width] + gauss
                    #print spec_T[i,:][tempbin:tempbin+opts.width]
                    #np.add(spec_T[i,:][tmpbinsert:tmpbinsert+opts.width],gauss/nchans)
            #print "gaussian"
            #print gauss
            #print gauss.max()
            #print "spec"
            #print spec_T[-1,:][tempbin:tempbin+opts.width]
            #plt.plot(gauss)
            #plt.show()
            spec_T_T = np.transpose(spec_T)
            if opts.onebit:
                #print np.shape(spec_T_T)
                flat_spec = filterbank.pack_1bit(spec_T_T.flatten())
                #print np.shape(flat_spec)
                flat_spec.shape = len(flat_spec)/512,512
                #flat_spec.shape = samples/8,512 
                outfil.append_spectra(flat_spec)
                #outfil.append_spectra(spec_T_T)
                #status(endbin,totsamps)
            else:
                outfil.append_spectra(spec_T_T)
                #status(endbin,totsamps)
            print "done (I think...)"
        else:
            if opts.onebit:
                if np.shape(spec)[0] != 0:
                    flat_spec = filterbank.pack_1bit(spec.flatten())
                    print len(flat_spec)
                    if np.mod(len(flat_spec),512) != 0: break
                    flat_spec.shape = len(flat_spec)/512,512
                    #flat_spec.shape = samples/8,512
                    outfil.append_spectra(flat_spec)
                    #outfil.append_spectra(spec)
                    #status(endbin,totsamps)
                #prog = 100.*endbin/totsamps
                #sys.stdout.write("Progress: %3.3f \r" % prog)
                #sys.stdout.flush()
            else:
                if np.shape(spec)[0] != 0:
                    outfil.append_spectra(spec)
                    #status(endbin,totsamps)
            #else:
            #    sampread = 0
        status(endbin,totsamps)
        #prog = 100.*endbin/totsamps
        #sys.stdout.write("Progress: %3.3f \r" % prog)
        #sys.stdout.flush()
        startbin += sampread
        endbin += sampread
        #startbin += sampread + 1
        #endbin += sampread + 1
        
        ### if time of inserted pulse is within grabbed spec,
        ### insert it. BUT!!! if it goes outside the specs, need
        ### to figure out how to take care of that

if __name__=='__main__':
    desc = 'meow'
    parser = optparse.OptionParser(description=desc)
    parser.add_option('--filfile',dest='inputfb',type='string',\
        help="Filterbank file to inject the fake FRB")
    parser.add_option('--time','-t',dest='Tinsert',type='float',\
        help="Time in sec where to put fake FRB, default=50s",\
        default=10.) 
    parser.add_option('--dm','-d',dest='DM',type='float',\
        help="DM of injecte signal in pc cm**-3. Default=500 pc cm**-3",\
        default=500.)
    parser.add_option('--is-1bit',dest='onebit',action='store_true',\
        help="Is you data 1-bit?. Default=False",\
        default=False)
    parser.add_option('--nbits',dest='nbits',type='int',\
        help="Data type, not necessary if your data is 1 or 8 bit. redundant... Default=8",\
        default=8)
    #parser.add_option('--width',dest='width',type='int',\
    #    help="Width of gaussian in samples. Default 100",\
    #    default=100)
    parser.add_option('--width',dest='width',type='float',\
        help="Width of gaussian in milliseconds. Default 5 ms",\
        default=5e-3)
    ### CHANGE THIS TO WIDTH IN SECONDS
    #parser.add_option('--FWHM','--fwhm',dest='FWHM',type='int',\
    #    help="FWHM in samples. Default=50",\
    #    default=20)
    parser.add_option('--FWHM','--fwhm',dest='FWHM',type='float',\
        help="FWHM in ms. Default = 3 ms",\
        default=3e-3)
    ### CHANGE THIS TO FWHM IN SECONDS?
    #parser.add_option('-b',dest='b',type='int',\
    #    help="Position of the center of the peak in samples. Default=50",\
    #    default=50)
    parser.add_option('-b',dest='b',type='float',\
        help="Position of the center of the peak in ms. Default= 2.5 ms",\
        default=2.5e-3)
    ### CHANGE THIS TO SECONDS, OR JUST HAVE THE PEAK IN THE CENTER?
    parser.add_option('-a',dest='a',type='float',\
        help="Height of curve's peak. Default=1e14",\
        default=1e14)
    parser.add_option('--SN',dest='SN',type='float',\
        help="Signal to noise. Default=15",\
        default=15)
    ### CHANGE THIS SOMEHOW TO SIGNAL TO NOISE?
    (opts,args) = parser.parse_args()
    main()

