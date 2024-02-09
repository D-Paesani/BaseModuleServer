import utils as uu
import subprocess
import re
from datetime import datetime
import json

cmdlogfile =  '../mypath/logs/jsccmd.log'
commandformatdef = 'python2 jsendcommand_dummy.py {ip} {args}' 
# commandformatdef = 'python3 jsendcommand_dummy_3.py {ip} {args}'

def cmdlogger(cmd, user='?', msg='-', logfile=cmdlogfile, enable=True):
    if not enable: return
    try:
        with open(logfile, 'a') as outfile:
            outfile.write('\n')
            for ii, iii in zip(['TIM','CMD','OPT','USR'],[datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S'),cmd, msg, user]):
                # outfile.write(F'{" "*4 if ii != "TIM" else "--> "}{ii} = {iii}\n')
                outfile.write(F'{ii} = {iii}\n')
    except:
        print('Error logging')
            
def parse_sensors(sss, param):
    ss = re.search(F'MON_{param}_VALUE = (.*)', sss).group(1).split(' ')
    adc = int(ss[0])
    val = float(ss[1].split('(')[1])
    unit = str(ss[2]).replace(')', '')
    return adc, val, unit

def parse_generic(sss, param):
    return re.search(F'{param} = (.*)', sss).group(1)

def execandparse(du, jc):
    cc = jc.command.format(ip=uu.getbaseip(int(du)), args=jc.cmd)
    print('--> JSC --> command --> ' +  cc)
    resp = subprocess.check_output(cc, shell=True).decode('utf-8')
    pp = {}
    pp['du'] = du
    for ii in jc.params:
        pp[ii] = jc.parser(resp, ii)
    return pp, cc

class jcmd:
    
    command = commandformatdef
    
    def __init__(self, cmd, parser, params, index=None, loggeron=True):
        self.cmd = cmd
        self.parser = parser
        self.params = params
        self.index = index
        self.logen = loggeron

    def exec(self, du, opts=None):
        pp, cc = execandparse(du, self)
        cmdlogger(cmd=cc, user='?', msg=F'du{du}', enable=self.logen)
        return pp
    
commands = dict(
    sensors    = jcmd(cmd='SENSOR_VALUES_GETALL', parser=parse_sensors,   params=['5V_I', 'LBL_I', 'DU_I', 'DU_IRTN', 'BPS_V', 'HYDRO_I', 'THEATSINK', 'TBOARD'], index=['ADC', 'VALUE', 'UNIT']),
    switch     = jcmd(cmd='SWITCH_CONTROL',       parser=parse_generic,   params=['SWITCHNUM', 'SWITCHSTATE']),
    rescue     = jcmd(cmd='RESCUE_ENABLE',        parser=parse_generic,   params=['ENABLESTATE']),
)

#Stato allarmi / rescue enable / alarm flag / alarm reset

