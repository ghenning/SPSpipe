import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
#import plotmaster
#import plotmaster02
#import plotmaster03
import plotmaster03b
import optparse

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

def replotting(DIR):
    filenames = gather_files(DIR)
    for i in range(len(filenames)):
        naked_file = filenames[i]
        current_file = filenames[i] + '.fil'
        path_to_file = os.path.join(DIR,current_file)
        path_to_text = os.path.join(DIR,'results',naked_file,'')
        plotmaster03b.plotstuff(path_to_text,path_to_file)
        #try:
        #    plotmaster02.plotstuff(path_to_text,path_to_file)
        #except:
        #    print 'computer says no'

def replotting2(TXTDIR,FILDIR):
    filenames = gather_files(FILDIR)
    for i in range(len(filenames)):
        naked_file = filenames[i]
        current_file = filenames[i] + '.fil'
        path_to_file = os.path.join(FILDIR,current_file)
        path_to_text = os.path.join(TXTDIR,naked_file,'')
        plotmaster03b.plotstuff(path_to_text,path_to_file)

if __name__=='__main__':
    desc = "hi, I'm a description"
    parser = optparse.OptionParser(description=desc)
    parser.add_option('--dir',dest='DIR',type='string',\
        help="directory of filterbanks")
    parser.add_option('--two-dirs',dest='two_dirs',action='store_true',\
        help="if directories are not ''standard'', then use this flat and \
                give both the filterbank and text file directories", default=False)
    parser.add_option('--txtdir',dest='TXTDIR',type='string',\
        help="directory level above text files, i.e. the ''results'' directory")
    (opts,args) = parser.parse_args()
    if opts.two_dirs:
        replotting2(opts.TXTDIR,opts.DIR)
    else:    
        replotting(opts.DIR)





