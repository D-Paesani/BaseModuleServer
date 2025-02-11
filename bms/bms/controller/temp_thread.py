from flask import current_app
from bms.web_manager import db
from .dbmanager import Temperature
from . import tempcontrol
from time import sleep
import concurrent.futures
import bms.controller.bms_utils as uu


import threading
TEMP_THREAD = None
TEMP_THREAD_STOP = threading.Event()
THREAD_START_TIMESTAMP = None


def thread_read_wwrs(du, wwrsa_ip, wwrsb_ip, app):
    with app.app_context():
        try:
            wets_temp = tempcontrol.read_temp_wwrs(du, [wwrsa_ip, wwrsb_ip])
            twa = Temperature(du=du, wwrsa_ip=wwrsa_ip, temperature=wets_temp['TEMP_WWRSA'])
            twb = Temperature(du=du, wwrsb_ip=wwrsb_ip, temperature=wets_temp['TEMP_WWRSB'])
            db.session.add_all([twa,twb])
            db.session.commit()
            return {'type' : {'wets_temp' : wets_temp}}
        except Exception as e:
            return {'error' : f'ERROR IN tempcontrol.read_temp_wwrs(du, [wwrsa_ip, wwrsb_ip]) {e}',
                    'type' : 'wets_temp'}

def thread_read_clb_fpga(du, clb_ip, app):
    with app.app_context():
        try:
            clb_temp = tempcontrol.read_temp_fpga(du)
            clb = Temperature(du=du, clb_ip=clb_ip, temperature=clb_temp['TEMP_FPGA'])
            db.session.add(clb)
            db.session.commit()
            return {'type' : {'clb_temp' : clb_temp}}
        except Exception as e:
            return {'error' : f'ERROR IN tempcontrol.read_temp_fpga(du) {e}',
                    'type' : 'clb_temp'}

def thread_read_du_t1_t2(du, app):
    with app.app_context():
        try:
            dul_temp, temp1, temp2 = tempcontrol.read_temp_dul_t1_t2(du)
            dul_temp_obj = Temperature(du=du, dul=True, temperature=dul_temp['TEMP_DUL'])
            temp1_obj = Temperature(du=du, temp1=True, temperature=temp1['TEMP_1'])
            temp2_obj = Temperature(du=du, temp2=True, temperature=temp2['TEMP_2'])
            db.session.add_all([dul_temp_obj,temp1_obj,temp2_obj])
            db.session.commit()
            return {'type' : {'dul_t1_t2' : {'dul_temp' : dul_temp,
                                             'temp1' : temp1,
                                             'temp2' : temp2}}}
        except Exception as e:
            return {'error' : f'ERROR IN tempcontrol.read_temp_dul_t1_t2(du) {e}',
                    'type' : 'dul_t1_t2'}

def read_temperatures(du, wwrsa_ip, wwrsb_ip, app):
    #print('thread ', du, wwrsa_ip, wwrsb_ip)
    clb_ip = uu.getbaseip(du)
    if not wwrsa_ip and not wwrsb_ip:
        wwrsa_ip, wwrsb_ip = uu.getwwrsips(du)
    with app.app_context():
        while not TEMP_THREAD_STOP.is_set():
            wets_temp = {}
            clb_temp = {}
            dul_temp ={}
            temp1 = {}
            temp2 = {}

            if app.config['USEDUMMY'] == False: #Production
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = []
                    futures.append(executor.submit(thread_read_wwrs, du, wwrsa_ip, wwrsb_ip, app))
                    futures.append(executor.submit(thread_read_clb_fpga, du, clb_ip, app))
                    futures.append(executor.submit(thread_read_du_t1_t2, du, app))
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        if 'error' in result:
                            print(f"Error in {result['type']}: {result['error']}")
                        elif 'wets_temp' in result['type']:
                            wets_temp = result['type']['wets_temp']
                        elif 'clb_temp' in result['type']:
                            clb_temp = result['type']['clb_temp']
                        elif 'dul_t1_t2' in result['type']:
                            dul_temp = result['type']['dul_t1_t2']['dul_temp']
                            temp1 = result['type']['dul_t1_t2']['temp1']
                            temp2 = result['type']['dul_t1_t2']['temp2']

                print(wets_temp, clb_temp, dul_temp, temp1, temp2)
            else: #Test
                try:
                    wets_temp['TEMP_WWRSA']=45
                    wets_temp['TEMP_WWRSB']=40
                    clb_temp['TEMP_FPGA']=35
                    dul_temp['TEMP_DUL']=33
                    temp1['TEMP_1']=24
                    temp2['TEMP_2']=26
                    twa = Temperature(du=du, wwrsa_ip=wwrsa_ip, temperature=wets_temp['TEMP_WWRSA'])
                    twb = Temperature(du=du, wwrsb_ip=wwrsb_ip, temperature=wets_temp['TEMP_WWRSB'])
                    clb = Temperature(du=du, clb_ip=clb_ip, temperature=clb_temp['TEMP_FPGA'])
                    dul_temp_obj = Temperature(du=du, dul=True, temperature=dul_temp['TEMP_DUL'])
                    temp1_obj = Temperature(du=du, temp1=True, temperature=temp1['TEMP_1'])
                    temp2_obj = Temperature(du=du, temp2=True, temperature=temp2['TEMP_2'])
                    db.session.add_all([twa,twb,clb,dul_temp_obj,temp1_obj,temp2_obj])
                    db.session.commit()
                except Exception as e:
                    print(f'#TEST {e}')
            
            #check for the temp alert
            if current_app.config['TEMP_ALARM'] > 1:
                trigger = False
                try:
                    if wets_temp['TEMP_WWRSA'] > current_app.config['TEMP_ALARM']:
                        trigger = trigger or True
                except Exception as e:
                    print(f'Error in temp wwrsa {e}')
                    
                try:
                    if wets_temp['TEMP_WWRSB'] > current_app.config['TEMP_ALARM']:
                        trigger = trigger or True
                except Exception as e:
                    print(f'Error in temp wwrsb {e}')
                
                try:
                    if clb_temp['TEMP_FPGA'] > current_app.config['TEMP_ALARM']:
                        trigger = trigger or True
                except Exception as e:
                    print(f'Error in temp clb fpga {e}')
                
                try:
                    if dul_temp['TEMP_DUL'] > current_app.config['TEMP_ALARM']:
                        trigger = trigger or True
                except Exception as e:
                    print(f'Error in temp dul {e}')
                
                try:
                    if temp1['TEMP_1'] > current_app.config['TEMP_ALARM']:
                        trigger = trigger or True
                except Exception as e:
                    print(f'Error in temp temp_1 {e}')
                
                try:
                    if temp2['TEMP_2'] > current_app.config['TEMP_ALARM']:
                        trigger = trigger or True
                except Exception as e:
                    print(f'Error in temp temp_2 {e}')
                    
                current_app.config.update({'TEMP_MONITORING_ALARM' : trigger}) #temp over limit

                if current_app.config['TEMP_MONITORING_ALARM']:
                    current_app.config.update({'TEMP_OVER_LIMIT' : {
                        'WWRSA' : wets_temp['TEMP_WWRSA'],
                        'WWRSB' : wets_temp['TEMP_WWRSB'],
                        'CLB_FPGA' : clb_temp['TEMP_FPGA'],
                        'DUL' : dul_temp['TEMP_DUL'],
                        'TEMP1' : temp1['TEMP_1'],
                        'TEMP2' : temp2['TEMP_2'],
                        'LIMIT' : current_app.config['TEMP_ALARM']}
                        })
                else:
                    current_app.config.update({'TEMP_OVER_LIMIT' : False })

            #ciclo necessario per kill istantaneo    
            for _ in range(60):  #ogni quanto prendere le misurazioni
                if TEMP_THREAD_STOP.is_set():
                    break
                sleep(0.5)