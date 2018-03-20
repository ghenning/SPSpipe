#!/usr/bin/env python

'''
    use parameters to find out how many bins I need, then just read those bins in with 
        fb_spec = np.copy(fb.get_spectra(START,STOP))
    and throw in gaussian/tophat into those bins

    test and see how it works
'''

"""
Inject fake FRBs into filterbanks

Injects gaussian to 8-bit data, and a top-hat to 1-bit data

NB: This reads the whole damn file, so I've just used it on
very short data files (minutes). In order to make this more
cool and practical, I should clip the original data file into
three pieces, with the middle one being very short, and injecting
the fake FRB into that piece. That would take a very short time,
and then I would simply glue back together the pieces to get
the original data file with a fake FRB. This could be a pet 
project later on if I have time.

Reworked version of Pablo & Leon FRBinject 2015
Henning, MPIfR, 2017
"""

import os
import numpy as np
#import imp # loads external python modules/classes
import optparse
import filterbank

desc = 'meow'

parser = optparse.OptionParser(description=desc)

parser.add_option('--filfile', dest='inputfb', type='string', \
        help="Filterbank file to inject the fake FRB")

parser.add_option('--time', '-t', dest='Tinsert', type='float', \
        help="Time in sec where to put fake FRB. Default=50 s", \
        default=50.)

parser.add_option('--dm', '-d', dest='DM', type='float', \
        help="DM of injected signal in pc cm**-3. Defaul=500 pc cm**-3", \
        default=500.)

parser.add_option('--is-1bit', dest='onebit', action='store_true', \
        help="Is your data 1-bit?. Default=False", \
        default=False)

parser.add_option('--nbits', dest='nbits', type='int', \
        help="Data type, not necessary if your data is 1 or 8 bit. Default=8", \
        default=8)

parser.add_option('--width', dest='width', type='int', \
        help="Width of gaussian in samples. Default=100", \
        default=100)

parser.add_option('--FWHM', '--fwhm', dest='FWHM', type='int', \
        help="FWHM in samples. Default=20", \
        default=20)

parser.add_option('-b', dest='b', type='int', \
        help="Position of the center of the peak in samples. Default=50", \
        default=50)

parser.add_option('-a', dest='a', type='float', \
        help="Height of curve's peak. Default=1e12", \
        default=1e12)

(opts,args) = parser.parse_args()

# time
# gaussian: width, FWHM, b=where in width the top is, a=intensity
# tophat: width, FWHM, b
# DM


def Gaussian(x,FWHM,b,a): # From Leon's FRBfaker
    c = FWHM / (2*np.sqrt(2*np.log(2)))
    I = a * np.exp(-1. * (x - b)**2 / (2.*c**2))
    return I

def onebittophat(x,FWHM,b):
    II = np.zeros_like(x)
    II[b-int(FWHM/2):b+int(FWHM/2)]=1
    return II

# Gaussian FAKE profile = FRB!
gauss = Gaussian(np.arange(opts.width), opts.FWHM, opts.b, opts.a)
mr_hat = onebittophat(np.arange(opts.width), opts.FWHM, opts.b)
#gauss = Gaussian(np.arange(100), 20, 50, 1e12) # gaussian for 8-bit
#mr_hat = onebittophat(np.arange(100),5,50) # top-hat for 1-bit

# WORK ON THE FILTERBANK:

#inputfb = '47T131_1_0_1250000.fil'
fb = filterbank.FilterbankFile(opts.inputfb)
[nsamps, nchans] = np.shape(fb.get_spectra(0,1e9))
outputfb = opts.inputfb.split('/')[-1].split('.fil')[0]+"_FRB.fil"

# To work on the timeseries of the filterbank we need to transpose it first
fb_spec = np.copy(fb.get_spectra(0,1e9))

'''
    need to transpose fb_spec, then iterate through channels, and throw in the
    gaussian in each channel at the appropriate time.
'''
def dispdelay(DM,lowfreq,hifreq):
    Dconst = 4.1488e3
    return DM * Dconst * (1./lowfreq**2 - 1./hifreq**2)


#opts.DM = 500. ; 
Dconst = 4.1488e3 # desired DM; dispersion constant
freqhi = fb.frequencies[0]; freqlo = fb.frequencies[-1] # highest frequency; lowest freq.
tdelay = dispdelay(opts.DM,freqlo,freqhi)
#tdelay = DM * Dconst * (1./freqlo**2 - 1./freqhi**2) # time delay
binsweep = int(tdelay/fb.dt) # time delay in bins, i.e. DM sweep in bins
#opts.Tinsert = 65. # where to insert FRB
Binsert = int(opts.Tinsert/fb.dt) # where to insert FRB in bins

fb_spec_T = np.transpose(fb_spec)

#print dispdelay(DM,fb.frequencies[0],freqhi)

for i in range(nchans):
    tempdelay = dispdelay(opts.DM,fb.frequencies[i],freqhi)
    tempbin = int(tempdelay/fb.dt) + Binsert
    #fb_spec_T[i,:][tempbin-50:tempbin+50] += gauss/nchans
    if opts.onebit:
        fb_spec_T[i,:][tempbin-opts.width/2:tempbin+opts.width/2] += mr_hat
        fb_spec_T[i,:][tempbin-opts.width/2:tempbin+opts.width/2] = np.where(fb_spec_T[i,:][tempbin-opts.width/2:tempbin+opts.width/2]>1,1,fb_spec_T[i,:][tempbin-opts.width/2:tempbin+opts.width/2])
        #fb_spec_T[i,:][tempbin-50:tempbin+50] += mr_hat
        #fb_spec_T[i,:][tempbin-50:tempbin+50] = np.where(fb_spec_T[i,:][tempbin-50:tempbin+50]>1,1,fb_spec_T[i,:][tempbin-50:tempbin+50])
    else:
        #fb_spec_T[i,:][tempbin-opts.width/2:tempbin+opts.width/2] += gauss/nchans
        fb_spec_T[i,:][tempbin-opts.width/2:tempbin+opts.width/2] = fb_spec_T[i,:][tempbin-opts.width/2:tempbin+opts.width/2] + gauss/nchans

fb_spec_T_T = np.transpose(fb_spec_T)

# PLOTTING FOR TESTING
#import matplotlib.pyplot as plt
#fig, ax = plt.subplots()
#cax = ax.imshow(fb_spec_T[:,Binsert-100:Binsert+binsweep+100])
#cbar = fig.colorbar(cax,ticks=[0,1],orientation='horizontal')
#plt.show()
#plt.plot(fb_spec_T_T)
#plt.show()
#print fb_spec_T_T.shape

# Write filterbank with FRB to disk (new file)
if opts.onebit:
    filterbank.create_filterbank_file(outputfb, fb.header.copy(), spectra=fb_spec_T_T, nbits=1, verbose=True)
else:
    filterbank.create_filterbank_file(outputfb, fb.header.copy(), spectra=fb_spec_T_T, nbits=opts.nbits, verbose=True)
#filterbank.create_filterbank_file(outputfb, fb.header.copy(), spectra=fb_spec_T_T, nbits=8, verbose=True)    

