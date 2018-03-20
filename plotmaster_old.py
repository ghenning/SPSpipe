#coding = utf-8

'''
    SOME EXTRA FUNCTIONS FOR THE PIPELINE
'''
#import matplotlib
#matplotlib.use('pdf')
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
#import matplotlib.pyplot as plt
import filterbank
import numpy as np
import os

# In case single_pulse_search.py doesn't finish "correctly", i.e.
# doesn't produce a ps figure with info
# run single_pulse_search.py on all .singlepulse (or all NEW.singlepulse?)
# to get the .ps file with the plots
def singlefix(DIR,THRESH=8.):
    os.system("single_pulse_search.py -t " + str(THRESH) + \
            " " + DIR + "*.singlepulse")

# break single pulse search plots into chunks in time
def sps_brkdown(DIR,FIL,BREAKDOWN=4):
    FIL_fil = filterbank.FilterbankFile(FIL)
    FIL_DUR = FIL_fil.dt * FIL_fil.nspec
    for i in range(BREAKDOWN):
        sps_start = (i) * FIL_DUR/float(BREAKDOWN)
        sps_stop = (i + 1) * FIL_DUR/float(BREAKDOWN)
        os.system("single_pulse_search.py -s " + str(sps_start) + \
                " -e " + str(sps_stop) + " " + DIR + "*.singlepulse")
    #allps = '*.ps'
    #dapath = os.path.join(DIR,allps)
    #os.system("mv " + dapath + " ..")

# gather info from NEW.singlepulse into one file to plot the m_I stuff
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
    if  sp_files:  
        firstspfile = sp_files[0] + ".singlepulse"
        os.system("head -1 " + INDIR + str(firstspfile) + " > " + OUTDIR + "allsps.txt")
        os.system("tail -n+2 -q " + INDIR + "*.singlepulse >> " + OUTDIR + "allsps.txt")
    else:
        open(OUTDIR + "allsps.txt",'w').close()

# gathers all events from the .singlepulse files
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
    firstspfile = sp_files[0] + ".singlepulse"
    os.system("head -1 " + INDIR + str(firstspfile) + " > " + OUTDIR + "allsps_MEGA.txt")
    os.system("tail -n+2 -q " + INDIR + "*.singlepulse >> " + OUTDIR + "allsps_MEGA.txt")

# Checks if a number is between two others, nobel prize worthy stuff here...
def in_between(one,two,three):
    if (one <= two <= three):
        return True

# make plots
# CURRENTLY: produces three figures
# i) Plots modulation index as a function of S/N
# ii) plots the same thing, but "zooms in" on the
# more important stuff. Also adds the m_I(S/N) curve
# iii) creates three subplots
#  a) S/N vs DM as is done in the ps output of spsearch
#  b) DM vs time as is done in the ps output of spsearch
#  c) DM vs time again, but low S/N events are omitted
#     (might want to think harder about what events to omit)
def plotstuff(TXTDIR,FIL):
    plt.ioff() # interactive mode off
    plt.close()
    filfile = filterbank.FilterbankFile(FIL)
    lenfile = filfile.dt * filfile.N # length of obs in s
    m_I_T = np.sqrt(filfile.nchan)/10. # m_I_T = sqrt(Nchan)/SN_min
    if os.stat(TXTDIR + "allsps.txt").st_size == 0:
        bigdat = np.empty((10,10))
    else: bigdat = np.loadtxt(TXTDIR + "allsps.txt",skiprows=1)
    #bigdat = np.loadtxt(TXTDIR + "allsps.txt",skiprows=1)
    smalldat = np.loadtxt(TXTDIR + "EventSummary.txt",skiprows=1)
    print smalldat.any()
    if not smalldat.any(): 
        counter = 0
        print "################################################"
        print "################################################"
        print "NO NOTEWORTHY EVENTS WRITTEN TO EventSummary.txt"
        print "################################################"
        print "################################################"
        #return counter # WANT TO PLOT BLUE DUDES TOO
    megadat = np.loadtxt(TXTDIR + "allsps_MEGA.txt",skiprows=1)
    #plt.figure(1) # Everything
    '''
        Basically crap
    '''
    '''START OF OLD PLOT plt.plot(bigdat[:,5],bigdat[:,1],'bx')
    plt.plot(smalldat[:,5],smalldat[:,1],'r.')
    plt.vlines(m_I_T,min(bigdat[:,1]),max(bigdat[:,1]))
    plt.xlabel("$m_I$",fontsize=24)
    plt.ylabel("$S/N$",fontsize=24)
    outplot = TXTDIR + "SNvmI.png"
    #outplot = TXTDIR + "SNvmI.pdf"
    #plt.savefig(outplot,format='pdf',dpi=200)
    plt.savefig(outplot,format='png',dpi=600)
    #plt.close(1)
    plt.figure(2) # zoomed in END OF OLD PLOT'''
    try:
        fig = plt.figure(1)
        ax = fig.add_subplot(1,1,1)
        ax.plot(bigdat[:,5],bigdat[:,1],'bx',ms=1)
        try:
            ax.plot(smalldat[:,5],smalldat[:,1],'r.',ms=1)
        except:
            print "no smalldat"
        ax.vlines(m_I_T,min(bigdat[:,1]),max(bigdat[:,1]))
        ax.set_xlabel("$m_I$",fontsize=24)
        ax.set_ylabel("$S/N$",fontsize=24)
        outplot = os.path.join(TXTDIR,"SNvmI.png")
        #fig.savefig(outplot,format='png',dpi=200)
        plt.savefig(outplot,format='png',dpi=200)
        plt.close(fig)
    except:
        print "First figure complains"
    '''
        SNvmI02.png

        Plots S/N(m_I) for the high S/N/groups (blue X) and
        low m_I (red dots). Restrictions are put on the x and
        y range of the plot so we can see better what's going on
        in the interesting region.
        Horizontal line is the S/N threshold we choose, and
        the vertical line is the modulation index threshold.
        The dash dotted curve is the relation between S/N and
        m_I. The shaded area is an attempt to constrain the
        number of events that would be considered as "good" events,
        i.e. an attempt to get rid of the red blob of crap that
        seems to show up around the intersection of the solid lines.
        The "good" events are counted and put in the database.
    '''
    try:
        fig = plt.figure(2)
        ax = fig.add_subplot(1,1,1)
        ax.plot(bigdat[:,5],bigdat[:,1],'bx',ms=1)
        try:
            ax.plot(smalldat[:,5],smalldat[:,1],'r.',ms=1)
        except:
            print "no smalldat"
        ax.vlines(m_I_T,0,max(bigdat[:,1]))
        ax.hlines(10.,0,m_I_T*2)
        ax.set_xlim(0,m_I_T*2.)
        try:
            ax.set_ylim(smalldat[:,1].min(),smalldat[:,1].max())
        except:
            print "no smalldat"
        #START OF OLD PLOT plt.plot(bigdat[:,5],bigdat[:,1],'bx')
        #plt.plot(smalldat[:,5],smalldat[:,1],'r.')
        #plt.vlines(m_I_T,0,max(bigdat[:,1]))
        #plt.hlines(10.,0,m_I_T*2)
        #plt.xlim(0,m_I_T*2.)
        #plt.ylim(smalldat[:,1].min(),smalldat[:,1].max()) END OF OLD PLOT
        SNSNx = np.linspace(.1,m_I_T,100)
        snsnx = np.linspace(.1,1.1,100)
        SNSNy = lambda x: np.sqrt(filfile.nchan)/x
        ax.plot(SNSNx,SNSNy(SNSNx),'k-.')
        #plt.plot(SNSNx,SNSNy(SNSNx),'k-.') OLD
        #xx = [a for a in SNSNx if a <= 1.5]
        #xxx = [a for a in SNSNx if a> 1.5]
        ax.fill_between(snsnx,SNSNy(snsnx)*(1-.2),SNSNy(snsnx)*(1+.2),facecolor='y')
        #plt.fill_between(snsnx,SNSNy(snsnx)*(1-.2),SNSNy(snsnx)*(1+.2),facecolor='y') # OLD
        #plt.fill_between(xx,SNSNy(xx)*(1-.2),SNSNy(xx)*(1+.2),facecolor='y')
        #plt.fill_between(xxx,SNSNy(xxx)*(1-.1),SNSNy(xxx)*(1+.1),facecolor='y')
        counter = 0
        #good_stuff = np.where((smalldat[:,5]<=1.1))
        for i in range(len(smalldat[:,5])):
        #for i in good_stuff:
            one = (1-.3)*SNSNy(smalldat[i,5])
            two = smalldat[i,1]
            three = (1+.3)*SNSNy(smalldat[i,5])
            #print one,two,three
            #print i,smalldat[i,5]
            if (in_between(one,two,three) and smalldat[i,5]<=1.1): counter += 1
            #if in_between(one,two,three): counter += 1
        ax.set_xlabel("$m_I$",fontsize=24)
        ax.set_ylabel("$S/N$",fontsize=24)
        #plt.xlabel("$m_I$",fontsize=24) OLD
        #plt.ylabel("$S/N$",fontsize=24) OLD
        outplot2 = os.path.join(TXTDIR,"SNvmI02.png")
        #outplot2 = TXTDIR + "SNvmI02.png"
        plt.savefig(outplot2,format='png',dpi=200)
        #fig.savefig(outplot2,format='png',dpi=200)
        #plt.savefig(outplot2,format='png',dpi=200) # OLD
        #outplot2 = TXTDIR + "SNvmI02.pdf"
        #plt.savefig(outplot2,format='pdf',dpi=200)
        #plt.close(2)
        plt.close(fig)
    except:
        print "figure 2 complains"
    #plt.figure(3)
    '''
        DM_SN_T.png

        Creates three subplots
        i) S/N(DM) for low m_I events
        ii) DM(T) for low m_I events
        iii) DM(T) for low m_I events, where lower SN values are omitted
    '''
    try:
        SNvals = smalldat[:,1]
        DMvals = smalldat[:,0]
        Tvals = smalldat[:,2]
        bb = SNvals.max()/5.
        SNvals2 = np.where(SNvals<bb,0,SNvals)
    except:
        print "no smalldat"
    try:
        fig = plt.figure(3)
        ax1 = fig.add_subplot(1,1,1)
        ax1.axis('off')
        #SNvals = smalldat[:,1]
        #DMvals = smalldat[:,0]
        #Tvals = smalldat[:,2]
        #bb = SNvals.max()/5.
        #SNvals2 = np.where(SNvals<bb,0,SNvals)
        ax2 = fig.add_subplot(9,6,(1,18))
        ax2.plot(DMvals,SNvals,'k.',ms=1)
        ax2.set_xlabel("DM",fontsize=18)
        ax2.set_ylabel("$S/N$",fontsize=18)
        ax3 = fig.add_subplot(9,6,(19,36))
        ax3.scatter(Tvals,DMvals,marker='o',linewidth=.5,facecolor='none',s=SNvals)
        ax3.set_xlabel("$T$",fontsize=18)
        ax3.set_ylabel("DM",fontsize=18)
        ax4 = fig.add_subplot(9,6,(37,54))
        ax4.scatter(Tvals,DMvals,marker='o',linewidth=.5,facecolor='none',s=SNvals2)
        ax4.set_xlabel("$T$",fontsize=18)
        ax4.set_ylabel("DM",fontsize=18)
        fig.subplots_adjust(wspace=.5,hspace=5.5)
        '''OLD plt.subplot(9,6,(1,18))
        plt.plot(DMvals,SNvals,'k.')
        plt.xlabel("DM",fontsize=18)
        plt.ylabel("$S/N$",fontsize=18)
        plt.subplot(9,6,(19,36))
        plt.xlabel("$T$",fontsize=18)
        plt.ylabel("DM",fontsize=18)
        plt.scatter(Tvals,DMvals,marker='o',facecolors='none',s=SNvals)
        plt.subplot(9,6,(37,54))
        plt.xlabel("$T$",fontsize=18)
        plt.ylabel("DM",fontsize=18)
        plt.scatter(Tvals,DMvals,marker='o',facecolors='none',s=SNvals2)
        plt.subplots_adjust(wspace=0.5,hspace=5.5) OLD END'''
        outplot3 = os.path.join(TXTDIR,"DM_SN_T.png")
        #outplot3 = TXTDIR + "DM_SN_T.png"
        #fig.savefig(outplot3,format='png',dpi=200)
        plt.savefig(outplot3,format='png',dpi=200)
        plt.close(fig)
    except:
        print "figure 3 complains"
    #plt.savefig(outplot3,format='png',dpi=200)
    #outplot3 = TXTDIR + "DM_SN_T.pdf"
    #plt.savefig(outplot3,format='pdf',dpi=200)
    #plt.close(3)
    #plt.figure(4)
    '''
        DM_SN_T_COLORS.png

        Creates a figure of DM(T), where each event is a circle
        with size depending on its S/N
        Black: all events
        Blue: High S/N/groups
        Red: Low m_I
    '''
    bigDM = bigdat[:,0]
    bigSN = bigdat[:,1]
    bigT = bigdat[:,2]
    megaDM = megadat[:,0]
    megaSN = megadat[:,1]
    megaT = megadat[:,2]
    try:
        fig = plt.figure(4)
        ax = fig.add_subplot(1,1,1)
        ax.scatter(megaT,megaDM,marker='o',color='black',linewidth=.5,facecolor='none',s=(megaSN-7)+.5,\
            label="All Events")
        ax.scatter(bigT,bigDM,marker='o',color='blue',linewidth=.5,facecolor='none',s=(bigSN-7)**2+.5,\
            label="High SN/Groups")
        try:
            ax.scatter(Tvals,DMvals,marker='o',color='red',linewidth=.5,facecolor='none',s=(SNvals-7)**2+.5,\
            label="Low $m_I$")
        except:
            print "no smalldat"
        ax.set_xlabel("$T$",fontsize=18)
        ax.set_ylabel("DM",fontsize=18)
        ax.legend(loc='upper center',ncol=3,frameon=False)
        #ax.set_ylim(0,200) # set the ylim temporarily because DDplan went up to 2000 instead of 200
        # OLD plt.scatter(megaT,megaDM,marker='o',color='black',facecolors='none',s=megaSN,\
        #        label="All Events")
        # OLD plt.scatter(bigT,bigDM,marker='o',color='blue',facecolors='none',s=bigSN,\
        #        label="High S/N/Groups")
        # OLD plt.scatter(Tvals,DMvals,marker='o',color='red',facecolors='none',s=SNvals,\
        #        label="Low $m_I$")
        # OLD plt.xlabel("$T$",fontsize=18)
        # OLD plt.ylabel("DM",fontsize=18)
        # OLD plt.legend(loc='upper center',ncol=3,frameon=False)
        outplot4 = os.path.join(TXTDIR,"DM_SN_T_COLORS.png")
        #outplot4 = TXTDIR + "DM_SN_T_COLORS.png"
        plt.savefig(outplot4,format='png',dpi=200)
        plt.close(fig)
    except:
        print "figure 4 complains"
    #outplot4 = TXTDIR + "DM_SN_T_COLORS.pdf"
    #plt.savefig(outplot4,format='pdf',dpi=200)
    #plt.figure(6)
    '''
        SPS_SPLITX.png

        This is the same figure as single_pulse_search.py creates,
        but here the "crap" events are omitted, so only high S/N/group
        events (blue) and low m_I events (red) are plotted.
        Also, this breaks down the data into four chunks in time, so 
        long files can be more easily read (and in color!).
        Splits the blue data in four parts, and then searches for 
        red data within that timeframe. Since the red data is a subset
        of the blue data, no events should be missing.
    '''
    sort_stuff = np.argsort(bigT)
    bigTsort = bigT[sort_stuff]
    bigDMsort = bigDM[sort_stuff]
    bigSNsort = bigSN[sort_stuff]
    try:
        sort_stuff2 = np.argsort(Tvals)
        Tsort = Tvals[sort_stuff2]
        DMsort = DMvals[sort_stuff2]
        SNsort = SNvals[sort_stuff2]
    except:
        print "no smalldat"
    try:
        for i in range(4):
            start = lenfile*i/4.
            stop = lenfile*(i+1)/4.
            tmpsortbig = np.where((bigTsort>=start) & (bigTsort<=stop))
            tmpT = bigTsort[tmpsortbig]
            tmpDM = bigDMsort[tmpsortbig]
            tmpSN = bigSNsort[tmpsortbig]
            try:
                tmpsortsmall = np.where((Tsort>=start) & (Tsort<=stop))
                tmpt = Tsort[tmpsortsmall]
                tmpdm = DMsort[tmpsortsmall]
                tmpsn = SNsort[tmpsortsmall]
            except:
                print "no smalldat"
            print lenfile
            print start
            print stop
            #continue
            #tmpt = Tsort[tmpsortsmall]
            #tmpdm = DMsort[tmpsortsmall]
            #tmpsn = SNsort[tmpsortsmall]
            #if not any(tmpT): continue
            fig = plt.figure(6+i)
            ax = fig.add_subplot(1,1,1)
            ax.axis('off')
            ax2 = fig.add_subplot(3,3,1)
            # OLD plt.figure(6+i)
            # OLD plt.subplot(3,3,1)
            # number vs SN
            if any(tmpT): plt.hist(tmpSN,lw=1,color='blue')
            if any(tmpt):
                if np.size(tmpt)==1: continue
                ax2.hist(tmpsn,lw=1,color='red')
                # OLD plt.hist(tmpsn,color='red')
            ax2.set_xlabel("S/N",fontsize=14)
            ax2.set_ylabel("No. pulses",fontsize=14)
            # OLD plt.xlabel("S/N",fontsize=14)
            # OLD plt.ylabel("No. pulses",fontsize=14)
            # OLD plt.subplot(3,3,2)
            ax3 = fig.add_subplot(3,3,2)
            # number vs DM
            if any(tmpT): ax3.hist(tmpDM,lw=1,color='blue')
            # OLD if any(tmpT): plt.hist(tmpDM,color='blue')
            if any(tmpt):
                if np.size(tmpt)==1: continue
                ax3.hist(tmpdm,lw=1,color='red')
                # OLD plt.hist(tmpdm,color='red')
            ax3.set_xlabel("DM",fontsize=14)
            ax3.set_ylabel("No. pulses",fontsize=14)
            # OLD plt.xlabel("DM",fontsize=14)
            # OLD plt.ylabel("No. pulses", fontsize=14)
            # OLD plt.subplot(3,3,3)
            ax4 = fig.add_subplot(3,3,3)
            # SN vs DM
            if any(tmpT): ax4.plot(tmpDM,tmpSN,'b.',ms=1)
            if any(tmpt): ax4.plot(tmpdm,tmpsn,'r.',ms=1)
            # OLD if any(tmpT): plt.plot(tmpDM,tmpSN,'b.',ms=1)
            # OLD if any(tmpt): plt.plot(tmpdm,tmpsn,'r.',ms=1)
            ax4.set_xlabel("DM",fontsize=14)
            ax4.set_ylabel("S/N",fontsize=14)
            # OLD plt.xlabel("DM",fontsize=14)
            # OLD plt.ylabel("S/N",fontsize=14)
            # OLD plt.subplot(3,3,(4,9))
            ax5 = fig.add_subplot(3,3,(4,9))
            # DM vs T with SN rings
            if any(tmpT): ax5.scatter(tmpT,tmpDM,color='blue',linewidth=.5,facecolor='none',s=(tmpSN)**2.0+.5)
            if any(tmpt): ax5.scatter(tmpt,tmpdm,color='red',linewidth=.5,facecolor='none',s=(tmpsn)**2.0+.5)
            # OLD if any(tmpT): plt.scatter(tmpT,tmpDM,color='blue',linewidth=.5,facecolors='none',s=tmpSN**1.5)
            # OLD if any(tmpt): plt.scatter(tmpt,tmpdm,color='red',linewidth=.5,facecolors='none',s=tmpsn**1.5)
            #if any(tmpT): plt.scatter(tmpT,tmpDM,marker='o',color='blue',facecolors='none',s=tmpSN)
            #if any(tmpt): plt.scatter(tmpt,tmpdm,marker='o',color='red',facecolors='none',s=tmpsn)
            ax5.set_xlim(start,stop)
            ax5.set_xlabel("$T$",fontsize=14)
            ax5.set_ylabel("DM",fontsize=14)
            ax5.set_ylim(0,200) # set ylim because DDplan is an asshole
            fig.subplots_adjust(wspace=.4,hspace=.4)
            # OLD plt.xlim(start,stop)
            # OLD plt.xlabel("$T$",fontsize=14)
            # OLD plt.ylabel("DM",fontsize=14)
            # OLD plt.subplots_adjust(wspace=0.4,hspace=.4)
            stringaling = str(i)
            tmpoutplot = TXTDIR + "THE_SPS_SPLIT" + stringaling + ".png"
            # OLD plt.savefig(tmpoutplot,format='png',dpi=200)
            # OLD plt.close(6+i)
            plt.savefig(tmpoutplot,format='png',dpi=200)
            plt.close(fig)
    except:
        print "figure 5 complains"
        #tmpoutplot = TXTDIR + "THE_SPS_SPLIT" + stringaling + ".pdf"
        #plt.savefig(tmpoutplot,format='pdf',dpi=200)
        #plt.close(6+i)
    #print np.shape(SNvals),np.shape(Tvals)
    #print type(SNvals),type(Tvals)
    '''for i in range(4):
        tmpT = np.array_split(bigTsort,4)[i]
        tmpDM = np.array_split(bigDMsort,4)[i]
        tmpSN = np.array_split(bigSNsort,4)[i]
        small_sorter = np.where((Tvals>=tmpT[0]) & (Tvals<=tmpT[-1]))
        tmpt = Tvals[small_sorter]
        tmpdm = DMvals[small_sorter]
        tmpsn = SNvals[small_sorter]
        #tmpt = np.array_split(Tvals,4)[i]
        #tmpdm = np.array_split(DMvals,4)[i]
        #tmpsn = np.array_split(SNvals,4)[i]
        #print len(tmpT),len(tmpDM),len(tmpSN),len(tmpt),len(tmpdm),len(tmpsn)
        #print tmpT[0],tmpT[-1],tmpt[0],tmpt[-1]
        #print tmpT
        #print tmpDM
        #print tmpSN
        plt.figure(6+i)
        plt.subplot(3,3,1)
        # number vs SN
        plt.hist(tmpSN,color='blue')
        #print "shape tmpt",np.shape(tmpt),"shape tmpsn",np.shape(tmpsn)
        #print "type tmpt",type(tmpt),"type tmpdm",type(tmpdm)
        
        #   IF THERE IS ONLY ONE POINT IN tmpt PLOTTING HISTOGRAM GIVES ME AN ERROR,
        #    NEED TO FIX!!!
        
        #if any(tmpt): 
        #    print np.size(tmpt)
        #    if np.size(tmpt)==1: continue #plt.hist(np.reshape(tmpsn,(1,1)),color='red')
        #    else: plt.hist(tmpsn,color='red')
            #if any(tmpt): plt.hist(tmpsn,color='red')
        if any(tmpt):
            if np.size(tmpt)==1: continue
            plt.hist(tmpsn,color='red')
        plt.xlabel("S/N",fontsize=14)
        plt.ylabel("No. pulses",fontsize=14)
        plt.subplot(3,3,2)
        # number vs DM
        plt.hist(tmpDM,color='blue')
        if any(tmpt): 
            if np.size(tmpt)==1: continue
            plt.hist(tmpdm,color='red')
        plt.xlabel("DM",fontsize=14)
        plt.ylabel("No. pulses",fontsize=14)
        plt.subplot(3,3,3)
        # SN vs DM
        plt.plot(tmpDM,tmpSN,'b.')
        if any(tmpt): plt.plot(tmpdm,tmpsn,'r.')
        plt.xlabel("DM",fontsize=14)
        plt.ylabel("S/N",fontsize=14)
        plt.subplot(3,3,(4,9))
        # DM vs T with SN rings
        plt.scatter(tmpT,tmpDM,marker='o',color='blue',facecolors='none',s=tmpSN)
        if any(tmpt): plt.scatter(tmpt,tmpdm,marker='o',color='red',facecolors='none',s=tmpsn)
        plt.xlabel("$T$",fontsize=14)
        plt.ylabel("DM",fontsize=14)
        plt.subplots_adjust(wspace=0.4,hspace=.4)
        stringaling = str(i)
        tmpoutplot = TXTDIR + "SPS_SPLIT" + stringaling + ".png"
        plt.savefig(tmpoutplot,format='png',dpi=200)
        plt.close(6+i)'''
    #plt.scatter(bigT,bigDM,marker='o',color='blue',facecolors='none',s=bigSN,\
    #        label='High SN/Groups')
    #plt.scatter(Tvals,DMvals,marker='o',color='red',facecolors='none',s=SNvals,\
    #        label="Low $m_I$")
    #plt.xlabel("$T$",fontsize=18)
    #plt.ylabel("DM",fontsize=18)
    #plt.legend(loc='upper center',ncol=2,frameon=False)
    #outplot6 = TXTDIR + "DM_SN_T_COLORS_LESS.png"
    #plt.savefig(outplot6,format='png',dpi=300)
    #plt.figure(5)
    '''
        DM_SN_HIST.png

        Creates a figure with five subplots.

        i) S/N(DM) for all events
        ii) S/N(DM) for high S/N/groups (blue) and low m_I (red)
        iii) histogram of all DMs
        iv) histogram of blue and red DMs
        v) histogram of red DMs
    '''
    try:
        fig = plt.figure(5)
        ax = fig.add_subplot(1,1,1)
        ax.axis('off')
        ax1 = fig.add_subplot(3,2,1)
        ax1.plot(megaDM,megaSN,'k.',ms=1)
        ax1.plot(bigDM,bigSN,'b.',ms=1)
        ax1.plot(DMvals,SNvals,'r.',ms=1)
        ax1.set_xlabel("DM",fontsize=18)
        ax1.set_ylabel("$S/N$",fontsize=18)
        ax2 = fig.add_subplot(3,2,2)
        ax2.plot(bigDM,bigSN,'b.',ms=1)
        ax2.plot(DMvals,SNvals,'r.',ms=1)
        ax2.set_xlabel("DM",fontsize=18)
        ax2.set_ylabel("$S/N$",fontsize=18)
        ax3 = fig.add_subplot(3,2,(3,4))
        ax3.hist(megaDM,color='black')
        ax3.hist(bigDM,color='blue')
        ax3.hist(DMvals,color='red')
        ax3.set_xlabel("DM",fontsize=18)
        ax3.set_ylabel("No. pulses",fontsize=18)
        ax4 = fig.add_subplot(3,2,5)
        ax4.hist(bigDM,lw=1,color='blue')
        ax4.hist(DMvals,lw=1,color='red')
        ax4.set_xlabel("DM",fontsize=18)
        ax4.set_ylabel("No. pulses",fontsize=18)
        ax5 = fig.add_subplot(3,2,6)
        ax5.hist(DMvals,lw=1,color='red')
        ax5.set_xlabel("DM",fontsize=18)
        ax5.set_ylabel("No. pulses",fontsize=18)
        fig.subplots_adjust(wspace=.3,hspace=.5)
        ''' OLD START plt.subplot(3,2,1)
        plt.plot(megaDM,megaSN,'k.')
        plt.plot(bigDM,bigSN,'b.')
        plt.plot(DMvals,SNvals,'r.')
        plt.xlabel("DM",fontsize=18)
        plt.ylabel("$S/N$",fontsize=18)
        plt.subplot(3,2,2)
        plt.plot(bigDM,bigSN,'b.')
        plt.plot(DMvals,SNvals,'r.')
        plt.xlabel("DM",fontsize=18)
        plt.ylabel("$S/NS$",fontsize=18)
        plt.subplot(3,2,(3,4))
        plt.hist(megaDM,color='black')
        plt.hist(bigDM,color='blue')
        plt.hist(DMvals,color='red')
        plt.xlabel("DM",fontsize=18)
        plt.ylabel("No. pulses",fontsize=18)
        plt.subplot(3,2,5)
        plt.hist(bigDM,color='blue')
        plt.hist(DMvals,color='red')
        plt.xlabel("DM",fontsize=18)
        plt.ylabel("No. pulses",fontsize=18)
        plt.subplot(3,2,6)
        plt.hist(DMvals,color='red')
        plt.xlabel("DM",fontsize=18)
        plt.ylabel("No. pulses",fontsize=18)
        plt.subplots_adjust(wspace=0.3,hspace=.5) OLD END '''
        outplot5 = os.path.join(TXTDIR,"DM_SN_HIST.png")
        #outplot5 = TXTDIR + "DM_SN_HIST.png"
        plt.savefig(outplot5,format='png',dpi=200)
        plt.close(fig)
    except:
        print "figure 6 complains"
    # OLD plt.savefig(outplot5,format='png',dpi=200)
    #outplot5 = TXTDIR + "DM_SN_HIST.pdf"
    #plt.savefig(outplot5,format='pdf',dpi=200)
    #plt.subplot(5,3,(4,9))
    #plt.scatter(bigT,bigDM,marker='o',color='blue',facecolors='none',s=bigSN)
    #plt.scatter(Tvals,DMvals,marker='o',color='red',facecolors='none',s=SNvals)
    #plt.xlabel("$T$",fontsize=18)
    #plt.ylabel("DM",fontsize=18)
    #plt.subplot(5,3,(10,15))
    #plt.scatter(Tvals,DMvals,marker='o',color='red',facecolors='none',s=SNvals)
    #plt.xlabel("$T$",fontsize=18)
    #plt.ylabel("DM",fontsize=18)
    #plt.show()
    ''' OLD START plt.close(1)
    plt.close(2)
    plt.close(3)
    plt.close(4)
    plt.close(5)
    #plt.close(6) OLD END '''
    #counter = 0
    plt.close('all')
    return counter
    #plt.show()
    #plt.show()


