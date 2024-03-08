

def getbaseip(duno, floor=100):
    jb = 1*(duno<=9) + 2*(duno>=9 and duno<=20) + 3*(duno>=21 and duno<=32)
    return F'10.{int(jb)}.{duno}.{floor}'

def printdebug(deb, msg):
    if not deb: return
    print('DEBUG: ', msg)

def parsestrlist(ss, typ=str):
    ss = ss.rstrip(' ,').replace(', ', ',').replace(' ', ',')
    if typ==str or typ==None: return ss
    return [typ(ii) for ii in parsestrlist(ss).split(',')], ss






