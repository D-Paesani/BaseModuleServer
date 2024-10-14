import subprocess

def getwwrsips(duno):
    if duno == 0: return [f'10.0.1.20{ii+1}' for ii in range(2)]
    jb = 1*(duno<=9) + 2*(duno>=9 and duno<=20) + 3*(duno>=21 and duno<=32) + \
     4*(duno>=32 and duno<=46) + \
     5*(duno>=47 and duno<=60) + 100
    return [F'10.{int(jb)}.{duno}.20{ii+1}' for ii in range(2)]

def getbaseip(duno, floor=100):
    if duno == 0: return '10.0.1.100'
    jb = 1*(duno<=9) + 2*(duno>=9 and duno<=20) + 3*(duno>=21 and duno<=32) + \
     4*(duno>=32 and duno<=46) + \
     5*(duno>=47 and duno<=60) + 100
    return F'10.{int(jb)}.{duno}.{floor}'

def printdebug(deb, msg):
    if not deb: return
    print('DEBUG: ', msg)

def parsestrlist(ss, typ=str):
    ss = ss.rstrip(' ,').replace(', ', ',').replace(' ', ',')
    if typ==str or typ==None: return ss
    return [typ(ii) for ii in parsestrlist(ss).split(',')], ss

def isDuAlive(ip):

    if not (ip := getbaseip(ip)): return False

    try:
        result = subprocess.run(['ping', '-c', '1', ip], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True  # Ping ok
        else:
            return False  # Ping failure
    except subprocess.TimeoutExpired:
        return False  # Ping timeout




