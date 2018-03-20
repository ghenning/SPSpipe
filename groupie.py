# coding = utf-8

'''
    READS THE groups.txt FILE CREATED BY rrattrapmod.py
    AND CHECKS IF THE INPUT "number" IS WITHIN THE 
    TIME-FRAME OF THE GROUPS
    RETURNS TRUE/FALSE
'''
'''

Comments Nov 2017

groupie(time, DM, groups.txt dir)
    check if time and DM of single pulse event is within a group
groupie2(time, DM, groups.txt dir)
    checks if singlepulse is within good rank groups
    if so, returns the central time of the group

'''
import numpy as np

# CHECKS IF TIME AND DM IS WITHIN A GROUP, IF SO, IT RETURNS TRUE
def groupie(number,DM,txtpath):
    groups = np.zeros((1,6))
    thetxtfile = txtpath + "groups.txt"
    #print thetxtfile
    with open(thetxtfile,'r') as grpfile:
        lines = grpfile.readlines()
        for i,line in enumerate(lines):
            if "Group of" in line:
                tmpgrp = np.zeros((1,6))
                midm = lines[i+1]
                madm = lines[i+2]
                cent = lines[i+3]
                dura = lines[i+4]
                maxs = lines[i+5]
                rank = lines[i+6]
                tmpgrp[0,0] = float(midm.split(':')[-1].split('\n')[0])
                tmpgrp[0,1] = float(madm.split(':')[-1].split('\n')[0])
                tmpgrp[0,2] = float(cent.split(':')[-1].split('\n')[0])
                tmpgrp[0,3] = float(dura.split(':')[-1].split('\n')[0])
                tmpgrp[0,4] = float(maxs.split(':')[-1].split('\n')[0])
                tmpgrp[0,5] = float(rank.split(':')[-1].split('\n')[0])
                groups = np.append(groups,tmpgrp,axis=0)

    groups = np.delete(groups,0,0)

    ranges = np.zeros((1,2))

    for i in range(len(groups[:,0])):
        tmprange = np.zeros((1,2))
        tmprange[0,0] = groups[i,2] - .5*groups[i,3]
        tmprange[0,1] = groups[i,2] + .5*groups[i,3]
        ranges = np.append(ranges,tmprange,axis=0)

    ranges = np.delete(ranges,0,0)

    #ranknums = [0,5,6,7]
    #ranknums = [0,3,4,5,6,7]

    #ranknums = [2]
    # setting it like this for now to ignore rrattrap
    ranknums = [9999]

    statement = False

    for i in range(len(ranges[:,0])):
        rank = int(groups[i,5])
        dmlo = groups[i,0]
        dmhi = groups[i,1]
        #if (ranges[i,0] <= number <= ranges[i,1] and dmlo <= DM <= dmhi): statement = True
        if (ranges[i,0] <= number <= ranges[i,1] and dmlo <= DM <= dmhi and rank in ranknums): statement = True
        #if (ranges[i,0] <= number <= ranges[i,1] and rank in ranknums): statement = True

    return statement

# CHECKS IF ANY EVENT FROM A SINGLEPULSE FILE IS WITHIN A GROUP (TIME,DM,RANK)
# AND IF SO IT RETURNS THE CENTRAL TIME FOR EACH GROUP, WHERE momentmod02.py
# WILL LOOK FOR EVENTS CLOSEST TO THOSE CENTRAL TIMES AND PROCESS THOSE EVENTS
# SO ONLY ONE EVENT IN A GROUP FOR EACH DM WILL BE PROCESSED.
def groupie2(number,dm,txtpath):
    groups = np.zeros((1,6))
    thetxtfile = txtpath + "groups.txt"
    #print thetxtfile
    with open(thetxtfile,'r') as grpfile:
        lines = grpfile.readlines()
        for i,line in enumerate(lines):
            if "Group of" in line:
                tmpgrp = np.zeros((1,6))
                midm = lines[i+1]
                madm = lines[i+2]
                cent = lines[i+3]
                dura = lines[i+4]
                maxs = lines[i+5]
                rank = lines[i+6]
                tmpgrp[0,0] = float(midm.split(':')[-1].split('\n')[0])
                tmpgrp[0,1] = float(madm.split(':')[-1].split('\n')[0])
                tmpgrp[0,2] = float(cent.split(':')[-1].split('\n')[0])
                tmpgrp[0,3] = float(dura.split(':')[-1].split('\n')[0])
                tmpgrp[0,4] = float(maxs.split(':')[-1].split('\n')[0])
                tmpgrp[0,5] = float(rank.split(':')[-1].split('\n')[0])
                groups = np.append(groups,tmpgrp,axis=0)

    groups = np.delete(groups,0,0)

    ranges = np.zeros((1,2))

    for i in range(len(groups[:,0])):
        tmprange = np.zeros((1,2))
        tmprange[0,0] = groups[i,2] - .5*groups[i,3]
        tmprange[0,1] = groups[i,2] + .5*groups[i,3]
        ranges = np.append(ranges,tmprange,axis=0)

    ranges = np.delete(ranges,0,0)

    ranknums = [0,5,6,7]
    
    statement = False

    #for i in range(len(ranges[:,0])):
    #    rank = int(groups[i,5])
    #    if (ranges[i,0] <= number <= ranges[i,1] and groups[i,0] <= dm <= groups[i,1] and rank in ranknums): 
    #        statement = True
    
    central_times = np.empty(0)

    for i in range(len(ranges[:,0])):
        rank = int(groups[i,5])
        if (any(ranges[i,0]<=T<=ranges[i,1] for T in number) and groups[i,0] <= dm <= groups[i,1] and rank in ranknums):
            statement = True
            central_times = np.append(central_times,(groups[i,2]))
# return group start/stop to use in waterfaller
# but I need an event from singlepulse file
# so, return group start/stop and center time, find event closest to center time,
# and do the regular stuff to that event, or use group start/stop time
# probably just the regular stuff to keep it consistent
# So I'll have max 1 event per group per DM to compute
    return statement,central_times

if __name__=="__main__":
    number = sys.argv[1]
    txtpath = sys.argv[2] # path to groups.txt file, no including the file itself
    groupie(number,txtpath)
