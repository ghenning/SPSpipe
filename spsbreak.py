# coding=utf-8

import filterbank
import os
import sys
import time

'''

Comments Nov 2017

runs single pulse search on .singlepulse files, and splits
it into 4 groups, so it makes the same shit as SPS_SPLIT.png, so
it's not really necessary.

'''

'''
    AN ATTEMPT TO MAKE THE GODDAMN SINGLEPULSESEARCH.PY CREATE
    THE PLOTS SPLIT IN TIME, BUT IT SEEMS TO ONLY WORK PROPERLY
    IF I DO IT STRAIGHT FROM THE TERMINAL.
    DON'T THINK THIS WILL BE AN ISSUE THOUGH BECAUSE I DO IT
    WITH COLORS IN PLOTMASTER.PY
'''

def spsbreakdown(DIR,FIL,BREAKDOWN=4):
    FIL_fil = filterbank.FilterbankFile(FIL)
    FIL_DUR = FIL_fil.dt * FIL_fil.nspec
    for i in range(BREAKDOWN):
        sps_start = (i) * FIL_DUR/float(BREAKDOWN)
        sps_stop = (i + 1) * FIL_DUR/float(BREAKDOWN)
        os.system("single_pulse_search.py -s " + str(sps_start) + \
                " -e " + str(sps_stop) + " " + DIR + "*.singlepulse")
        #time.sleep(15)

if __name__=="__main__":
    DIR = sys.argv[1]
    FIL = sys.argv[2]
    spsbreakdown(DIR,FIL)
