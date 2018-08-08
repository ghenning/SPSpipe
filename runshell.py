import subprocess
import os
import sys
import numpy as np
import time
import launchmaker
#from dbmaker import create_table,add_names
#import initdb

# define bash command which I can call
def bash_command(cmd):
	#subprocess.Popen(['/bin/bash', '-c', cmd])
	subprocess.call(['/bin/bash', '-c', cmd])

# Creates a list of all the dd files 
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

#resdir = '/hercules/u/ghil/piperes/'

# splits the files into groups of 8/4/2/whatever
# for each group, I will create a txt file with the
# names of the files, which the pipeline file will read.
# Loop through groups, and for each I will call the launch
# script, which requests cores and computation time, and
# calls the pipeline script to process the group.
def split_files(FILES,RESDIR):
    #splitter = np.ceil(len(FILES)/2.) 
    splitter = 2
    print "splitter: ",splitter
    SPLITF = np.array_split(FILES,splitter)
    for i in range(int(splitter)):
        for j in range(len(SPLITF[i])):
            FIL = SPLITF[i][j]
            LODM = str(450)
            HIDM = str(650)
            RESPATH = os.path.join(RESDIR,"results")
            FILPATH = RESDIR
            CODEPATH = "/hercules/u/ghil/piperuns/obs_180622_1118/"
            JOBNAME = "1118"
            launchmaker.create_script(LODM,HIDM,FILPATH,FIL,RESPATH,CODEPATH,JOBNAME)
            make_exe = "chmod +x launch_me.sh"
            bash_command(make_exe)
            run_it = "sbatch ./launch_me.sh"
            bash_command(run_it)
        while Qstuff(RESDIR):
            print "still running portion %s of %s" % (i+1,splitter)
            time.sleep(180)
'''    for i in range(int(splitter)):
        txtout1 = 'outcrap'
        txtout2 = 'tmpFILfiles.txt'
        txtpath = os.path.join(RESDIR,txtout2)
        #txtpath = os.path.join(RESDIR,txtout1,txtout2)
        print "split chunk size: ", len(SPLITF[i])
        #with open(RESDIR + "tmpFILfiles.txt",'w') as tmpfile:
        with open(txtpath,'w') as tmpfile:
            for j in range(len(SPLITF[i])):
                tmpfile.write(SPLITF[i][j] + "\n")
                print "writing file to tmpFILfiles.txt:"
                print SPLITF[i][j]
        # ADD qsub command with the bash command!?!?
        bash_command('sbatch ./SLURMlaunch.sh') # sbatch - SLURM equiv to qsub
        while Qstuff(RESDIR):
            print "Current pool party in progress, waiting..."
            time.sleep(180)
        #bash_command('./thelaunch.sh')
        #bash_command('qsub ./thelaunch.sh')
        #bash_command('./thelaunch.sh')
        #time.sleep(30) # need to add some delay because otherwise it reads the same file again for some reason
'''
'''
    write a single FIL file name to a file, each file is then read and processed
    with SLURMlaunch.sh - mainpipe1bit.py
'''
def split_files_TEMPTEST(FILES,RESDIR):
    SPLITF = np.array_split(FILES,20) # will be 20 for 500 files
    for j in range(25): # will be 25 for 500 files
        for i in range(len(SPLITF)):
            txtout = 'FILfile' + str(i) + ".txt"
            txtpath = os.path.join(RESDIR,txtout)
            towrite = SPLITF[i][j]
            with open(txtpath,'w') as tmpfile:
                tmpfile.write(SPLITF[i][j])
        bash_command('sbatch ./SLURMlaunch.sh')
        while Qstuff(RESDIR):
            print "processing... keep waiting..."
            time.sleep(180)

def Qstuff(RESDIR):
    Qout = os.path.join(RESDIR,'Qstatus.txt')
    comm = 'squeue -u ghil > ' + Qout
    bash_command(comm)
    theQ = np.loadtxt(Qout,dtype='string')
    if theQ.ndim==1:
        return False
    YESNO = any(theQ[1:,2]=='1118')
    print "################################################"
    print "################################################"
    print YESNO
    print "################################################"
    print "################################################"
    if YESNO:
        return True
    else:
        return False
    #stsize = os.stat(Qout).st_size
    #if stsize >= 86:
    #    return True
    #else:
    #    return False

def dbstuff(DIR,FILES):
	create_table(DIR)
	dbdb = 'PipelineDB.sqlite' 
	db = os.path.join(DIR,dbdb)
	add_names(db,FILES)
	

if __name__=='__main__':
    # This script is the only one I will have to run, the rest should
    # be calles automatically, ezpz
    # Running it is just:
    # python runshell.py /path_to_dd_files/
    resdir = '/hercules/results/ghil/obs_180622_1118/'
    DIR = resdir
    files = gather_files(DIR)
    # do os.system blabla to run initdb.db_stuff with singularity
    #bash_command('module load singularity')
    comm = 'singularity exec -B /hercules/u/ghil/piperuns/obs_180622_1118/:/work -B /hercules/results/ghil/obs_180622_1118/:/data \
        /hercules/u/ghil/singularity/images/prestomod-2017-05-11-29e5097df53c.img python /work/initdb.py' # TMP PATH TEST
    bash_command(comm)
    #### TEMPORARILY OUT ###
    split_files(files,resdir) #LEAVE OUT FOR NOW... TESTING SOMETHING
    ###split_files_TEMPTEST(files,resdir)
    #### TEMPORARILY OUT ###
    #bash_command('sbatch ./SLURMlaunch.sh')   
