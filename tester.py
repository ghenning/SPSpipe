import numpy as np

def header(file):
    inread = ''
    while True:
        tmp = file.read(1)
        inread = inread + tmp
        flag = inread.find('HEADER_END')
        if flag != -1:
            break
    return inread

def readfixwrite(INFILE,OUTFILE):
    while 1:
        dataIn = INFILE.read(38147*2*2048)
        if len(dataIn)==0: break
        d2fix = np.fromstring(dataIn,dtype='uint8')
        d2fix = d2fix.astype('float32')
        dlen = d2fix.shape[0]
        d2fix.shape = (dlen/2048,2048)
        for i in range(2048):
            thechan = d2fix[:,i]
            fixed = thechan/(np.median(thechan)+1)
            #howmany = np.count_nonzero(fixed)
            #print howmany 
            d2fix[:,i] = fixed
        # need some scaling here???
        #print d2fix.flatten()
        d2fix = d2fix * 255 # DON'T KNOW WHAT TO PUT HERE EXACTLY
        d2fix = d2fix.astype('uint8') 
        OUTFILE.write(d2fix.flatten())
        #print np.count_nonzero(d2fix.flatten())
        #print len(d2fix.flatten())-np.count_nonzero(d2fix.flatten())
        #print d2fix.flatten()
        #print d2fix.flatten()[0:30]
        #print d2fix.flatten()[-30:]


def main():
    thefile = 'FRB121102_180622_10_FB0_NEWHEAD.fil'
    outie = 'FRBtsting.fil'
    outfile = open(outie,'w')
    infile = open(thefile,'r')
    head = header(infile)
    print len(head)
    infile.seek(len(head))
    outfile.write(head)
    readfixwrite(infile,outfile)
    infile.close()
    outfile.close()

if __name__=="__main__":
    main()



'''numbers = blabla(infile)
#print numbers[1].type
print type(numbers[1])
print len(numbers)
snarf = np.fromstring(numbers,dtype='uint8')
snarf = snarf.astype('float32')
print snarf
print len(snarf)
print snarf.shape[0]
snarf.shape=(len(snarf)/2048,2048)

#snarf.shape(snarf.shape[0]/2048,2048)
print np.shape(snarf)
onechan = snarf[:,0]
print onechan
print len(onechan)
print np.median(onechan)
divided = onechan/np.median(onechan)
print divided'''
