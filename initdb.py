import os
import numpy as np
import sys
#from dbmaker import create_table,add_names
from newdb import create_table,add_names
'''

Comments Nov 2017

creates database

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


'''def db_stuff(DIR,FILES):
    create_table(DIR)
    dbdb = 'ZPipeDB.sqlite'
    db = os.path.join(DIR,dbdb)
    add_names(db,FILES)'''

def db_stuff(DIR):
    fileDIR = '/data/'
    #FILES = gather_files(DIR)
    FILES = gather_files(fileDIR)
    create_table(DIR)
    print "TABLE CREATED"
    ###dbdb = 'ZPipeDB.sqlite'
    dbdb = '/data/results/PipelineDB.sqlite'
    db = os.path.join(DIR,dbdb)
    add_names(db,FILES)
    print "NAMES ADDED TO DB"

if __name__=='__main__':
    DIR = "/data/results/"
    #files = gather_files(DIR)
    #db_stuff(DIR,files)
    db_stuff(DIR)

