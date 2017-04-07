import serial

def scan():
    """scan for available ports. return a list of tuples (num, name)"""
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.portstr))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    # s.open()
    # print s.readline()
    # print s.isOpen()
    return available

if __name__=='__main__':
# def sweep():
    print "Found ports:"
    for n,s in scan():
        print "%s" % (s)