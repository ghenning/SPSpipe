'''
    DEFINITIONS FOR DATABASE MANIPULATION

    create_table: creates database and table

    add_names: adds filterbank file names to table

    update_stuff: adds time of processing and no. of low m_I events

    get_stuff: prints table
'''
'''

Comments Nov 2017

create_table(directory)
    checks if the database file exists, if it does it breaks the loop, 
    if not, creates a table called Progress
        FIL_NAME PROCESSED NUM_EVENTS CAND_EVENTS CHECKED
add_names(database, filterbank files)
    adds filterbank names into database and puts None/0 to other fields
update_stuff(database, filterbank file, num events, cadidates)
    adds values to corresponding filterbank file
        processed - time of finish
        num events - low m_I events
        cand events - low m_I events near curve, not properly working/ready yet, ignore
checked_stuff(db, filfile)
    sets checked to 1
unchecked_stuff(db, filfile)
    sets checked to 0 - using spreadsheet to keep track of processing
get_stuff(db)
    prints out the database

'''
import sqlite3
import os

# CREATE DATABASE TABLE
# FOUR COLUMNS: NAME OF FIL / DATE AND TIME WHEN PROCESSED / NO. OF LOW M EVENTS / NO. OF GOOD EVENTS
# IF THE DB FILE ALREADY EXISTS, A NEW ONE ISN'T REQUIRED TO BE CREATED
def create_table(DIR):
    sq_name = "PipelineDB.sqlite"
    sqlite_file = os.path.join(DIR,sq_name)
    if os.path.isfile(sqlite_file):
        print "The DB file already exists!"
        return
    #sqlite_file = DIR + "ZPipeDB.sqlite"
    table_name = "Progress"
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    column1 = "FIL_NAME"
    column2 = "PROCESSED"
    column3 = "NUM_EVENTS"
    column4 = "CAND_EVENTS"
    column5 = "CHECKED"
    col1type = "TEXT"
    col2type = "TEXT"
    col3type = "INTEGER"
    c.execute("CREATE TABLE {tn} ({nf} {ft})"\
            .format(tn=table_name, nf=column1, ft=col1type))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
            .format(tn=table_name, cn=column2, ct=col2type))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
            .format(tn=table_name, cn=column3, ct=col3type))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
            .format(tn=table_name, cn=column4, ct=col3type))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
            .format(tn=table_name, cn=column5, ct=col3type))
    conn.commit()
    conn.close()

# ADDS NEW LINE FOR EACH FIL FILE, ONLY NAMES UPDATED
# OTHER COLUMNS ARE LEFT EMPTY UNTIL THEY HAVE BEEN PROCESSED IN PIPELINE
# ONLY ADD THE NAMES IF IT ISN'T IN THE DATABASE FILE ALREADY
def add_names(db,filfiles):
    #if os.path.isfile(db):
    #    return
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for i in filfiles:
        c.execute("SELECT FIL_NAME FROM Progress WHERE FIL_NAME = ?", (i,))
        data = c.fetchall()
        if len(data)==0:
            c.execute('insert into Progress values (?,?,?,?,?)', (i,None,None,None,0))
    conn.commit()
    conn.close()

# WHEN FIL FILE IS PROCESSED BY PIPELINE, UPDATE TABLE
# ADDS TIME WHEN PROCESSING IS FINISHED, AND NUMBER OF LOW M EVENTS
def update_stuff(db,filfile,nevents,cands):
    import time
    conn = sqlite3.connect(db)
    c = conn.cursor()
    timtim = time.strftime("%c")
    sql = ''' UPDATE Progress SET PROCESSED = ?, NUM_EVENTS = ? , CAND_EVENTS = ? WHERE FIL_NAME = ? '''
    c.execute(sql,(timtim,nevents,cands,filfile))
    conn.commit()
    conn.close()

def checked_stuff(db,filfile):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = ''' UPDATE Progress SET CHECKED = ? WHERE FIL_NAME = ? '''
    c.execute(sql,(1,filfile))
    conn.commit()
    conn.close()

def uncheck_stuff(db,filfile):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = ''' UPDATE Progress SET CHECKED = ? WHERE FIL_NAME = ? '''
    c.execute(sql,(0,filfile))
    conn.commit()
    conn.close()

# PRINTS THE TABLE
def get_stuff(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM Progress')
    all_rows = c.fetchall()
    for row in all_rows:
        print row
    #for rownum,row in enumerate(all_rows):
    #   print row
    #   print rownum

if __name__=="__main__":
    #testing stuff:
    DIR = "../dbtest/"
    db = DIR + "ZPipeDB.sqlite"
    filfiles = ['one','two','three','four','five','six','seven']
    nevents = [11,22,33,44,55,66,77]
    create_table(DIR)
    add_names(db,filfiles)
    for i in range(len(filfiles)-1):
        update_stuff(db,filfiles[i],nevents[i])
    get_stuff(db)







