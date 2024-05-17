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
from itertools import chain

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
    templ = dict(name='sensors.html', prefilldu='1', table='') 
    dd, ddt = [], []
    dudict = {}
    
    if request.method == 'POST':
        
        try:
            du, templ['prefilldu'] = uu.parsestrlist(request.form.get('du'), typ=int)
        except:
            return gettemplate(templ, msg='Error retrieving DU list') 
        
        for ii in du:
            try: 
                resp = {} 
                for icmd in ['sensors_avg', 'sensors_max']: resp.update(jsc.commands[icmd].exec(ii, args=None))
                ddt.append(int(resp['du']))
                # resp.pop('du')
                ddtemp = pd.DataFrame(resp, columns=[ii for ii in sum([jsc.commands[jj].params for jj in ['sensors_avg', 'sensors_max']],[])], index=jsc.commands['sensors_avg'].index)
                dd.append(ddtemp.transpose())
                dudict[F'{ii:03d}'] = ddtemp.to_dict()
            except:
                return gettemplate(templ, msg=F'Error reading DU {ii}')
        
        templ['table_toex'] = dudict
        spacer, nspacer = '-', 35
        templ['table'] = '\n\n\n'.join(['<br>' + spacer*nspacer + F'DU{ddt[iii]:04d}' + spacer*nspacer + dd[iii].to_html(index=True) for iii in range(len(dd))])

        return gettemplate(templ, msg=F'Reading sensors on DU={du} with response:')    
    else:
        return gettemplate(templ, msg=F'Waiting for user input')
    
@cmd_blueprint.route('/swcontrol', methods = ['GET', 'POST'])
@login_required
def f_swcontrol(): 
    templ = dict(name='swcontrol.html', table='', datajson='', prefilldu='1', prefillsws=1, prefillstate=1) 
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
            return jsonify({'msg' : 'Error retrieving SW',
                            'table' : ''})
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
                return ({'msg' : F'Error {("writing to" if state<2 else "reading").lower()} SW {ii} ',
                         'table' : ''})
                return gettemplate(templ, msg=F'Error {("writing to" if state<2 else "reading").lower()} SW {ii} ')  
                         
        msg = F'{"Writing to" if state<2 else "Reading"} DU{du:04d} switch{"es" if len(sws) > 1 else ""} {sws} {F"to STATE={state}" if state<2 else ""} with response:'
        return jsonify ({'msg' : msg,
                         'table' : templ['table']})
        return gettemplate(templ, msg)
                    
    else:
         return gettemplate(templ, msg='Waiting for user input')


@cmd_blueprint.route('/rescue', methods = ['GET', 'POST'])
@login_required
def f_rescue(): 
    templ = dict(name='rescue.html', table='', datajson='', prefilldu='1', prefillstate=1) 
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
                               
        msg = F'{"Writing" if state<2 else "Reading"} DU{du:04d} rescue enable {F"to STATE={state}" if state<2 else ""} with response:'
        return gettemplate(templ, msg)
                    
    else:
        return gettemplate(templ, msg='Waiting for user input')
    

# @mirko: 
# questo è per mandare i comandi raw tramite un bottone SEND
# poi se aggiungiamo questa pagina, ricordiamoci il link sulla pagina "help"
# qui ho messo anche un bottone PING per pingare la DU e avere il risultato a schermo
@cmd_blueprint.route('/sendraw', methods = ['GET', 'POST']) 
@login_required
def f_sendraw(): 
    templ = dict(name='sendraw.html', prefilldu='', prefillcmd='VERSION', answ='') 
     
    if request.method == 'POST':
         
        submit =  request.form.get('submit')
        templ['answ'] = ''
        
        try:
            du = templ['prefilldu'] = int(request.form.get('du'))  # qui la pagina html dice "insert target DU"
        except:
            return jsonify ({'msg' : 'Error retrieving DU',
                         'answ' : templ['answ']})
            return gettemplate(templ, msg='Error retrieving DU') 
            
        if submit == 'SEND':
           
            try:
                cmd =  templ['prefillcmd'] = request.form.get('cmd') # string per il comando
            except:
                return jsonify ({'msg' : 'Error retrieving CMD value',
                         'answ' : templ['answ']})
                return gettemplate(templ, msg='Error retrieving CMD value')
                
            try: 
                templ['answ'] = jsc.commands['raw'].exec(du, args=dict(cmdstr=cmd))['answ'].replace("\n",'<br>').replace('  ','&nbsp;&nbsp;&nbsp;&nbsp;') #answ contiene la risposta raw di jsend command da mostrare a schermo
            except:
                return jsonify ({'msg' : 'Error sending command',
                         'answ' : templ['answ']})
                return gettemplate(templ, msg=F'Error sending command') 
                                
            msg = F'Sending command [{cmd}] to DU{du:04d} with response:'
        
        
        elif submit == 'PING':
        
            pingd = uu.isDuAlive(du)
            msg = f'Pinging DU{du:04d} at [{uu.getbaseip(du)}] : {"ALIVE" if pingd else "UNREACHABLE"}'
        
        return jsonify ({'msg' : msg,
                         'answ' : templ['answ']})
                
    else:
        return gettemplate(templ, msg='Waiting for user input')


@cmd_blueprint.route('/export_to_xlsx', methods=['POST'])   # @mirko, dobbiamo rifarla per tabelle di lunghezza variabile, magari usiamo pandas + lista globale di dfs...
@login_required
def generate_xlsx():
    import base64
    
    table = request.json.get('table')
    wb = Workbook()

    for key, val in table.items():
        ws = wb.create_sheet(title=f'DU{key}')
        #pd.DataFrame(val).transpose().to_excel('test'+key+'.xlsx', sheet_name=f'DU{key}')
        df = pd.DataFrame(val).transpose()
    
        for r_idx, row in enumerate(df.itertuples(), 1):
            ws.row_dimensions[r_idx].height = 25
            for c_idx, value in enumerate(row, 1):
                if r_idx == 1 and c_idx < 4:
                    ws.cell(row=r_idx, column=c_idx+1, value=df.columns[c_idx-1]).font = txt_pry
                    ws.cell(row=r_idx, column=c_idx+1).alignment = alin_centr
                if c_idx == 1:
                    ws.cell(row=r_idx+1, column=c_idx, value=value).font = txt_pry
                else:
                    ws.cell(row=r_idx+1, column=c_idx, value=value).font = txt_cont
                ws.cell(row=r_idx+1, column=c_idx).alignment = alin_centr
        ws.column_dimensions['A'].width = 38

    wb.remove(wb.active)

    filename = '/app/bms/controller/temp.xlsx'
    wb.save(filename=filename)
    with open(filename, 'rb') as f:
        data = f.read()
        data_base64 = base64.b64encode(data).decode('utf-8')
    remove(filename)
    fnam = 'bmsexport_' +  datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
    return jsonify({'file_data': data_base64,
                    'du' : fnam})


@cmd_blueprint.route('/peripherals', methods=['GET', 'POST'])
@login_required
def f_peripherals():
    templ = dict(name='peripherals.html', prefilldu='', du='', answ='')
    try:
    #    request.args['submit']:
    #if request.method == 'GET':
        du = request.args['du']
        templ = dict(name='peripherals.html', prefilldu=du, du=du, answ='')

        to_send = {}
        
        for BPD in jsc.peripheral_dict_BPD.items():
            operatedsws = {}
            l_couple = []    
            for ii in BPD[1]:
                try: #gestione errori si può copiare da swcontrol
                    resp = jsc.commands['switch'].exec(du, args=dict(sw=ii, state=2))
                    operatedsws[F'SW_{ii}'] = resp      
                except:
                    pass
            for key in operatedsws.values():
                if key.get('SWITCHSTATE'):
                    if key.get('SWITCHSTATE') == 'CLOSED':
                        l_couple.append('1')
                    else:
                        l_couple.append('0')
            to_send[BPD[0]] = l_couple    
            to_send[BPD[0]].append('ON' if l_couple[0]=='1' and l_couple[1]=='1' else 'OFF')

        templ['du'] = to_send

        return gettemplate(templ, msg='Waiting for user input')
    except:
        pass
        
    if request.method == 'POST':
        periph = request.json
        du = periph['du']

        periph2operate = list(periph.keys())[0]#nome periferica

        status2write = int(periph[periph2operate][1])
        status2write = 0 if status2write == '1' else 1

        operatedsws = {}
        for ii in jsc.peripheral_dict_BPD[periph2operate]: 
            try: #gestione errori si può copiare da swcontrol
                resp = jsc.commands['switch'].exec(du, args=dict(sw=ii, state=status2write))
                operatedsws[F'SW_{ii}'] = resp      
            except:
                pass  

        status = 1 if operatedsws['SW_1']['SWITCHSTATE'] == 'CLOSED' and operatedsws['SW_2']['SWITCHSTATE'] == 'CLOSED' else 0
        print('status => ', status)
        return jsonify({'status' : status,
                        'response' : True})
    return gettemplate(templ, msg='Waiting for user input')

