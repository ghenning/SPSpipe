import numpy as np
import filterbank
import waterfaller
import matplotlib.pyplot as plt
import optparse
import os

def grab_info(FILE,T,t):
    ### waterfaller stuff
    ####
    # need some file manipulation
    # or do I??? doesn't seem so
    ####
    thefile = filterbank.FilterbankFile(FILE)
    channels = thefile.nchans
    numsamp = thefile.N
    samptime = thefile.dt
    tot_time = numsamp*samptime
    if ((T+t)>=tot_time):
        print "Time requested exceeds the duration of the file, I'll fix it for you"
        T = tot_time - .1 - t
        print "new start time is: %f" % T
    data, bins, nbins, start = waterfaller.waterfall(thefile,T,t)
    ###main(data.data,channels) 
    return data.data,channels

def main(DATA,CHANNELS,FILE,SAVE):
    ### split into 8 and flatten each
    ### then plot 8 histograms, each one for 256 channels
    dirtofile = os.path.dirname(FILE)
    name = os.path.splitext(os.path.basename(FILE))[0]
    #fig = plt.figure(1)
    fig, ax = plt.subplots(2,4,sharey='row',sharex='col',figsize=(12,8))
    plt.suptitle(name + ': Channel histograms')
    counterino = 0
    for i in range(2):
        for j in range(4):
            #channels = 2048
            startchan = counterino * CHANNELS/8
            endchan = (counterino + 1) * CHANNELS/8 - 1
            counterino += 1
            #startchan = ((i+1)*j)*CHANNELS/8
            #endchan = ((i+1)*(j+1))*CHANNELS/8 - 1
            #tempsample = testdata[startchan:endchan,:].flatten()
            tempsample = DATA[startchan:endchan,:].flatten()
            #print tempsample
            ###ax = fig.add_subplot(2,4,i+1)
            ax[i,j].hist(tempsample,bins=np.arange(256))
            #ax[i,j].set_title("#%s-%s" % (startchan+1,endchan+1))
            ax[i,j].text(.5,.9,"#%s-%s" % (startchan+1,endchan+1),horizontalalignment='center',transform=ax[i,j].transAxes)
            ax[i,j].set_yscale('log')
            ax[i,j].set_xticks([0,32,64,96,128,160,192,224,256])
            labels = ax[i,j].get_xticklabels()
            plt.setp(labels,rotation=-90)
            ##axes = plt.gca()
            ###axes.set_xlim([min(tempsample)-2,max(tempsample)+2])
        if SAVE:
            outname = os.path.join(dirtofile,name + "_hist.png")
            plt.savefig(outname,format='png',dpi=200)
    plt.subplots_adjust(wspace=0,hspace=0)

    fig9 = plt.figure(9)
    ax = fig9.add_subplot(1,1,1)
    ax.set_title(name + ": All channels histogram")
    ax.hist(DATA.flatten())
    ax.set_yscale('log')

        #plt.show()    
    ### other plots? (std,mean of each channel)
    fig2 = plt.figure(2)
    ax = fig2.add_subplot(1,1,1)
    ax.set_title(name + ": Cmap of data")
    ax.set_ylabel("channel")
    ax.set_xlabel("sample")
    #cax = ax.imshow(testdata)
    cax = ax.imshow(DATA,aspect='auto')
    cbar = fig2.colorbar(cax,orientation='horizontal')
    if SAVE:
        outname = os.path.join(dirtofile,name + "_cmap.png")
        plt.savefig(outname,format='png',dpi=200)
    #plt.show()
    #ax.imshow(data.data)
    ##fig3 = plt.figure(3)
    ##ax = fig3.add_subplot(1,1,1)
    ##ax.set_title(name + ":$\sigma$ over channels")
    ##ax.set_ylabel("$\sigma$")
    ##ax.set_xlabel("channel")
    #STDs = np.std(testdata,axis=1)
    STDs = np.std(DATA,axis=1)
    #STDs = np.std(data.data,axis=1)
    ##print len(STDs)
    ##ax.plot(np.arange(CHANNELS),STDs)
    ##if SAVE:
        ##outname = os.path.join(dirtofile,name + "_sigma.png")
        ##plt.savefig(outname,format='png',dpi=200)
    ### plt.plot(np.arange(channels,STDs)
    fig4 = plt.figure(4)
    ax = fig4.add_subplot(1,1,1)
    ax.set_title(name + ": median over channels")
    ax.set_ylabel("median")
    ax.set_xlabel("channel")
    #MEDIANS = np.median(testdata,axis=1)
    MEDIANS = np.median(DATA,axis=1)
    print len(MEDIANS)
    '''
    90th percentile for each channel, and plot that!!!
    '''
    percs = np.zeros(CHANNELS)
    for i in range(CHANNELS):
        percs[i] = np.percentile(DATA[i,:],90)
    #print percs
    #print percs[1024]
    ax.plot(np.arange(CHANNELS),MEDIANS)
    ax.fill_between(np.arange(CHANNELS),MEDIANS+STDs,MEDIANS-STDs,facecolor='red',alpha=.5)
    ax.scatter(np.arange(CHANNELS),percs,marker='.',color='magenta',s=1)
    if SAVE:
        outname = os.path.join(dirtofile,name + "_median.png")
        plt.savefig(outname,format='png',dpi=200)
    plt.show()
    plt.close('all')
    #MEDIANS = np.median(data.data,axis=1)
    ### plt.plot(np.arange(channels),MEDIANS)

if __name__=='__main__':
    desc = "woof"
    parser = optparse.OptionParser(description=desc)
    parser.add_option('--filfile',dest='THEFILE',type='string',\
            help="input filterbank file to investigate")
    parser.add_option('--time','-T',dest='START',type='float',\
            help="start time in sec")
    parser.add_option('--dur','-t',dest='DUR',type='float',\
            help="time chunk you want in sec")
    parser.add_option('--save','-s',dest='SAVE',action='store_true',\
            help="if you want to save the plots", default=False)
    ### ADD OPTION TO SHOW/NOT SHOW AS WELL
    ###parser.add_option('--out','-o',dest='OUT',type='string',\
            ###help="where do you want the plots?")
    (opts,args) = parser.parse_args()
    ### some sanity check that we're not going outside of filterbank
    FILE = opts.THEFILE
    T = opts.START
    t = opts.DUR
    DATA, CHANNELS = grab_info(FILE,T,t)
    main(DATA,CHANNELS,FILE,opts.SAVE)###,OUTPATH)


