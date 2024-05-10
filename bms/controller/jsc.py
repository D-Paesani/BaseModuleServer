import bms.controller.bms_utils  as uu
import subprocess
import os
import re
from datetime import datetime
import json
from . import BASEDIR
from flask_login import current_user

# home/km3net/applications/bps-test

logerrors = False

cmdlogfile =  f'{BASEDIR}/logs/jsccmd.log'

commandformatdef = 'python2 %s/jsend/jsendcommand_dummy_host.py {ip} {args}'  % (BASEDIR)
# commandformatdef = 'python2 %s/jsendcommand_dummy.py {ip} {args}' % (BASEDIR)
# commandformatdef = 'python3 jsendcommand_dummy_3.py {ip} {args}'

def cmdlogger(cmd, user, msg='-', logfile=cmdlogfile, enable=True):
    if not enable: return
    try:
        with open(logfile, 'a') as outfile:
            outfile.write('\n')
            for ii, iii in zip(['TIM','CMD','OPT','USR'],[datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S'),cmd, msg, user]):
                # outfile.write(F'{" "*4 if ii != "TIM" else "--> "}{ii} = {iii}\n')
                # outfile.write(F'{ii} = {iii}|')
                outfile.write(F'{iii}|')
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

class jcmd:
    
    command = commandformatdef
    
    def __init__(self, cmd, parser=None, params=None, args=None, index=None, loggeron=True):
        self.cmd = cmd
        self.parser = parser
        self.params = params
        self.index = index
        self.logen = loggeron
        self.args = args

    def exec(self, du, args=None):        
        try: 
            
            aa = '' if (self.args is None) or (args is None) else ' '.join([str(args[ii]) for ii in self.args])
            cmd = '' if self.cmd is None else self.cmd
                        
            if not (ip := uu.getbaseip(int(du))): 
                raise Exception(F'problem in retrieving DU IP: got {ip}') 
            
            cc = self.command.format(ip=ip, args=' '.join([cmd, aa]))
            print('--> JSC --> EXEC:',  cc)
            resp = subprocess.check_output(cc, shell=True).decode('utf-8')
            
            pp = {}
            pp['du'] = du
            pp['answ'] = resp
            
            if self.parser is not None:
                for ii in self.params:
                    pp[ii] = self.parser(resp, ii)
            
            # cmdlogger(cmd=cc, user=current_user, msg=F'du<{du}> args<{aa}>', enable=self.logen)
            cmdlogger(cmd=cc, user=current_user, msg=F'du<{du}>', enable=self.logen)
            
            return pp
        
        except Exception as ee:
            print('--> JSC --> ERROR:', ee)
            if logerrors: cmdlogger(cmd=cc, user=current_user, msg=F'ERROR: {ee}', enable=self.logen)
            return None
    
commands = dict(
    sensors    = jcmd(cmd='SENSOR_VALUES_GETALL', args=None,              parser=parse_sensors,   params=['5V_I', 'LBL_I', 'DU_I', 'DU_IRTN', 'BPS_V', 'HYDRO_I', 'THEATSINK', 'TBOARD'], index=['ADC', 'VALUE', 'UNIT']),
    switch     = jcmd(cmd='SWITCH_CONTROL',       args=['sw', 'state'],   parser=parse_generic,   params=['SWITCHNUM', 'SWITCHSTATE']),
    rescue     = jcmd(cmd='RESCUE_ENABLE',        args=['state'],         parser=parse_generic,   params=['ENABLESTATE']),
    raw        = jcmd(cmd=None,                   args=['cmdstr'],        parser=None,            params=['answ']),
)