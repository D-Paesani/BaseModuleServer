import bms.controller.bms_utils as uu
import subprocess
import os
import re
from datetime import datetime
import json
from . import BASEDIR
from flask_login import current_user

usedummy = True
logerrors = False
cmdlogfile =  f'{BASEDIR}/logs/jsccmd.log'

cmdformat = 'cd /bpd-software/host/python/console/ && python2 jsendcommand2.py  {ip} {args}'
cmdformat = 'python2 %s/jsendcommand_dummy.py {ip} {args}' % (BASEDIR) if usedummy else cmdformat

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
    ss = re.search(F'MON_{param} = (.*)', sss).group(1).split(' ')
    adc = int(ss[0])
    val = float(ss[1].split('(')[1])
    unit = str(ss[2]).replace(')', '')
    return adc, val, unit

def parse_generic(sss, param):
    sss = sss.split('Received')[1]
    return re.search(F'{param} = (.*)', sss).group(1)
    
class jcmd:
    
    command = cmdformat
    
    def __init__(self, cmd, parser=None, params=None, args=None, index=None, loggeron=True, parser_opt=None):
        self.cmd = cmd
        self.parser = parser
        self.index = index
        self.logen = loggeron
        self.args = args
        self.parser_opt = parser_opt
        self.params = params if type(parser_opt) is not str else [F'{ii}_{parser_opt}' for ii in params]

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
            
            cmdlogger(cmd=cc, user=current_user, msg=F'du<{du}>', enable=self.logen)
            
            return pp
        
        except Exception as ee:
            print('--> JSC --> ERROR:', ee)
            if logerrors: cmdlogger(cmd=cc, user=current_user, msg=F'ERROR: {ee}', enable=self.logen)
            return None
        
peripheral_dict_BPD = { 
                       'veoc' :     ['1', '2'],
                       '12volts' :  ['3'],
                       'beacon' :   ['4'],
                       'hydrophone' :    ['5'],
                       }     

sens_pars_BPS =   ['5V_I', 'LBL_I', 'DU_I', 'DU_IRTN', 'BPS_V', 'HYDRO_I', 'THEATSINK', 'TBOARD',]
sens_pars_BPD =   ['DUL_BOARDTEMP','TEMP2','TEMP1','VEOC_RTN_I','VEOC_FWR_I','HYDRO_I','INPUT_V','LBL_I','GLRA_I','GLRB_I','PWB_I',]
sensor_index =    ['ADC', 'VALUE', 'UNIT']

commands = dict(
        
    sensors_val = jcmd(cmd='SENSOR_VALUES_GETALL',      parser_opt='VALUE',     args=None,  parser=parse_sensors,  params=sens_pars_BPD, index=sensor_index ),
    sensors_avg = jcmd(cmd='SENSOR_AVERAGE_GETALL',     parser_opt='MEAN',      args=None,  parser=parse_sensors,  params=sens_pars_BPD, index=sensor_index ),
    sensors_max = jcmd(cmd='SENSOR_MAXVALUES_GETALL',   parser_opt='MAXVALUE',  args=None,  parser=parse_sensors,  params=sens_pars_BPD, index=sensor_index ),

    switch      = jcmd(cmd='SWITCH_CONTROL',            args=['sw', 'state'],   parser=parse_generic,   params=['SWITCHNUM', 'SWITCHSTATE']                 ),
    rescue      = jcmd(cmd='RESCUE_ENABLE',             args=['state'],         parser=parse_generic,   params=['ENABLESTATE']                              ),
    raw         = jcmd(cmd=None,                        args=['cmdstr'],        parser=None,            params=['answ']                                     ),
    
)

