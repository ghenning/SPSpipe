# coding = utf-8

'''
    Independent from the pipeline

    Transforms all the .dd files to .fil

    Input is the directory where the .fil files are

   !!!!!!
        MAYBE INCORPORATE THE RETRIEVAL OF THE .dd FILES
        FROM THE ARCHIVE SERVER, THEN TRANSFORM THEM
        ITERATIVELY
   !!!!!!

    RUNNING THIS WITH SINGULARITY:
        singularity exec -B /path/to/.dd/files/:/data -B /path/to/code/:/work imagename.img \
            python /work/NameOfScript.py --thedir /data
'''
'''

comments Nov 2017

transforms .dd files to filterbank files

'''
import optparse
import os
from multiprocessing import Pool
import subprocess
import numpy as np

def bash_command(cmd):
    subprocess.call(['/bin/bash','-c',cmd])

extension_old = '.dd'
extension_new = '.fil'

def gather_files(DIR):
    dir_filenames = []
    for (dirpath,dirnames,filenames) in os.walk(DIR):
        dir_filenames.extend(filenames)
        break
    dd_filenames = []
    for i in range(len(dir_filenames)):
        tmpfilename = ['.'.join(dir_filenames[i].split('.')[0:-1]),dir_filenames[i].split('.')[-1]]
        if (tmpfilename[1]=='dd'):
            dd_filenames.append(tmpfilename[0])
    return dd_filenames

def splitfiles(FILES):
    splitter = np.ceil(len(FILES)/4.)
    SPLIT = np.array_split(FILES,splitter)
    return SPLIT

#def thetransform(FILE,DIR): # take a few files at once and transform with pool.map
def thetransform(FILE): # can only give one argument to pool.map
    # the dir is just the mounted /data dir with singularity
    DIR = '/data'
    current_file = FILE + extension_old
    outgoing_file = FILE + extension_new
    ddpath = os.path.join(DIR,current_file)
    filpath = os.path.join(DIR,outgoing_file)
    print "Transforming file from .dd to .fil"
    print current_file
    comm = "filterbank " + ddpath + " -o " + filpath
    bash_command(comm)
    print "Done transforming file, now removing .dd file"
    print current_file
    comm2 = "rm -f " + ddpath
    bash_command(comm2)

if __name__=='__main__':
    desc = "hi, I'm a description"
    parser = optparse.OptionParser(description=desc)
    parser.add_option('--thedir',dest='thedir',type='string',\
        help="directory of dd files")
    (opts,args) = parser.parse_args()
    files = gather_files(opts.thedir)
    split = splitfiles(files)
    for i in range(len(split)):
        tmpfiles = split[i]
        pool = Pool(processes=4)
        pool.map(thetransform,tmpfiles)

    
    

