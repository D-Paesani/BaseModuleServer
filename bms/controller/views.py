from flask import Flask, request, render_template, abort, Blueprint, abort, flash, redirect, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import bms.controller.jsc as jsc
import bms.controller.bms_utils  as uu
import pandas as pd
from collections import deque
from flask_login import login_required, current_user
from . import BASEDIR
from ..web_manager.decorators import admin_required
from .export_to_xlsx import *
from time import sleep
import datetime


#from flask_breadcrumbs import Breadcrumbs, register_breadcrumb

cmd_blueprint = Blueprint('cmd', __name__, template_folder="./templates")

def gettemplate(templ, msg=None):
    if msg != None: templ['msg'] = msg
    return render_template(templ['name'], **templ)

@cmd_blueprint.route('/help', methods = ['GET'])
@login_required
#@register_breadcrumb(app, '.home', 'Home')
def f_help(): 
    return render_template('help.html')

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
    templ = dict(name='sensors.html', prefilldu='0', table='') 
    dd, ddt = [], []
    duClipboardDict = {}
    
    if request.method == 'POST':
        
        try:
            du, templ['prefilldu'] = uu.parsestrlist(request.form.get('du'), typ=int)
        except:
            return gettemplate(templ, msg='Error retrieving DU list') 
        
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
                return gettemplate(templ, msg=F'Error reading DU {ii} {e}')
        print(duClipPower.to_dict())
        templ['table_clip_power'] = duClipPower.to_dict()
        templ['table_to_clip'] = duClipboardDict
        templ['table'] = {f'DU{ddt[i]:03d}': tab.to_html(classes='table table-striped', index=True) for i, tab in enumerate(dd)}

        return gettemplate(templ, msg=F'Reading sensors on DU={du} with response:')    
    else:
        return gettemplate(templ, msg=F'Waiting for user input')
     
@cmd_blueprint.route('/swcontrol', methods = ['GET', 'POST'])
@login_required
def f_swcontrol(): 
    templ = dict(name='swcontrol.html', table='', datajson='', prefilldu='0', prefillsws=1, prefillstate=1) 
    dd = pd.DataFrame()
    state = 2
    
    if request.method == 'POST':
        
        try:
            du = templ['prefilldu'] = int(request.form.get('du'))
        except:
            return jsonify({'msg' : 'Error retrieving DU',
                            'table' : ''})
            return gettemplate(templ, msg='Error retrieving DU') 
        try:
            sws, templ['prefillsws'] = uu.parsestrlist(request.form.get('sws'), typ=int)
        except:
            return jsonify({'msg' : 'Error retrieving SW', 'table' : ''})
            return gettemplate(templ, msg='Error retrieving SW')
        
        submit = request.form.get('submit')
        
        if submit == 'WRITE':

        # data = request.json
        # if data.get('submit') == 'WRITE':
            try:
                state =  templ['prefillstate'] = int(request.form.get('state'))
            except:
                return jsonify({'msg' : 'Error retrieving STATE value',
                            'table' : ''})
                return gettemplate(templ, msg='Error retrieving STATE value')
            
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
                return ({'msg' : F'Error {("writing to" if state<2 else "reading").lower()} SW {ii} ', 'table' : ''})
                return gettemplate(templ, msg=F'Error {("writing to" if state<2 else "reading").lower()} SW {ii} ')  
                         
        msg = F'{"Writing to" if state<2 else "Reading"} DU{du:03d} switch{"es" if len(sws) > 1 else ""} {sws} {F"to STATE={state}" if state<2 else ""} with response:'
        return jsonify ({'msg' : msg, 'table' : templ['table']})
        return gettemplate(templ, msg)
                    
    else:
         return gettemplate(templ, msg='Waiting for user input')

@cmd_blueprint.route('/rescue', methods = ['GET', 'POST'])
@login_required
def f_rescue(): 
    templ = dict(name='rescue.html', table='', datajson='', prefilldu='0', prefillstate=1) 
    dd = pd.DataFrame()
    state = 2
     
    if request.method == 'POST':
        
        try:
            du = templ['prefilldu'] = int(request.form.get('du'))
        except:
            return gettemplate(templ, msg='Error retrieving DU') 
            
        if request.form['submit'] == 'WRITE':
            try:
                state =  templ['prefillstate'] = int(request.form.get('state'))
            except:
                return gettemplate(templ, msg='Error retrieving STATE value')
            
        try: 
            resp = jsc.commands['rescue'].exec(du, args=dict(state=state))
            # resp.pop('du')
            dd = pd.concat([dd, pd.DataFrame(resp, index=[''])])
            dd = dd[jsc.commands['rescue'].params]
            templ['table'] = dd.to_html(index=False)
        except:
            return gettemplate(templ, msg=F'Error {("writing" if state<2 else "reading").lower()}') 
                               
        msg = F'{"Writing" if state<2 else "Reading"} DU{du:03d} rescue enable {F"to STATE={state}" if state<2 else ""} with response:'
        return gettemplate(templ, msg)
                    
    else:
        return gettemplate(templ, msg='Waiting for user input')
    
@cmd_blueprint.route('/sendraw', methods = ['GET', 'POST']) 
@login_required
def f_sendraw(): 
    templ = dict(name='sendraw.html', prefilldu='0', prefillcmd='VERSION', answ='') 
     
    if request.method == 'POST':
         
        submit =  request.form.get('submit')
        templ['answ'] = ''
        
        try:
            du = templ['prefilldu'] = int(request.form.get('du')) 
        except:
            return jsonify ({'msg' : 'Error retrieving DU', 'answ' : templ['answ']})
            return gettemplate(templ, msg='Error retrieving DU') 
            
        if submit == 'SEND':
           
            try:
                cmd =  templ['prefillcmd'] = request.form.get('cmd') # string per il comando
            except:
                return jsonify ({'msg' : 'Error retrieving CMD value', 'answ' : templ['answ']})
                return gettemplate(templ, msg='Error retrieving CMD value')
                
            try: 
                templ['answ'] = jsc.commands['raw'].exec(du, args=dict(cmdstr=cmd))['answ'].replace("\n",'<br>').replace('  ','&nbsp;&nbsp;&nbsp;&nbsp;') #answ contiene la risposta raw di jsend command da mostrare a schermo
            except:
                return jsonify ({'msg' : 'Error sending command', 'answ' : templ['answ']})
                return gettemplate(templ, msg=F'Error sending command') 
                                
            msg = F'Sending command [{cmd}] to DU{du:03d} with response:'
        
        elif submit == 'PING':
        
            pingd = uu.isDuAlive(du)
            msg = f'Pinging DU{du:03d} at [{uu.getbaseip(du)}] : {"ALIVE" if pingd else "UNREACHABLE"}'
        
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
    fnam = 'BMS_' + (F'DU{int(dus[0]):03d}_' if len(dus)==1 else  '') + datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S') 
    return jsonify({'file_data': data_base64, 'du' : fnam})

@cmd_blueprint.route('/peripherals', methods=['GET', 'POST'])
@login_required
def f_peripherals():
    templ = dict(name='peripherals.html', prefilldu='0', du='', peri_status=None)

    if request.method == 'GET':
        
        try:
            
            try:
                du = request.args['du']
            except:
                return gettemplate(templ, msg='Waiting for user input')
            
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
            to_send[thiscommand]['SW'] = {'sw_status' : int('ON' in sw_status)}
            to_send[thiscommand]['SW'].update({'sw_display' : F'AUTORESCUE is {sw_status}'}) 

        except Exception as ee:
            return gettemplate(templ, msg='Error retrieving status')
            return gettemplate(templ, msg=F'Error retrieving status: {ee}')
        
        templ['du'] = du
        templ['peri_status'] = to_send
        # return jsonify(templ) #@mirko per diagnostica
        return gettemplate(templ, msg='Requesting status')
        
    if request.method == 'POST':
        
        req = request.json
        du, periph2operate, status2write = int(req['du']), req['periph'], int(req['val'])

        if periph2operate in jsc.peripheral_dict_BPD:     
            for ii in jsc.peripheral_dict_BPD[periph2operate]: 
                try:
                    resp = jsc.commands['switch'].exec(du, args=dict(sw=ii, state=status2write))
                except Exception as ee:
                    return jsonify({'status' : f'Error in operating rescue enable: {ee}', 'response':False})
                    
        elif periph2operate == 'rescue':
            try:
                resp = jsc.commands['rescue'].exec(du, args=dict(state=status2write))
            except Exception as ee:
                return jsonify({'status' : f'Error in operating rescue enable: {ee}', 'response':False})
        else:
            pass # for future use

        return jsonify({'status' : 'status', 'response':True})





