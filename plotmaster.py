#coding = utf-8

import matplotlib.pyplot as plt
import filterbank
import numpy as np
import os
'''

Gathers all singlepulses and writes new txtfiles which the plotter reads from
    allsps.txt - all sps from NEW sps files
    allsps_MEGA.txt - all sps from single pulse search
    EventSummary.txt - all low m_I sps from spsummarizer.py
reads those files and sorts them if not empty, if empty, nothing will be plotted from those files
plots (current version)
    SNvmI02.png - signal to noise vs modulation index
    DM_SN_T_COLORS.png - scatterplot with circles indicating SN, DM vs time
                        color code: black - all sps
                                    blue - high SN or groups
                                    red - low m_I
    THE_SPS_SPLITX.png - similar to single pulse search figures
                        histogram w. number of pulses vs SN
                        histogram w. DM of pulses 
                        SN vs DM
                        DM vs T with circles indicating SN (blue and red pulses)


'''
'''
DON'T NEED THIS ANYMORE WITH NEW MOMENTMOD
# Gather info from NEW.singlepulse into one file for plotting
def gathersps(INDIR,OUTDIR):
    spdir_files = []
    for (dirpath,dirnames,filenames) in os.walk(INDIR):
        spdir_files.extend(filenames)
        break
    sp_files = []
    for i in range(len(spdir_files)):
        tmpfilename = ['.'.join(spdir_files[i].split('.')[0:-1]),spdir_files[i].split('.')[-1]]
        if (tmpfilename[-1]=='singlepulse'):
            sp_files.append(tmpfilename[0])
    if sp_files:
        firstspfile = sp_files[0] + ".singlepulse"
        os.system("head -1 " + INDIR + str(firstspfile) + " > " + OUTDIR + "allsps.txt")
        os.system("tail -n+2 -q " + INDIR + "*.singlepulse >> " + OUTDIR + "allsps.txt")
    else:
        open(OUTDIR + "allsps.txt",'w').close()'''

# Gather info from original .singlepulse files
def gathersps2(INDIR,OUTDIR):
    spdir_files = []
    for (dirpath,dirnames,filenames) in os.walk(INDIR):
        spdir_files.extend(filenames)
        break
    sp_files = []
    for i in range(len(spdir_files)):
        tmpfilename = ['.'.join(spdir_files[i].split('.')[0:-1]),spdir_files[i].split('.')[-1]]
        if (tmpfilename[-1]=='singlepulse'):
            sp_files.append(tmpfilename[0])
    if sp_files:
        firstspfile = sp_files[0] + ".singlepulse"
        os.system("head -1 " + INDIR + str(firstspfile) + " > " + OUTDIR + "allsps_MEGA.txt")
        os.system("tail -n+2 -q " + INDIR + "*.singlepulse >> " + OUTDIR + "allsps_MEGA.txt")
    else:
        open(OUTDIR + "allsps_MEGA.txt",'w').close()

# Checks if a number is between two others
def in_between(one,two,three):
    if (one <= two <= three):
        return True

def plotstuff(TXTDIR,FIL):
    plt.ioff() #interactive mode off
    plt.close()
    filfile = filterbank.FilterbankFile(FIL)
    lenfile = filfile.dt * filfile.N # length of obs in s
    nchans = filfile.nchan
    m_I_T = np.sqrt(nchans)/10. # m_I_T = sqrt(Nchan)/SN_min
    #m_I_T = np.sqrt(filfile.nchan)/7. # m_I_T = sqrt(Nchan)/SN_min
    #the_good = os.path.isfile(os.path.join(TXTDIR,"EventSummary.txt"))
    #the_bad = os.path.isfile(os.path.join(TXTDIR,"allsps.txt"))
    #the_ugly = os.path.isfile(os.path.join(TXTDIR,"allsps_MEGA.txt"))
    the_good = os.path.isfile(os.path.join(TXTDIR,"waterfall_result.txt"))
    the_bad = os.path.isfile(os.path.join(TXTDIR,"goodsps_sorted.txt"))
    the_ugly = os.path.isfile(os.path.join(TXTDIR,"allsps_MEGA.txt"))
    if the_good:
        smalldat = np.loadtxt(os.path.join(TXTDIR,"waterfall_result.txt"))
        if np.ndim(smalldat)==1: smalldat = np.zeros((1,13))
        SNvals = smalldat[:,1]
        DMvals = smalldat[:,0]
        Tvals = smalldat[:,2]
        sort_stuff2 = np.argsort(Tvals)
        Tsort = Tvals[sort_stuff2]
        DMsort = DMvals[sort_stuff2]
        SNsort = SNvals[sort_stuff2]
    if the_bad:
        print "goodsps yes yes"
        bigdat = np.loadtxt(os.path.join(TXTDIR,"goodsps_sorted.txt"))
        if np.ndim(bigdat)==1: bigdat = np.zeros((1,6))
        bigDM = bigdat[:,0]
        bigSN = bigdat[:,1]
        bigT = bigdat[:,2]
        sort_stuff = np.argsort(bigT)
        bigTsort = bigT[sort_stuff]
        bigDMsort = bigDM[sort_stuff]
        bigSNsort = bigSN[sort_stuff] 
        print len(bigT)
    if the_ugly:
        megadat = np.loadtxt(os.path.join(TXTDIR,"allsps_MEGA.txt"))
        if np.ndim(megadat)==1: megadat = np.zeros((1,5))
        megaDM = megadat[:,0]
        megaSN = megadat[:,1]
        megaT = megadat[:,2]

    #SNvmI02
    '''
    SOMETHING OFF ABOUT THIS, COMMENT IT OUT FOR NOW
    '''

    fig = plt.figure(2)
    ax = fig.add_subplot(1,1,1)
    if the_bad: 
        ax.plot(bigdat[:,5],bigdat[:,1],'bx',ms=1)
        ax.vlines(m_I_T,0,max(bigdat[:,1]))
    else:
        ax.vlines(m_I_T,0,20)
    if the_good:
        ax.plot(smalldat[:,5],smalldat[:,1],'r.',ms=1)
        ax.set_ylim(3.,smalldat[:,1].max())
    #else:
        #ax.set_ylim(3.,20)
    ax.hlines(7.,0,m_I_T*2)
    #ax.set_xlim(0,m_I_T*2.)
    #ax.set_ylim(smalldat[:,1].min(),smalldat[:,1].max())
    counter = 0
    SNSNx = np.linspace(.1,m_I_T,100)
    SNSNy = lambda x: np.sqrt(filfile.nchan)/x
    ax.plot(SNSNx,SNSNy(SNSNx),'k-.')
    '''counter = 0
    for i in range(len(smalldat[:,5])):
        one = (1-.3)*SNSNy(smalldat[i,5])
        two = smalldat[i,1]
        three = (1+.3)*SNSNy(smalldat[i,5]) 
        if (in_between(one,two,three) and smalldat[i,5]<=1.1): 
            counter += 1 # need to refine this!!!
    '''
    ax.set_xlabel("$m_I$",fontsize=24) 
    ax.set_ylabel("$S/N$",fontsize=24)
    outplot2 = os.path.join(TXTDIR,"SNvmI02.png")
    #plt.savefig(outplot2,format='png',dpi=200)
    plt.close(fig)
    plt.close('all')

    #DM_SN_T_COLORS
    
    fig = plt.figure(4)
    ax = fig.add_subplot(1,1,1)
    if the_ugly:
        ax.scatter(megaT,megaDM,marker='o',color='black',linewidth=.5,facecolor='none',s=(megaSN)+.5,\
            label="All Events")
    if the_bad and np.count_nonzero(bigdat)>0:
        bigSN[bigSN>65] = 65
        ax.scatter(bigT,bigDM,marker='o',color='blue',linewidth=.5,facecolor='none',s=(bigSN-5)**2+.5,\
            label="High SN/Groups")
    if the_good and np.count_nonzero(smalldat)>0:
        ax.scatter(Tvals,DMvals,marker='o',color='red',linewidth=.5,facecolor='red',s=2,\
            label="$m_I$ cands")
        #ax.scatter(Tvals,DMvals,marker='o',color='red',linewidth=.5,facecolor='none',s=(SNvals-10)**2+.5,\
        #    label="$m_I$ cands")
    ax.set_xlabel("$T$",fontsize=18)
    ax.set_ylabel("DM",fontsize=18)
    ax.legend(loc='upper center',ncol=3,frameon=False)
    outplot4 = os.path.join(TXTDIR,"DM_SN_T_COLORS.png")
    plt.savefig(outplot4,format='png',dpi=200)
    plt.close(fig)  
    plt.close('all')
    
    #SPS_SPLITX
    for i in range(4):
        start = lenfile*i/4.
        stop = lenfile*(i+1)/4.
        if the_bad:
            tmpsortbig = np.where((bigTsort>=start) & (bigTsort<=stop))
            tmpT = bigTsort[tmpsortbig]
            tmpDM = bigDMsort[tmpsortbig]
            tmpSN = bigSNsort[tmpsortbig]
        else:
            tmpT = np.zeros((1,1))
        if the_good:
            tmpsortsmall = np.where((Tsort>=start) & (Tsort<=stop))
            tmpt = Tsort[tmpsortsmall]
            tmpdm = DMsort[tmpsortsmall]
            tmpsn = SNsort[tmpsortsmall]
        else:
            tmpt = np.zeros((1,1))
        fig = plt.figure(6+i)
        ax = fig.add_subplot(1,1,1)
        ax.axis('off')
        ax2 = fig.add_subplot(3,3,1)
        if any(tmpT): plt.hist(tmpSN,lw=1,color='blue')
        if any(tmpt):
            #if np.size(tmpt)==1: continue
            ax2.hist(tmpsn,lw=1,color='red')
        ax2.set_xlabel("S/N",fontsize=10)
        ax2.set_ylabel("No. pulses",fontsize=10)
        ax3 = fig.add_subplot(3,3,2) 
        if any(tmpT): ax3.hist(tmpDM,lw=1,color='blue')
        if any(tmpt):
            #if np.size(tmpt)==1: continue
            ax3.hist(tmpdm,lw=1,color='red')
        ax3.set_xlabel("DM",fontsize=10)
        ax3.set_ylabel("No. pulses",fontsize=10)
        ax4 = fig.add_subplot(3,3,3)
        if any(tmpT): ax4.plot(tmpDM,tmpSN,'b.',ms=1)
        if any(tmpt): ax4.plot(tmpdm,tmpsn,'r.',ms=1)
        ax4.set_xlabel("DM",fontsize=10)
        ax4.set_ylabel("S/N",fontsize=10)
        ax5 = fig.add_subplot(3,3,(4,9))
        if any(tmpT): 
            tmpSN[tmpSN>65] = 65
            ax5.scatter(tmpT,tmpDM,color='blue',linewidth=.5,facecolor='none',s=(tmpSN-5)**2.+1)
        if any(tmpt): ax5.scatter(tmpt,tmpdm,color='red',linewidth=.5,facecolor='red',s=2)
        #if any(tmpt): ax5.scatter(tmpt,tmpdm,color='red',linewidth=.5,facecolor='none',s=(tmpsn-7)**2.+1)
        ax5.set_xlim(start,stop)
        ax5.set_xlabel("$T$",fontsize=14)
        ax5.set_ylabel("DM",fontsize=14)
        #ax5.set_ylim(0,300) # comment out if you don't want/need this
        fig.subplots_adjust(wspace=.7,hspace=.7)
        stringaling = str(i)
        thename = "THE_SPS_SPLIT" + stringaling + ".png"
        tmpoutplot = os.path.join(TXTDIR,thename)
        plt.savefig(tmpoutplot,format='png',dpi=200)
        plt.close(fig)
        plt.close('all')
    #plt.close('all')
    return counter




    











