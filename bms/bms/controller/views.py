from flask import Flask, request, render_template, abort, Blueprint, abort, flash, redirect, url_for, jsonify, current_app, make_response
from flask_debugtoolbar import DebugToolbarExtension
import bms.controller.jsc as jsc
import bms.controller.bms_utils  as uu
import pandas as pd
from collections import deque
from flask_login import login_required, current_user
from . import BASEDIR
from bms.web_manager.decorators import admin_required
from .export_to_xlsx import *
from time import sleep
import datetime
from . import tempcontrol
from .dbmanager import Temperature
from bms.web_manager import db
from datetime import datetime
import concurrent.futures
from bms.controller import cmd_lambda
from bms.web_manager.commands_help import *
from . import BASEDIR
from bms.logger.logger import Logger


logger = Logger("views", log_file=f"{BASEDIR}/loggers/views.log")

#from flask_breadcrumbs import Breadcrumbs, register_breadcrumb

cmd_blueprint = Blueprint('cmd', __name__, template_folder="./templates")

def gettemplate(templ, msg=None):
    if msg != None: templ['msg'] = msg
    return render_template(templ['name'], **templ)

@cmd_blueprint.route('/help', methods = ['GET'])
@login_required
#@register_breadcrumb(app, '.home', 'Home')
def f_help(): 
    return render_template('help.html', runas=current_app.config['USEDUMMY'])

def read_log_file(nlines=2000):
    with open(f'{BASEDIR}/logs/jsccmd.log', 'r') as log:
        return deque(log, nlines)

@cmd_blueprint.route('/cmdlog')
@login_required
@admin_required
def render_log():
    #if current_user.can(Permission.ADMIN):
    lines = read_log_file()
    lines.reverse()
    return render_template('cmdlog.html', logs=lines)
    #else:
    #    abort(403)

# def f_showcmdlog():
#     def generate():
#         with open(jsc.cmdlogfile) as f:
#             while True:
#                 yield f.read()
#                 # time.sleep(1)
#     return app.response_class(generate(), mimetype='text/plain')



@cmd_blueprint.route('/dumpsensor/<duid>', methods = ['GET'])
@login_required
def f_dumpsensor(duid):
    resp = {}
    try:
        for icmd in ['sensors_avg', 'sensors_max']: resp.update(jsc.commands[icmd].exec(duid, args=None))
        resp.pop('answ')
    except:
        abort(404)
    return resp
    
@cmd_blueprint.route('/sensors', methods = ['GET', 'POST'])
@login_required
def f_sensors(): 
    templ = dict(name='sensors.html', prefilldu=current_app.config['DU'], table='') 
    templ['SENSOR'] = current_app.config['SENSOR']
    dd, ddt = [], []
    duClipboardDict = {}
    
    if request.method == 'POST':
        isDash = request.form.get('isDash')
        
        try:
            du, templ['prefilldu'] = uu.parsestrlist(request.form.get('du'), typ=int)
            if len(du) == 1:
                current_app.config.update({'DU' : du[0]})
        except Exception as e:
            msg='Error retrieving DU list'
            logger.error(f"Sensors: Error {msg} - {e}", exc_info=True)
            return gettemplate(templ, msg=msg) 
        
        for ii in du:
            try: 
                #ricordiamoci aggiungere backup di come era fatto (meglio) prima
                resp = {}
                ddtemp_list = []
                for readtype in ['avg', 'max', 'val']:
                    ccmd = 'sensors_'+readtype
                    ddtemp = pd.DataFrame(jsc.commands[ccmd].exec(ii, args=None), columns=jsc.commands[ccmd].params, index=jsc.commands[ccmd].index)
                    ddtemp.columns = [jjj.rsplit('_',1)[0] for jjj in ddtemp.columns]
                    ddtemp = ddtemp.transpose()
                    ddtemp.columns = [jjj + '_' + readtype for jjj in ddtemp.columns]
                    ddtemp_list.append(ddtemp)

                for icmd in ['sensors_avg', 'sensors_max', 'sensors_val']: resp.update(jsc.commands[icmd].exec(ii, args=None))
                ddt.append(int(resp['du']))
                
                ddtemp_pivot = ddtemp_list[0].join(ddtemp_list[1].join(ddtemp_list[2]))

                ###
                duClipPower = ddtemp_pivot.copy()
                duClipPower = duClipPower[['ADC_val', 'ADC_max', 'ADC_avg', 'VALUE_avg']]
                duClipPower.rename(columns={'ADC_val':'0ADC_val','ADC_max':'1ADC_max','ADC_avg':'2ADC_avg','VALUE_avg':'3VALUE_avg'}, inplace=True)
                rename_rows_clip_power = {
                                    'DUL_BOARDTEMP': 'aDUL_BOARDTEMP',
                                    'TEMP2': 'bTEMP2',
                                    'TEMP1': 'cTEMP1',
                                    'VEOC_RTN_I': 'dVEOC_RTN_I',
                                    'VEOC_FWR_I': 'eVEOC_FWR_I',
                                    'HYDRO_I': 'fHYDRO_I',
                                    'INPUT_V': 'gINPUT_V',
                                    'LBL_I': 'hLBL_I',
                                    'GLRA_I': 'iGLRA_I',
                                    'GLRB_I': 'lGLRB_I',
                                    'PWB_I': 'm1PWB_I'
                                }
                duClipPower.rename(index=rename_rows_clip_power, inplace=True)
                ###

                ddtemp_pivot = ddtemp_pivot[['ADC_avg', 'VALUE_avg', 'ADC_max', 'VALUE_max', 'ADC_val', 'VALUE_val', 'UNIT_avg']]
                duClipboard = ddtemp_pivot.copy()
                ddtemp_pivot.rename(columns={'UNIT_avg': 'UNIT'}, inplace=True)

                duClipboard.rename(columns={'ADC_avg':'0ADC_avg', 'VALUE_avg':'1VALUE_avg', 'ADC_max':'2ADC_max', 'VALUE_max':'3VALUE_max', 'ADC_val':'4ADC_val', 'VALUE_val':'5VALUE_val', 'UNIT_avg': '6UNIT'}, inplace=True)
                duClipboardDict[F'{ii:03d}'] = duClipboard.to_dict()

                columns = pd.MultiIndex.from_tuples([
                                                        ('AVERAGE', 'ADC'), ('AVERAGE', 'VALUE'),
                                                        ('MAX', 'ADC'), ('MAX', 'VALUE'),
                                                        ('VALUE', 'ADC'), ('VALUE', 'VALUE'),
                                                        ('', 'UNIT')
                                                    ])
                ddtemp_pivot.columns = columns                                         
                
                dd.append(ddtemp_pivot)
            except Exception as e:
                msg=F'Error reading DU {ii}'
                logger.error(f"Sensors: Error {msg} - {e}", exc_info=True)
                return gettemplate(templ, msg=msg)
        #print(duClipPower.to_dict())
        templ['table_clip_power'] = duClipPower.to_dict()
        templ['table_to_clip'] = duClipboardDict
        templ['table'] = {f'DU{ddt[i]:03d}': tab.to_html(classes='table table-striped', index=True) for i, tab in enumerate(dd)}

        if isDash:
            logger.info(f"Sensors on Dash: du={du} - {templ}")
            return jsonify ({'sensors' : {'table' : templ['table'],
                                          'table_clip_power' : templ['table_clip_power']}})
        logger.info(f"Sensors: du={du} - {templ}")
        return gettemplate(templ, msg=F'Reading sensors on DU={du} with response:')    
    else:
        return gettemplate(templ, msg=F'Waiting for user input')
     
@cmd_blueprint.route('/swcontrol', methods = ['GET', 'POST'])
@login_required
def f_swcontrol(): 
    templ = dict(name='swcontrol.html', table='', datajson='', prefilldu=current_app.config['DU'], prefillsws=1, prefillstate=1) 
    dd = pd.DataFrame()
    state = 2
    
    if request.method == 'POST':
        
        try:
            du = templ['prefilldu'] = int(request.form.get('du'))
            current_app.config.update({'DU' : du})
        except Exception as e:
            logger.error(f"SWcontrol: Error retrieving DU - {e}", exc_info=True)
            return jsonify({'msg' : 'Error retrieving DU',
                            'table' : ''})
        try:
            sws, templ['prefillsws'] = uu.parsestrlist(request.form.get('sws'), typ=int)
        except Exception as e:
            logger.error(f"SWcontrol: Error retrieving SW du={du} - {e}", exc_info=True)
            return jsonify({'msg' : 'Error retrieving SW', 'table' : ''})
        
        submit = request.form.get('submit')
        
        if submit == 'WRITE':

        # data = request.json
        # if data.get('submit') == 'WRITE':
            try:
                state =  templ['prefillstate'] = int(request.form.get('state'))
            except Exception as e:
                logger.error(f"SWcontrol: Error retrieving STATE value du={du} - {e}", exc_info=True)
                return jsonify({'msg' : 'Error retrieving STATE value',
                            'table' : ''})
            
        for ii in sws:
            try: 
                resp = jsc.commands['switch'].exec(du, args=dict(sw=ii, state=state))
                # resp.pop('du')
                resp['switch'] = ii
                dd = pd.concat([dd, pd.DataFrame(resp, index=[''])])
                mapping = {'OPEN': 'OPEN (OFF)', 'CLOSED': 'CLOSED (ON)'}
                dd['SWITCHSTATE'] = dd['SWITCHSTATE'].replace(mapping)
                
                #dd['SWITCHSTATE_4DUMMIES'] = dd['SWITCHSTATE']
                #for torep, repl in zip(['OPEN', 'CLOSED'], ['OPEN (OFF)', 'CLOSED (ON)']): dd['SWITCHSTATE'].replace(torep, repl, inplace=True)
                dd = dd[jsc.commands['switch'].params]
                print(dd)
                templ['table'] = dd.to_html(index=False)
                
            except Exception as e:
                msg = F'Error {("writing to" if state<2 else "reading").lower()} SW {ii} '
                logger.error(f"SWcontrol: Error du={du} - {msg} - {e}", exc_info=True)
                return ({'msg' : msg, 'table' : ''})
                         
        msg = F'{"Writing to" if state<2 else "Reading"} DU{du:03d} switch{"es" if len(sws) > 1 else ""} {sws} {F"to STATE={state}" if state<2 else ""} with response:'
        logger.info(f"SWcontrol: du={du} - {msg} - {templ}")
        return jsonify ({'msg' : msg, 'table' : templ['table']})
                    
    else:
         return gettemplate(templ, msg='Waiting for user input')

@cmd_blueprint.route('/rescue', methods = ['GET', 'POST'])
@login_required
def f_rescue(): 
    templ = dict(name='rescue.html', table='', datajson='', prefilldu=current_app.config['DU'], prefillstate=1) 
    dd = pd.DataFrame()
    state = 2
     
    if request.method == 'POST':
        
        try:
            du = templ['prefilldu'] = int(request.form.get('du'))
            current_app.config.update({'DU' : du})
        except Exception as e:
            logger.error(f'Rescue: Error retrieving DU - {e}', exc_info=True)
            return gettemplate(templ, msg='Error retrieving DU') 
            
        if request.form['submit'] == 'WRITE':
            try:
                state =  templ['prefillstate'] = int(request.form.get('state'))
            except Exception as e:
                logger.error(f'Rescue: Error retrieving STATE value du={du} - {e}', exc_info=True)
                return gettemplate(templ, msg='Error retrieving STATE value')
            
        try: 
            resp = jsc.commands['rescue'].exec(du, args=dict(state=state))
            # resp.pop('du')
            dd = pd.concat([dd, pd.DataFrame(resp, index=[''])])
            dd = dd[jsc.commands['rescue'].params]
            templ['table'] = dd.to_html(index=False)
        except Exception as e:
            msg=F'Error {("writing" if state<2 else "reading").lower()}'
            logger.error(f"Rescue: Error du={du} - {msg} - {e}", exc_info=True)
            return gettemplate(templ, msg=msg) 
                               
        msg = F'{"Writing" if state<2 else "Reading"} DU{du:03d} rescue enable {F"to STATE={state}" if state<2 else ""} with response:'
        logger.info(f"Rescue: {msg} - {templ}")
        return gettemplate(templ, msg)
                    
    else:
        return gettemplate(templ, msg='Waiting for user input')

@cmd_blueprint.route('/utilities', methods = ['GET', 'POST'])
@login_required
def f_threshold():
    templ = dict(name='utilities.html', prefilldu=current_app.config['DU'], answ='', prefillsw='5', prefillreset='24', 
        help_reset_maxvalues=help_reset_maxvalues,
        help_alarm_threshold_set=help_alarm_threshold_set,
        help_alarm_threshold_get=help_alarm_threshold_get)
        
    if request.method == 'POST': 
        submit =  request.form.get('submit')
        templ['answ'] = ''
        try:
            du = templ['prefilldu'] = int(request.form.get('du')) 
            current_app.config.update({'DU' : du})
        except Exception as e:
            logger.error(f"Utilities: Error retrieving DU {e}")
            return jsonify ({'msg' : 'Error retrieving DU', 'answ' : templ['answ']})
        
        if submit == 'GET':
            try:
                sw =  templ['prefillsw'] = request.form.get('sw') # string per il comando
            except Exception as e:
                logger.error(f"Utilities: Error retrieving SW value du={du} - {e}")
                return jsonify ({'msg' : 'Error retrieving SW value', 'answ' : templ['answ']})
                
            try: 
                templ['answ'] = jsc.commands['get_threshold'].exec(du, args=dict(sw=sw))['answ'].replace("\n",'<br>').replace('  ','&nbsp;&nbsp;&nbsp;&nbsp;') #answ contiene la risposta raw di jsend command da mostrare a schermo
            except Exception as e:
                logger.error(f"Utilities: Error sending command get_threshold du={du} - {e}")
                return jsonify ({'msg' : 'Error sending command', 'answ' : f"{e} - {templ['answ']}"})
                                
            msg = F'Sending command {jsc.commands["get_threshold"].cmd} {sw} to DU{du:03d} with response:'
        
        elif submit == 'SET':
            try:
                sw =  templ['prefillsw'] = request.form.get('sw') # string per il comando
                threshold = templ['prefillsw'] = request.form.get('threshold')
            except Exception as e:
                logger.error(f"Utilities: Error retrieving SW/Threshold value du={du} - {e}")
                return jsonify ({'msg' : 'Error retrieving SW/Threshold value', 'answ' : templ['answ']})
            try: 
                templ['answ'] = jsc.commands['set_threshold'].exec(du, args=dict(sw=sw, value=threshold))['answ'].replace("\n",'<br>').replace('  ','&nbsp;&nbsp;&nbsp;&nbsp;') #answ contiene la risposta raw di jsend command da mostrare a schermo
            except Exception as e:
                logger.error(f"Utilities: Error sending command set_threshold du={du} - {e}")
                return jsonify ({'msg' : 'Error sending command', 'answ' : f"{e} - {templ['answ']}"})
                                
            msg = F'Sending command {jsc.commands["set_threshold"].cmd} {sw} {threshold} to DU{du:03d} with response:'
        
        elif submit == 'RESET':
            try:
                reset_maxvalue =  templ['prefillreset'] = request.form.get('reset_maxvalue') # string per il comando
            except Exception as e:
                logger.error(f"Utilities: Error retrieving reset value du={du} - {e}")
                return jsonify ({'msg' : 'Error retrieving reset value', 'answ' : templ['answ']})
            try: 
                templ['answ'] = jsc.commands['reset_maxvalue'].exec(du, args=dict(value=reset_maxvalue))['answ'].replace("\n",'<br>').replace('  ','&nbsp;&nbsp;&nbsp;&nbsp;') #answ contiene la risposta raw di jsend command da mostrare a schermo
            except Exception as e:
                logger.error(f"Utilities: Error sending command reset_maxvalue du={du} - {e}")
                return jsonify ({'msg' : 'Error sending command', 'answ' : f"{e} - {templ['answ']}"})
                                
            msg = F'Sending command {jsc.commands["reset_maxvalue"].cmd} {reset_maxvalue} to DU{du:03d} with response:'
        logger.info(f"Utilities: {msg} - {templ}")
        return jsonify ({'msg' : msg, 'answ' : templ['answ']})
                
    else:
        return gettemplate(templ, msg='Waiting for user input')

    

@cmd_blueprint.route('/sendraw', methods = ['GET', 'POST']) 
@login_required
def f_sendraw(): 
    templ = dict(name='sendraw.html', prefilldu=current_app.config['DU'], prefillcmd='VERSION', answ='') 
     
    if request.method == 'POST':
         
        submit =  request.form.get('submit')
        templ['answ'] = ''
        
        try:
            du = templ['prefilldu'] = int(request.form.get('du')) 
            current_app.config.update({'DU' : du})
        except Exception as e:
            logger.error(f"Sendraw: Error retrieving DU {e}", exc_info=True)
            return jsonify ({'msg' : 'Error retrieving DU', 'answ' : templ['answ']})
            
        if submit == 'SEND':
           
            try:
                cmd =  templ['prefillcmd'] = request.form.get('cmd') # string per il comando
            except Exception as e:
                logger.error(f"Sendraw: Error retrieving CMD value du={du} - {e}", exc_info=True)
                return jsonify ({'msg' : 'Error retrieving CMD value', 'answ' : templ['answ']})
                
            try: 
                templ['answ'] = jsc.commands['raw'].exec(du, args=dict(cmdstr=cmd))['answ'].replace("\n",'<br>').replace('  ','&nbsp;&nbsp;&nbsp;&nbsp;') #answ contiene la risposta raw di jsend command da mostrare a schermo
            except Exception as e:
                logger.error(f"Sendraw: Error sending command du={du} - {e}", exc_info=True)
                return jsonify ({'msg' : 'Error sending command', 'answ' : templ['answ']})
                                
            msg = F'Sending command [{cmd}] to DU{du:03d} with response:'
        
        elif submit == 'PING':
        
            pingd = uu.isDuAlive(du)
            msg = f'Pinging DU{du:03d} at [{uu.getbaseip(du)}] : {"ALIVE" if pingd else "UNREACHABLE"}'
        logger.info(f"Sendraw: {msg} - {templ}")
        return jsonify ({'msg' : msg, 'answ' : templ['answ']})
                
    else:
        return gettemplate(templ, msg='Waiting for user input')

@cmd_blueprint.route('/export_to_xlsx', methods=['POST'])   # @mirko, dobbiamo rifarla per tabelle di lunghezza variabile, magari usiamo pandas + lista globale di dfs...
@login_required
def generate_xlsx():
    import base64
    cols = {1:'A',2:'B',3:'C',4:'D',5:'E',6:'F',7:'G',8:'H',9:'I'}
    table = request.json.get('table')

    wb = Workbook()

    dus=[]
    for duname, content in table.items():
        j = 2
        ws = wb.create_sheet(title=f'DU{duname}')
        for colname, param_content in content.items():
            ws.column_dimensions[cols[j]].width = 18
            ws.cell(row=1, column=j, value=colname[1:]).font = txt_pry #nomi colonne
            ws.cell(row=1, column=j).alignment = align_centr
            i = 2
            for param_name, param_value in param_content.items():
                ws.row_dimensions[i].height = 25
                ws.cell(row=i, column=1, value=param_name).font = txt_pry #nomi valori righe

                ws.cell(row=i, column=j, value=param_value).font = txt_cont #valori
                ws.cell(row=i, column=j).alignment = align_centr
                i += 1
            j += 1
        
        ws.column_dimensions['A'].width = 34
        ws.row_dimensions[1].height = 30

    wb.remove(wb.active)

    filename = '/app/bms/controller/temp.xlsx'
    wb.save(filename=filename)
    with open(filename, 'rb') as f:
        data = f.read()
        data_base64 = base64.b64encode(data).decode('utf-8')
    remove(filename) 
    fnam = 'BMS_' + (F'DU{int(dus[0]):03d}_' if len(dus)==1 else  '') + datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S') 
    return jsonify({'file_data': data_base64, 'du' : fnam})

@cmd_blueprint.route('/peripherals', methods=['GET', 'POST'])
@login_required
def f_peripherals():
    templ = dict(name='peripherals.html', prefilldu=current_app.config['DU'], du='', peri_status=None)

    if request.method == 'GET':
        
        try:
            try:
                isDash = request.args['isDash']
            except:
                isDash = False
            
            try:
                du = request.args['du']
            except Exception as e:
                msg='Waiting for user input #error input#'
                logger.error(f"Peripherals: Error {msg}")
                return gettemplate(templ, msg=msg)
            
            to_send = {} 
                    
            #read SWS
            for periph, periphsws in jsc.peripheral_dict_BPD.items():
                operatedsws = {}
    
                for ii in periphsws:
                    resp = jsc.commands['switch'].exec(du, args=dict(sw=ii, state=2))
                    swname = F'SW_{ii}'
                    operatedsws[swname] = {}
                    # operatedsws[swname]['resp'] =       resp
                    sw_name =                           resp.get('SWITCHNUM').replace('SWITCH_','')
                    sw_status =                         resp.get('SWITCHSTATE').replace('OPEN','OFF').replace('CLOSED','ON')
                    operatedsws[swname]['sw_status']  = int('ON' in sw_status)
                    operatedsws[swname]['sw_display'] = F'{sw_name} is {sw_status}'
     
                to_send[periph] = operatedsws
                
            #read RESCUE
            thiscommand = 'rescue'
            resp = jsc.commands[thiscommand].exec(du, args=dict(state=2))
            to_send[thiscommand] = {}
            sw_status = resp.get('ENABLESTATE').replace('DISABLED','OFF').replace('ENABLED','ON')
            # to_send[thiscommand]['resp'] = resp           
            to_send[thiscommand]['SW'] = {'sw_status' : int('OFF' in sw_status)}
            to_send[thiscommand]['SW'].update({'sw_display' : F'AUTORESCUE is {sw_status}'}) 

        except Exception as e:
            logger.error(f"Peripherals: Error retrieving status du={du} - {e}", exc_info=True)
            return gettemplate(templ, msg='Error retrieving status')
        
        templ['du'] = du
        templ['prefilldu'] = du
        templ['peri_status'] = to_send

        if isDash:
            logger.info(f"Peripherals on Dash: {templ}")
            return jsonify ({'peripherals' : templ})
        logger.info(f"Peripherals: {templ}")
        return gettemplate(templ, msg='Requesting status')
        
    if request.method == 'POST':
        
        req = request.json
        du, periph2operate, status2write = int(req['du']), req['periph'], int(req['val'])

        if periph2operate in jsc.peripheral_dict_BPD:     
            for ii in jsc.peripheral_dict_BPD[periph2operate]: 
                try:
                    resp = jsc.commands['switch'].exec(du, args=dict(sw=ii, state=status2write))
                    logger.info(f"Peripherals: switch command on du={du} sw={ii} state={status2write}")
                except Exception as e:
                    logger.error(f"Peripherals: Error in operating rescue enable du={du} - {e}", exc_info=True)
                    return jsonify({'status' : f'Error in operating rescue enable: {e}', 'response':False})
                    
        elif periph2operate == 'rescue':
            try:
                resp = jsc.commands['rescue'].exec(du, args=dict(state=status2write))
                logger.info(f"Peripherals: rescue command on du={du} state={status2write}")
            except Exception as e:
                logger.error(f"Peripherals: Error in operating rescue enable du={du} - {e}", exc_info=True)
                return jsonify({'status' : f'Error in operating rescue enable: {e}', 'response':False})
        else:
            pass # for future use

        return jsonify({'status' : 'status', 'response':True})
    
@cmd_blueprint.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    templ = dict(name='dashboard.html', prefilldu=current_app.config['DU'], prefillsw='5', prefillreset='24', 
        help_reset_maxvalues=help_reset_maxvalues,
        help_alarm_threshold_set=help_alarm_threshold_set,
        help_alarm_threshold_get=help_alarm_threshold_get)

    templ['SENSOR'] = current_app.config['SENSOR']
    if request.method == 'POST':
        du = templ['prefilldu'] = request.get_json()['du']
        current_app.config.update({'DU' : du})
        return jsonify({'response':True})
    return gettemplate(templ)

@cmd_blueprint.route('/monitoring_status', methods=['GET'])
@login_required
def monitoring_status():
    sleep(1)   
    status = current_app.config['TEMP_MONITORING_ALARM']
    print('STATUS ',status, current_app.config['TEMP_ALARM'])
    if status:
        return jsonify({'status' : status,
                        'temps' : current_app.config['TEMP_OVER_LIMIT']})
    return jsonify({'status': status})

from .temp_thread import *
###

@cmd_blueprint.route('/unset_temp_alarm', methods=['POST'])
@login_required
def unset_temp_alarm():
    if current_app.config['TDK_LAMBDA']:
        current_app.config.update({'TEMP_ALARM' : 0})
        current_app.config.update({'TEMP_MONITORING_ALARM' : False})
    return jsonify ({'response' : 'Temperature Alarm is OFF'})

    
@cmd_blueprint.route('/set_temp_alarm', methods=['POST'])
@login_required
def set_temp_alarm():
    if current_app.config['TDK_LAMBDA']:
        data = request.get_json()
    try:
        value = int(data.get('value'))
        current_app.config.update({'TEMP_ALARM' : value})
        return jsonify ({'response' : f'Temperature Alarm is ON - {value}°'})
    except Exception as e:
        return jsonify ({'response' : f'Value Error => {e}'})


@cmd_blueprint.route('/temperatures', methods=['GET', 'POST'])
@login_required
def temperatures():
    global TEMP_THREAD, TEMP_THREAD_STOP, THREAD_START_TIMESTAMP
    templ = dict(name='temperatures.html', prefilldu=current_app.config['DU'], wwrsa=current_app.config['WWRSA'], wwrsb=current_app.config['WWRSB'], temp='')
    templ['temp'] = current_app.config['TEMP_ALARM']
    
    if request.method == 'POST':
        submit = request.form.get('submit')
        
        if submit == 'START':
            du = templ['prefilldu'] = request.form.get('du')
            current_app.config.update({'DU' : du})

            wwrsa = templ['wwrsa'] = request.form.get('wwrsa')            
            current_app.config.update({'WWRSA' : wwrsa})

            wwrsb = templ['wwrsb'] = request.form.get('wwrsb')
            current_app.config.update({'WWRSB' : wwrsb})

            templ['temp'] = current_app.config['TEMP_ALARM']

            if TEMP_THREAD is not None and TEMP_THREAD.is_alive():
                TEMP_THREAD_STOP.set()
                TEMP_THREAD.join()
            
            TEMP_THREAD_STOP.clear()
            TEMP_THREAD = threading.Thread(target=read_temperatures, args=(int(du), wwrsa, wwrsb, current_app._get_current_object()))
            TEMP_THREAD.start()
            THREAD_START_TIMESTAMP = datetime.utcnow()

            templ['msg'] = "Temperature monitor is ON"
            current_app.config.update({'TEMP_MONITORING_STATUS' : True})
            return gettemplate(templ)

    status = current_app.config['TEMP_MONITORING_STATUS']    
    templ['msg'] = "Temperature monitor is ON" if status else "Temperature monitor is OFF"      
    return gettemplate(templ)

@cmd_blueprint.route('/stop_reading', methods=['GET'])
@login_required
def stop_reading():
    global TEMP_THREAD, TEMP_THREAD_STOP, THREAD_START_TIMESTAMP
    if TEMP_THREAD is not None and TEMP_THREAD.is_alive():
        TEMP_THREAD_STOP.set()
        TEMP_THREAD.join()
        TEMP_THREAD = None

        THREAD_START_TIMESTAMP = None
    try:
        if current_app.config['TEMP_MONITORING_ALARM'] and current_app.config['TDK_LAMBDA']:
            jsc.commands['switch'].exec(0, args=dict(sw='2', state=0)) #SWITCH_CONTROL 2 0
            jsc.commands['switch'].exec(0, args=dict(sw='1', state=0)) #SWITCH_CONTROL 1 0
            sleep(1)
            # import subprocess
            # command = ['/app/bms/tdk_lambda.py', 'power_off']
            # subprocess.call(command)
            cmd_lambda.lambda_off()
    except Exception as e:
        print(f'ERROR IN STOP LAMBDA {e}')
    
    current_app.config.update({'TEMP_MONITORING_STATUS' : False})
    current_app.config.update({'TEMP_MONITORING_ALARM' : False})
    current_app.config.update({'TEMP_ALARM' : 0})

    return jsonify({"msg": "Temperature monitor is OFF"}), 200

@cmd_blueprint.route('/get-temps', methods=['GET'])
@login_required
def get_temperatures():
    global THREAD_START_TIMESTAMP

    try:
        temperatures = Temperature.query.filter(Temperature.timestamp > THREAD_START_TIMESTAMP).order_by(Temperature.timestamp.asc()).all()

        data = {'wwrsa_ip': [], 'wwrsb_ip': [], 'clb_ip': [], 'temp1': [], 'temp2': [], 'dul': []}

        for key in data.keys():
            key_data = [t for t in temperatures if getattr(t, key)]
            for t in key_data:
                data[key].append({
                    'timestamp': t.timestamp.isoformat(),
                    'temperature': round(t.temperature),
                })
    except Exception as e:
        print(f'ERROR IN API UPDATE => {e}')
    
    #print(data)
    return jsonify(data)
