
'''

i take filterbank file
ii insert FRB
iii rename file to original file name

repeat steps ii and iii until all FRBs are injected
'''

import numpy as np
import os
import oldfake as fake

#filfiles = ['GRB050826_CX.fil','GRB111225A_CX.fil','LSQ12DLF_CX.fil','PTF10BJP_CX.fil','GRB051109B_CX.fil','PTF12DAM_CX.fil']
#filfile = filfiles[0]
#filfile = 'GRB050826_CX.fil'
#orig_names = ['GRB050826_CX.fil','GRB111225A_CX.fil','LSQ12DLF_CX.fil','PTF10BJP_CX.fil','GRB051109B_CX.fil','PTF12DAM_CX.fil']
#orig_name = 'GRB050826_CX.fil'
#new_names = ['GRB050826_CX_FRB.fil','GRB111225A_CX_FRB.fil','LSQ12DLF_CX_FRB.fil','PTF10BJP_CX_FRB.fil','GRB051109B_CX_FRB.fil','PTF12DAM_CX_FRB.fil']
#new_name = 'GRB050826_CX_FRB.fil'

DMs = [200,400,600,800]
times = np.arange(10,236,15)
time1 = [10,70,130,190]
time2 = [25,85,145,205]
time3 = [40,100,160,220]
time4 = [55,115,175,235]
#SNs = [6,10,25,100]
# testing with super high SNs
SNs = [10,15,25,40]
#widths1 = [.5e-3,2.e-3,9.2e-3,16.e-3] 
#widths2 = [16.e-3,.5e-3,2.e-3,9.2e-3]
#widths3 = [9.2e-3,16.e-3,.5e-3,2.e-3]
#widths4 = [2.e-3,9.2e-3,16.e-3,.5e-3]

#widths1 = [.3e-3,1.e-3,3.e-3,6.e-3] 
#widths2 = [6.e-3,.3e-3,2.e-3,3.e-3]
#widths3 = [3.e-3,6.e-3,.3e-3,2.e-3]
#widths4 = [2.e-3,3.e-3,6.e-3,.3e-3]

widths1 = [2.e-3,6.e-3,10.e-3,20.e-3] 
widths2 = [20.e-3,2.e-3,6.e-3,10.e-3]
widths3 = [10.e-3,20.e-3,2.e-3,6.e-3]
widths4 = [6.e-3,10.e-3,20.e-3,2.e-3]
### add options to main so I can call it
#for i in range(6):
#    filfile = filfiles[i]
#    orig_name = orig_names[i]
#    new_name = new_names[i]
filfile = "sbeam300.fil"
orig_name = "sbeam300.fil"
new_name = "sbeam300_FRB.fil"
for i in range(4):
    # parameters for injector
    DM = DMs[i]
    ###DM = 500
    width = widths1[i]
    ###width = .5e-3
    SN = SNs[i]
    ###SN = 15
    ###time = time1[i]
    time = time1[i]
    onebit = False
    # run the injector
    print "Putting fake FRB in file %s" % filfile
    print "Tiime: %s, DM: %s, SN: %s, width: %s" % (time,DM,SN,width)
    fake.main(filfile,time,DM,width,SN,onebit)
    # rename the file to its original name
    os.system('mv %s %s' % (new_name,orig_name))
for i in range(4):
    # parameters for injector
    DM = DMs[i]
    ###DM = 500
    width = widths2[i]
    ###width = 4.e-3
    SN = SNs[i]
    ###SN = 15
    ###time = time1[i]
    time = time2[i]
    onebit = False
    # run the injector
    print "Putting fake FRB in file %s" % filfile
    print "Tiime: %s, DM: %s, SN: %s, width: %s" % (time,DM,SN,width)
    fake.main(filfile,time,DM,width,SN,onebit)
    # rename the file to its original name
    os.system('mv %s %s' % (new_name,orig_name))
for i in range(4):
    # parameters for injector
    DM = DMs[i]
    ###DM = 500
    width = widths3[i]
    ###width = 9.e-3
    SN = SNs[i]
    ###SN = 15
    ###time = time1[i]
    time = time3[i]
    onebit = False
    # run the injector
    print "Putting fake FRB in file %s" % filfile
    print "Tiime: %s, DM: %s, SN: %s, width: %s" % (time,DM,SN,width)
    fake.main(filfile,time,DM,width,SN,onebit)
    # rename the file to its original name
    os.system('mv %s %s' % (new_name,orig_name))
for i in range(4):
    # parameters for injector
    DM = DMs[i]
    ###DM = 500
    width = widths4[i]
    ###width = 12.e-3
    SN = SNs[i]
    ###SN = 15
    ###time = time1[i]
    time = time4[i]
    onebit = False
    # run the injector
    print "Putting fake FRB in file %s" % filfile
    print "Tiime: %s, DM: %s, SN: %s, width: %s" % (time,DM,SN,width)
    fake.main(filfile,time,DM,width,SN,onebit)
    # rename the file to its original name
    os.system('mv %s %s' % (new_name,orig_name))
