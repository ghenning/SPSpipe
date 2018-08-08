# coding = utf-8
'''

Comments Nov 2017

Basic description

    Creates results directory
    loads textfile with filterbank name (from runshell.py)
    Grabs info from the first filterbank file from the directory
        reads all filterbanks from dir
        grabs first file
        reads:  number of channels
                subbands to use (nchans/8)
                frequencies (central, bandwidth)
                sample time
    Creates DDplan (with DDplanmaker.py)
    Reads DDplan results
        low DM, high DM, dDM, Downsampling, dsubDM, numDMs, DMs/call, calls, numjobs
    THE_PROCESS(filterbank file) [main loop]
        creates directories (logs, prepsubband, subband)
        RFI find
            If you give it the option that there is already a mask, it will look for
            the maskfile and use it, if not it runs RFIfind (default values, -time 2.0 for 47T)
        prepsubband
            mask, -nobary, DDplan parameters
            option to use subbands or not
        single pulse search
            -t 7.0, -m 0.02, -b, -p
        Reads single pulse search files and runs RRATtrapmod.py
        Runs singleplus (from momentmod.py)
        Runs spsummarizer to grab singlepulsees for plotting (spsummarizer gives num of low m_I events)
             gathersps
        Runs plotter
        updates database

'''
'''
    UPDATE:

    Commented out the part where all the dd files are read and transformed
    to fil. This is now done in chunks in transformer.py

    Now this script just reads the names of the files in the chunk from a
    txt file generated in runshell.py, and performs the pipeline process
    on those files.

    The old "main loop" is now a worker process called THE_PROCESS(file),
    and Pool from multiprocessing calls this worker funtion on all the 
    files in the chunk. 

    All the parameters needed from DDplan are obtained from the first file
    in the chunk, so the only parameter needed for the worker function is
    a file, the rest has already been handled.
'''

'''
    The main program of the FRB search pipeline
    
    Runs on a directory full of filterbank files (or dd files)

    What it does:
        converts .dd files to .fil if needed
        runs DDplan.py to create a dedispersion plan
        loops over every fil file and runs
            - rfifind
            - prepsubband
            - single_pulse_search
            - momentmod (computes modulation index and moments)
            - rrattrap
            - spsummarizer (gathers low modulation index events)
            - creates a few plots (eps outputs)
'''

'''
    IMPORT
'''
import matplotlib
matplotlib.use('Agg')
import numpy as np
import optparse
import filterbank
import waterfaller
import rawdata
import os
#from momentmod import singleplus
from momentmod02 import singleplus
import time
import rrattrapmod
import spsummarizer
import dbmaker
import DDplanmaker
from multiprocessing import Pool,Process
###from plotmaster import gathersps,plotstuff,gathersps2,sps_brkdown
from plotmaster import plotstuff,gathersps2
import newsps2
import spsbreak
import newdb
'''
    OPTIONS
'''
desc ="FRB search pipeline. Essentials to run:\
        --dddir [directory to .dd/.fil]\
        the rest are optional and all have a default\
        value set"

parser = optparse.OptionParser(description=desc)

parser.add_option('--dddir', dest='dddir', type='string', \
        help="The directory of the .dd files that need to be \
        converted to .fil files. If you already have .fil files \
        you still use this command as the location of the directory")

parser.add_option('--outdir', dest='RESDIR', type='string',\
        help="The directory where all the results will go in")

parser.add_option('--chunkfile', dest='chunkfile', type='string',\
        help="Location of the file with the chunk of temporary files \
        to work with")

parser.add_option('--fil',dest='FILNAME',type='string',\
        help="name of the fil file to process")

parser.add_option('--taskno',dest='taskno',type='string',\
        help="task number, slurm stuff...")

parser.add_option('--is-fil', dest='is_fil', action='store_true', \
        help="If you have .fil files and don't need to convert .dd files. \
        USE transformer.py FIRST! \
        Default: True", default=True)

parser.add_option('--nosub', dest='no_subband', action='store_true', \
        help="Don't subband. Default: Use subbands", default=False)

parser.add_option('--DDlo', dest='DDloDM', type='float', \
        help="Lower DM limit (in pc cm**-3) for DDplan. Default: 0.0", \
        default=0.0)

parser.add_option('--DDhi', dest='DDhiDM', type='float', \
        help="Upper limit (in pc cm**-3) for DDplan. Default: 5000.0", \
        default=5000.0)

parser.add_option('--is-mask', dest='ismask', action='store_true', \
        help="If you already have a mask file, i.e. you have already ran \
        rfifind. Default: False", \
        default=False)

parser.add_option('--sorter', dest='sorter', type='string', \
        help="DON'T RECOMMEND CHANGING THIS! By which argument to sort the EventSummary.txt file, options are \
        dm, sn (or s/n), m (or m_i), t (or time). (DM, signal to noise, modulation index,time). \
        Default: t", default="t") # should add time as well?

# skipping waterfaller options

(opts,args) = parser.parse_args()

dddir = opts.dddir # quick fix because I forgot to prepend opts while writing
RESDIR = opts.RESDIR
'''#print dddir
#print RESDIR
#print os.system("ls "+ dddir)
print "ls RESDIR"
print os.system("ls "+ RESDIR)
print "END ls RESDIR"
print "RESDIR"
print RESDIR
print "END RESDIR"
print "chunkfile"
print opts.chunkfile
print "end chunkfile"'''
'''
    TIMING

    t_dd
    t_rfifind
    t_prepsubb
    t_sps
    t_waterfall
    t_tot
'''
os.system("mkdir " + RESDIR) # create the result directory
timname = "timing.txt"
timout = os.path.join(RESDIR,timname)
with open(timout,'a') as timfile:
    timfile.write("Time for tasks in [s] \n")
#with open(RESDIR + "timing.txt",'w') as timfile: # a file measuring time for tasks
#    timfile.write("Time for tasks in [s] \n")
t0 = time.time()

'''
    CONVERSION OF .dd TO .fil

    THIS WILL BE DONE IN transformer.py!!!
'''
extension_old = '.dd'
extension_new = '.fil'
dot = '.'
'''if not opts.is_fil: # if directory does not have .fil, the .dd files need to be converted
    dir_filenames = []
    # fetch all filenames in the .dd directory
    for (dirpath,dirnames,filenames) in os.walk(dddir):
        dir_filenames.extend(filenames)
        break

    dd_filenames = []
    # append all .dd files in directory to an array/list/whatever
    # files are appended without extension
    for i in range(len(dir_filenames)):
        tmpfilename = [dot.join(dir_filenames[i].split(dot)[0:-1]), dir_filenames[i].split(dot)[-1]]
        if (tmpfilename[1]=='dd'):
            dd_filenames.append(tmpfilename[0])

    # convert .dd to .fil
    for i in range(len(dd_filenames)):
        datafilename = dd_filenames[i]
        os.system("filterbankPFFTS " + dddir + datafilename + extension_old + \
                " -o " + dddir + datafilename + extension_new)
'''
t1 = time.time()
t_dd = t1 - t0

'''
    INITIALIZE .fil ARRAY FOR LOOPING
    essentially the same as above, but for the fresh, new .fil files

    NB: WILL GIVE SOME FILES AS INPUT, SO I WON'T NEED THIS
'''
'''dir_filenames = [] # don't need the old one
for (dirpath,dirnames,filenames) in os.walk(dddir):
    dir_filenames.extend(filenames)
    break

fil_filenames = []
for i in range(len(dir_filenames)):
    tmpfilename = [dot.join(dir_filenames[i].split(dot)[0:-1]), dir_filenames[i].split(dot)[-1]]
    if (tmpfilename[1]=='fil'):
        fil_filenames.append(tmpfilename[0])
'''
'''
    CREATE DATABASE TABLE
'''
#with open(opts.chunkfile,'r') as FILE: # create list from the files given in chunkfile
#	lines = FILE.readlines()
#	fil_filenames = []
#	for i,line in enumerate(lines):
#		theline = line.split('\n')[0]
#		fil_filenames.append(theline)
#fil_filenames = [i.split('\n')[0] for i in lines]
#with open(dddir + 'tmpFILfiles.txt','r') as FFF:
#	lines2 = FFF.readlines()
#	fil_filenames = []
#fil_filenames = [i.split('\n')[0] for i in lines2]
#fil_filenames = ['fakeone_one_FRB','fakeone_two_FRB_FRB','faketwo_two_FRB','faketwo_one_FRB']
#fil_filenames = np.asarray(fil_filenames)
#with open(opts.chunkfile,'r') as f:
#	lines = f.readlines()
#	print lines
#	print "oooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"
#with open(RESDIR + 'tmpFILfiles.txt','r') as f:
#	lines = f.readlines()
#fil_filenames = [i.split('\n')[0] for i in lines]
'''
fil_filenames = np.loadtxt(opts.chunkfile,dtype='string')
print "FIL FILENAMES"
print fil_filenames
print "FIL FILENAMES"
'''
#dbmaker.create_table(RESDIR) # create database and table # DO THIS IN runshell.py

#db = RESDIR + "ZPipeDB.sqlite" # string to database
###db = os.path.join(RESDIR,"ZPipeDB.sqlite")
db = os.path.join(RESDIR,"PipelineDB.sqlite")

#dbmaker.add_names(db,fil_filenames) # adds fil names to table

'''
    DDplan.py

    -l : low DM; -d : high DM; -s : subbands; -n : channels; -f : center freq.
    -b : bandwidth; -t : sample time; -r : acceptable time resolution (ms)

    Only need to run once
'''
'''
def gather_files(DIR):
    dir_filenames = []
    for (dirpath,dirnames,filenames) in os.walk(DIR):
        dir_filenames.extend(filenames)
        break
    fil_filenames = []
    for i in range(len(dir_filenames)):
        tmpfilename = ['.'.join(dir_filenames[i].split('.')[0:-1]),dir_filenames[i].split('.')[-1]]
        if (tmpfilename[1]=='fil'):
            fil_filenames.append(tmpfilename[0])
    return fil_filenames
'''
#THEFILES = gather_files(dddir)
#fil_filenames = THEFILES
#print fil_filenames
#first_fil = dddir + 'fakeone_one_FRB' + extension_new
'''
if fil_filenames.size==1:
    fil_filenames = fil_filenames.reshape(1,)
'''
###first_fil = dddir + fil_filenames[int(opts.taskno)-1] + extension_new # SLURM array test
#first_fil = dddir + fil_filenames[0] + extension_new # grab first .fil file
first_fil = os.path.join(dddir,opts.FILNAME + ".fil")
first_filfil = filterbank.FilterbankFile(first_fil)
numchan = first_filfil.nchan # number of channels
subb = int(numchan/8) # number of subbands to use
freqs = first_filfil.frequencies # list of frequencies
central_freq = np.median(freqs) # central frequencies
bandw = freqs[0]-freqs[-1] # bandwidth
samptime = first_filfil.tsamp # sample time
# Run DDplan.py and save terminal print to a .txt file
###DDtxt = "DDtxtfile.txt"
###DDpath = os.path.join(RESDIR,DDtxt)
''' JUST USE THE DDPLAN FILE ALREADY EXISTING
if not os.path.isfile(DDpath):
    with open(DDpath,'w') as aaa:
        print "creating DDplan txt file"
    DDeps = "outTrashDD"
    DDout = os.path.join(RESDIR,DDeps)
    os.system("DDplan.py -l " + str(opts.DDloDM) + \
            " -d " + str(opts.DDhiDM) + \
            " -s " + str(subb) + \
            " -n " + str(int(numchan)) + \
            " -f " + str(central_freq) + \
            " -b " + str(bandw) + \
            " -t " + str(samptime) + \
            " -r " + str(1.0) + \
            " -o " + DDout + \
            " >> " + DDpath)
            #" -o " + RESDIR + "outTrashDD " + \
            #" >> " + DDpath)
            #" > " + RESDIR + "DDtxtfile.txt")
'''
# Open DD .txt file
#f = open(RESDIR + "DDtxtfile.txt", 'r')
'''f = open(DDpath,'r')
# read file, create empty array to put in DDplan table
lines = f.readlines()
deleters = [] # need this for deleting empty lines later on, you'll see
DDresults = np.zeros([15,9]) # make it long enough

# Find the DDplan table
for i,line in enumerate(lines):
    if 'WorkFract' in line:
        DDstartpoint = i + 1

for i,line in enumerate(lines[DDstartpoint:-1]):
    if not lines[DDstartpoint+i].split():
        break
    for j in range(len(lines[DDstartpoint].split())):
        DDresults[i,j] = float(lines[DDstartpoint+i].split()[j])

# Find empty lines at bottom of table
for i,line in enumerate(DDresults):
    if not line.any():
        deleters.append(i) # add empty line numbers into deleters

# Delete empty lines in DDresults arrray
for x in reversed(deleters): # have to do it backwards
    DDresults = np.delete(DDresults,x,0)

f.close()
'''
DD_path = DDplanmaker.create_DDplan(RESDIR,first_fil,opts.DDloDM,opts.DDhiDM)
DDresults = DDplanmaker.read_DDplan(DD_path)
#DDplanmaker.remove_DDfiles(DD_path) # remove txt and eps files that DDplan creates
# Sort DDresults
LoDM = DDresults[:,0] ; HiDM = DDresults[:,1] ; dDM = DDresults[:,2]
DownSamp = DDresults[:,3] ; dsubDM = DDresults[:,4] ; numDMs = DDresults[:,5]
DMsCall = DDresults[:,6] ; Calls = DDresults[:,7]
numjobs = len(LoDM)
'''
    DDplan.py gives the following info (dedispersion plan):
    LowDM   HighDM  dDM Downsampling    dsubDM  numDMs  DMs/call    calls   workfract
'''

'''
    Main Loop: (looping over every .fil file)
        rfifind
        prepsubband
        single_pulse_search
        waterfaller
        moments/modulation index
        rrattrap
        create new singlepulse files
        write out final results for each .fil (EventSummary.txt)
        
        NB: should add some extra features
            summarize all EventSummary files
            plots (S/N v m_I; S/N v DM; freq v time, etc)

'''
#for x in range(len(fil_filenames)):
def THE_PROCESS(FILFILE):
    print "###################################"
    print "#### MAIN LOOP ITERATION START ####"
    print "###################################"
    print "### WORKING ON FILTERBANK FILE: ###"
    print FILFILE
    print "###################################"
    #fil_filenames = np.loadtxt(opts.chunkfile,dtype='string')
    #current_fil = fil_filenames[x] # current .fil without extension
    #current_fil = fil_filenames[FILFILE]
    current_fil = FILFILE
    tmpdir = RESDIR + current_fil + "/" # a sub-dir for this .fil results
    tmpfil = dddir + current_fil + extension_new # path to current .fil
    os.system("mkdir " + tmpdir) # make dir for current .fil results
    prepdir = tmpdir + "prepsub/" # sub-sub-dir for prepsubband results
    subdir = tmpdir + "subbands/" # sub-sub-dir for subband results
    logdir = tmpdir + "logs/" # sub-sub-dir for logs
    os.system("mkdir " + prepdir) # create prepsubband dir
    os.system("mkdir " + subdir) # create subband dir
    os.system("mkdir " + logdir)
    sampsize = filterbank.FilterbankFile(tmpfil).dt
    numsamps = filterbank.FilterbankFile(tmpfil).N
    lenfilterbank = sampsize*numsamps/60.
    approxlen = round(lenfilterbank,1)
    print RESDIR
    print db
    print current_fil
    newdb.update_init(db,current_fil,approxlen)
    # CX observation manual channel zapping
    # different for upper and lower bandwidth ranges
    # and different for upper and lower bandwiths of ranges
    # for upper range:
    #       top band : 8800,8300,7800 MHz   - channel no: 507:517,1019:1029,1531:1541
    #       low band : 6301,5340-5440 MHz   - channel no: 40-146, 1021-1031
    #   shift values more to the left? at least for the low band
    # for lower range:
    #       top band : 7700 MHz             - channel no: 1736:1746
    #       low band : 5850,5001,4152 MHz   - channel no: 151:161,1020:1030,1889:1899
    # 1689:1792 is 4250:4350 MHz, because there is constant squiggly RFI in these channels
    cx_top = False # if I'm working on the top range of CX receiver data
    cx_obs = True # if I'm working on CX receiver data
    if cx_top and cx_obs:
        if tmpfil.endswith("FB0_NEWHEAD.fil"):
            zappys = "30:146,1016:1036"
        elif tmpfil.endswith("FB1_NEWHEAD.fil"):
            zappys = "502:522,1014:1034,1526:1546" 
        else:
            ##zappys = "30:146,1016:1036"
            zappys = "0:200,1016:1036"
    if cx_obs and not cx_top:
        if tmpfil.endswith("FB0_NEWHEAD.fil"):
            #zappys = "0:10,1020:1030,146:166,1015:1035,1884:1904,2040:2048,1689:1792" 
            zappys = "0:10,1020:1030,2020:2048,1689:1792,592:634"
        elif tmpfil.endswith("FB1_NEWHEAD.fil"):
            zappys = "0:50,1020:1030,1731:1751,2040:2048"
        else:
            ##zappys = "30:146,1016:1036"
            zappys = "0:200,1016:1036"
    '''
        rfifind
    '''
    t2 = time.time()
    if opts.ismask: # if you have masks already
        tmpdirfiles = []
        for (dirpath,dirnames,filenames) in os.walk(tmpdir):
            tmpdirfiles.extend(filenames)
            break
        for i in range(len(tmpdirfiles)):
            tmpdirfilename = [dot.join(tmpdirfiles[i].split(dot)[0:-1]),tmpdirfiles[i].split(dot)[-1]]
            if (tmpdirfilename[1]=='mask'):
                current_mask = tmpdir + tmpdirfilename[0] + ".mask"
    else: # test changes to rfifind on testPSRs (one file) and see what happens
        os.system("rfifind -time 2.0 " + \
                "-o " + tmpdir + current_fil + \
                " " + tmpfil + \
                " " + "-zapchan " + zappys + \
                " " + "-chanfrac 0.7" + \
                " " + "-timesig 10" + \
                " " + "-intfrac 0.3" + \
                " | tee " + logdir + "RFI_LOG01.txt")
        current_mask = tmpdir + current_fil + "_rfifind.mask"
#        os.system("rfifind -nocompute -time 1.0 -freqsig 6.0 " + \
#                "-mask " + current_mask + \
#               " -o " + tmpdir + current_fil + \
#               " | tee " + logdir + "RFI_LOG02.txt")

    t3 = time.time()
    t_rfifind = t3 - t2

    '''
        prepsubband
    '''
    for ddplan in range(numjobs):
        tmpLoDM = LoDM[ddplan] # lower DM limit for current DDplan job
        sub_dmstep = DMsCall[ddplan] * dDM[ddplan] # subband DM range for current job
        for call in range(int(Calls[ddplan])):
            lowDMprep = LoDM[ddplan] + call * sub_dmstep # lower DM limit for current call
            logname = "LOG_" + current_fil + "_Plan" + str(ddplan+1) + "_Call" + str(call+1)
            if opts.no_subband: # if no subband flag is set
                os.system("prepsubband -mask " + current_mask + \
                        " -nobary" + \
                        " -lodm " + str(lowDMprep) + \
                        " -dmstep " + str(dDM[ddplan]) + \
                        " -numdms " + str(int(DMsCall[ddplan])) + \
                        " -downsamp " + str(int(DownSamp[ddplan])) + \
                        " -o " + prepdir + current_fil + " " + \
                        tmpfil + \
                        " | tee " + logdir + logname + "_nosub.txt")
            else: # using subbands
                tmpsubdm = tmpLoDM + (call + .5) * sub_dmstep # done in plazar's pipeline, can't
                # remember fully the reasoning behind this
                os.system("prepsubband " + tmpfil + \
                        " -nobary" + \
                        " -sub -subdm " + str(tmpsubdm) + \
                        " -downsamp " + str(int(DownSamp[ddplan])) + \
                        " -nsub " + str(subb) + \
                        " -mask " + current_mask + \
                        " -o " + subdir + current_fil + \
                        " | tee " + logdir + logname + "_sub01.txt")
                tmpsubname = current_fil + "_DM" + str(tmpsubdm)
                os.system("prepsubband -lodm " + str(lowDMprep) + \
                        " -dmstep " + str(dDM[ddplan]) + \
                        " -numdms " + str(int(DMsCall[ddplan])) + \
                        " -downsamp " + str(1) + \
                        " -nobary" + \
                        " -nsub " + str(subb) + \
                        " -o " + prepdir + current_fil + " " + \
                        subdir + tmpsubname + "0.sub[0-9]*" + \
                        " | tee " + logdir + logname + "_sub02.txt")
    t4 = time.time()
    t_prepsubb = t4 - t3

    '''
        single_pulse_search
    '''
    # run single_pulse_search.py on every .dat file given by prepsubband
    # set a S/N threshold of 5
    # add -m option (20 ms) : MAXWIDTH, set the max downsampling in sec
    # Don't plot
    # Break down to X many chunks, and plot chunks instead, because the
    # filterbanks are a few hours long
    logname2 = "SPLOG" + current_fil
    print "Running sinigle_pulse_search.py..."
    os.system("single_pulse_search.py -t 7.0 -m 0.02 -b -p " + \
            prepdir + "*.dat" + \
            " | tee " + logdir + logname2 + ".txt")
    spsbreak.spsbreakdown(prepdir,tmpfil)
    ###sps_brkdown(prepdir,tmpfil) # works locally with singularity
	# maybe it's an issue just on numerix0
    #BREAKDOWN = 4 # THIS PART IS NOT WORKING AS INTENDED!!!
    #FIL_fil = filterbank.FilterbankFile(tmpfil)
    #FIL_DUR = FIL_fil.dt * FIL_fil.nspec
    #for i in range(BREAKDOWN):
    #    sps_start = (i)*FIL_DUR/float(BREAKDOWN)
    #    sps_stop = (i+1)*FIL_DUR/float(BREAKDOWN)
    #    os.system("single_pulse_search.py -s " + str(sps_start) + \
    #            " -e " + str(sps_stop) + " " + prepdir + "*.singlepulse")
    print "single_pulse_serach.py finished!"

    t5 = time.time()
    t_sps = t5 - t4

    # make an array with all the .singlepulse files
    spdir_files = []
    for (dirpath,dirnames,filenames) in os.walk(prepdir):
        spdir_files.extend(filenames)
        break

    sp_files = []
    for i in range(len(spdir_files)):
        tmpfilename = [dot.join(spdir_files[i].split(dot)[0:-1]),spdir_files[i].split(dot)[-1]]
        if (tmpfilename[-1]=='singlepulse'):
            sp_files.append(tmpfilename[0])

    # Run RRATtrap mod, which creates groups of candidates, and gives a time window for 
    # the candidates, in which we will look for events of interest
    # Had to hack the original one a bit to make it work
    # COMMENTED OUT FOR TESTING PURPOSES 18.5.'17
    rrattrapmod.wholetrap(dDM[-1]+2,prepdir,tmpdir) # ADDED +2 to FIX?

    # Call momentmod.py, which takes in .fil file, list of singlepulse file names,
    # and the singlepulse file directory. Checks the singlepulse files for events
    # with high S/N, and then computes the moments and modulation index of these
    # events and writes them on a NEWsinglepulse file
    print "Running singleplus mod, creating extended singlepulse files"
    print "Take a coffee break, nap, or enjoy some other recreational activity, this might take a while"
    SAMPSIZE, RAWDATAFILE = newsps2.giantsps(tmpfil,sp_files,prepdir,tmpdir)
    num_waters = newsps2.gullfoss(tmpfil,RAWDATAFILE,tmpdir,SAMPSIZE)
    ###singleplus(tmpfil,sp_files,prepdir,tmpdir)
    print "Singleplus mod finished"
    t6 = time.time()
    t_waterfall = t6 - t5
    t_tot = (t6 - t0)/3600.
    # run spsummarizer
    new_sp_dir = prepdir + "_NEWSPs/"
    ###nevents = spsummarizer.spsum(tmpfil,new_sp_dir,tmpdir,opts.sorter)
    print "###################################################"
    print "###################################################"
    print "###################################################"
    print "sorter: ", opts.sorter
    print "###################################################"
    print "###################################################"
    print "###################################################"

    #with open(RESDIR + "timing.txt", 'a') as timfile:
    with open(timout,'a') as timfile:
        timfile.write("Fil: " + current_fil + "\n")
        timfile.write("t_dd: " + str(t_dd) + "\n")
        timfile.write("t_rfifind: " + str(t_rfifind) + "\n")
        timfile.write("t_prepsubb: " + str(t_prepsubb) + "\n")
        timfile.write("t_sps: " + str(t_sps) + "\n")
        timfile.write("t_waterfall: " + str(t_waterfall) + "\n")
    print "###############################"
    print "### MAIN LOOP ITERATION END ###"
    print "###############################"
    # Create plots showing S/N vs m_I
    # gathersps "cat"s all pulses from NEWsps to make it easier to read and plot
    # plotstuff creates two figures of S/N vs m_I
    ###gathersps(prepdir + "_NEWSPs/", tmpdir)
    gathersps2(prepdir,tmpdir)
    counter = plotstuff(tmpdir,tmpfil) # TEMPORARILY COMMENTED OUT FOR TESTING
    # UPDATE DATABASE
    nevents = 0
    # REMOVE .dat and .sub file, go green, save space
    rm_string = "rm -f "
    ending1 = "*.dat"
    rm_command = os.path.join(prepdir,ending1)
    rm_string2 = "rm -f "
    ending2 = "*.sub*"
    rm_command2 = os.path.join(subdir,ending2)
    os.system(rm_string + rm_command) # COMMENTED OUT FOR NOW TO SEE .dat FILES
    os.system(rm_string2 + rm_command2)
    ###dbmaker.update_stuff(db,current_fil,nevents,counter)
    # processing time currently set to 0 for now, maybe add later
    # number under threshold maybe add later, set to 0 for now
    newdb.update_end(db,current_fil,0,num_waters,0,1)

THE_PROCESS(opts.FILNAME)
######THE_PROCESS(fil_filenames[int(opts.taskno)-1]) #SLURM array test
#THE_PROCESS(fil_filenames[0]) # CHUNKFILES WILL ONLY HAVE ONE FILE IN THEM NOW, SO RUN THIS
# AND COMMENT OUT THE POOL STUFF

#blablabla = np.arange(len(fil_filenames))
###pool = Pool(processes=8)
#pool.map(THE_PROCESS,blablabla)
###pool.map(THE_PROCESS,fil_filenames)
#pool.map(THE_PROCESS,np.asarray(fil_filenames))

#THEFILES = gather_files(dddir)

#splitter = 3

#SPLITF = np.array_split(THEFILES,splitter)

#procs = []
#print "starting multiprocessing pool"
#for i in range(splitter):
#    print "################################"
#    print "### WE'RE GOING TO THE POOL: ###"
#    print SPLITF[i]
#    print "################################"
#    pool = Pool(processes=3)
#    pool.map(THE_PROCESS,SPLITF[i])
    #proc = Process(target=THE_PROCESS,args=(SPLITF[i],))
    #procs.append(proc)
    #proc.start()
#for proc in procs:
    #proc.join()

#procs = []
#for index,number in enumerate(fil_filenames):
#	proc = Process(target=THE_PROCESS,args=(fil_filenames,))
#	procs.append(proc)
#	proc.start()
#for proc in procs:
#	proc.join()

print "Script end!"
current_time = time.strftime("%c")
print "End time of script"
print current_time








