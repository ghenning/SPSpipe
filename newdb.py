'''
    updated version of old database

    table:
    name - len of file - start time - end time - processing time - num waterfalls - num waterfalls beneath threshold
    name, len, start should go in init
    end, process time, num waterfalls, num good waterfalls go in end

    create_table: creates database and table

    add_names: adds filterbank file names to table
   
    update_stuff: adds stuff to table

    get_stuff: prints table
'''

import sqlite3
import os

def create_table(DIR):
    sq_name = "PipelineDB.sqlite"
    sqlite_file = os.path.join(DIR,sq_name)
    if os.path.isfile(sqlite_file):
        print "THE DB FILE ALREADY EXISTS"
        return
    table_name = "STATUS"
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c1 = "FIL_NAME"
    c2 = "LEN_FILE"
    c3 = "START_TIME"
    c4 = "END_TIME"
    c5 = "PROCESSING_TIME"
    c6 = "NUM_WATERFALLS"
    c7 = "WATERFALLS_THRESH"
    c8 = "PROCESSED"
    c9 = "CHECKED"
    ctype1 = "TEXT"
    ctype2 = "INTEGER"
    c.execute("CREATE TABLE {tn} ({nf} {ft})"\
        .format(tn=table_name, nf=c1, ft=ctype1))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=c2, ct=ctype1))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=c3, ct=ctype1))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=c4, ct=ctype1))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=c5, ct=ctype1))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=c6, ct=ctype2))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=c7, ct=ctype2))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=c8, ct=ctype2))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn=table_name, cn=c9, ct=ctype2))
    conn.commit()
    conn.close()

def add_names(db,filfiles):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for i in filfiles:
        c.execute("SELECT FIL_NAME FROM STATUS WHERE FIL_NAME = ?", (i,))
        data = c.fetchall()
        if len(data)==0:
            c.execute('insert into STATUS values (?,?,?,?,?,?,?,?,?)', (i,None,None,None,None,None,None,0,0))
    conn.commit()
    conn.close()

def update_init(db,filfile,length):
    import time
    conn = sqlite3.connect(db)
    c = conn.cursor()
    timtim = time.strftime("%c")
    sql = ''' UPDATE STATUS SET LEN_FILE = ?, START_TIME = ? WHERE FIL_NAME = ? '''
    c.execute(sql,(length,timtim,filfile))
    conn.commit()
    conn.close()

def update_end(db,filfile,processing,num_water,num_thresh,processed):
    import time
    conn = sqlite3.connect(db)
    c = conn.cursor()
    timtim = time.strftime("%c")
    sql = ''' UPDATE STATUS SET END_TIME = ?, PROCESSING_TIME = ?, NUM_WATERFALLS = ?, WATERFALLS_THRESH = ?, PROCESSED = ? WHERE FIL_NAME = ? '''
    c.execute(sql,(timtim,processing,num_water,num_thresh,processed,filfile))
    conn.commit()
    conn.close()

def checked_stuff(db,filfile):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = ''' UPDATE STATUS SET CHECKED = ? WHERE FIL_NAME = ? '''
    c.execute(sql,(1,filfile))
    conn.commit()
    conn.close()

def uncheck_stuff(db,filfile):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = ''' UPDATE STATUS SET CHECKED = ? WHERE FIL_NAME = ? '''
    c.execute(sql,(0,filfile))
    conn.commit()
    conn.close()

def get_stuff(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM STATUS')
    all_rows = c.fetchall()
    for row in all_rows:
        print row
'''
def db_stuff(DIR):
    fileDIR = '/data/'
    FILES = gather_files(fileDIR)
    create_table(DIR)
    print "TABLE CREATED"
    dbdb = 'PipelineDB.sqlite'
    db = os.path.join(DIR,dbdb)
    add_names(db,FILES)
    print "NAMES ADDED TO DB"

def gather_files(DIR):
    dir_filenames = []
    for (dirpath,dirnames,filenames) in os.walk(DIR):
        dir_filenames.extend(filenames)
    fil_filenames = []
    for i in range(len(dir_filenames)):
        tmpfilename = ['.'.join(dir_filenames[i].split('.')[0:-1]),dir_filenames[i].split('.')[-1]]
        if (tmpfilename[1]=='fil'):
            fil_filenames.append(tmpfilename[0])
    return fil_filenames
'''
