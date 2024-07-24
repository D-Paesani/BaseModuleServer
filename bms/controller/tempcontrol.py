import bms.controller.bms_utils as uu
import subprocess
import os
import re
from datetime import datetime
import json
from . import BASEDIR
from flask_login import current_user


def read_temp_wwrs(duno=None, ips=None):
        
    if not ips: 
        ips = uu.getwwrsips(duno)
    
    try: 
        temps = dict()
        for ii,ww in zip(ips,['A','B']):
            cc =  f'snmpwalk -v2c -c public {ii} .1.3.6.1.4.1.96.100.7.1.3.1'
            print('--> TEMPCTRL --> EXEC:',  cc)
            resp = subprocess.check_output(cc, shell=True).decode('utf-8')
            temps[f'TEMP_WWRS{ww}'] = int(resp.rsplit(' ')[-1])
        
        return temps

    except Exception as ee:
        print('--> TEMPCTRL --> ERROR:', ee)
        return None

 
def read_temp_fpga(duno):
    try: 
        cc = f'../clb-client-v1.4.2-7f0365b9/bin/cmdr {uu.getbaseip(duno)} var.get sys.fpga_temp'
        print('--> TEMPFPGA --> EXEC:', cc)
        resp = subprocess.check_output(cc, shell=True).decode('utf-8')
        return {'TEMP_FPGA': int(resp.rsplit(' ')[-2][1:],16)/100.0}
        
    except Exception as ee:
        print('--> TEMPFPGA --> ERROR:', ee)
        return None
