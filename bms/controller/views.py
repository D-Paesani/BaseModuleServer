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
        resp = jsc.commands['sensors'].exec(int(duid))
    except:
        abort(404)
    return resp
    
    
@cmd_blueprint.route('/sensors', methods = ['GET', 'POST'])
@login_required
def f_sensors(): 
    templ = dict(name='sensors.html', prefilldu='1', table='') 
    dd, ddt = [], []
    
    if request.method == 'POST':
        
        try:
            du, templ['prefilldu'] = uu.parsestrlist(request.form.get('du'), typ=int)
        except:
            return gettemplate(templ, msg='Error retrieving DU list') 
        
        for ii in du:
            try: 
                resp = jsc.commands['sensors'].exec(ii, args=None)
                ddt.append(int(resp['du']))
                # resp.pop('du')
                dd.append(pd.DataFrame(resp, columns=[ii for ii in jsc.commands['sensors'].params], index=jsc.commands['sensors'].index))

            except:
                return gettemplate(templ, msg=F'Error reading DU {ii}')
            
        templ['table_toex'] = dd
        templ['table'] = '\n\n\n'.join(['<br>' + '-'*50 + F'   DU{ddt[iii]:04d}   ' + '-'*50 + dd[iii].to_html(index=True) for iii in range(len(dd))])
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
            return gettemplate(templ, msg='Error retrieving DU') 
        try:
            sws, templ['prefillsws'] = uu.parsestrlist(request.form.get('sws'), typ=int)
        except:
            return gettemplate(templ, msg='Error retrieving SW')
        
        submit = request.form.get('submit')
        
        if submit == 'WRITE':

        # data = request.json
        # if data.get('submit') == 'WRITE':
            try:
                state =  templ['prefillstate'] = int(request.form.get('state'))
                
            except:
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
                templ['table'] = dd.to_html(index=False)
                
            except Exception as e:
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
    templ = dict(name='sendraw.html', prefilldu='', prefillcmd='', answ='') 
     
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
                templ['answ'] = jsc.commands['raw'].exec(du, args=dict(cmdstr=cmd))['answ'] #answ contiene la risposta raw di jsend command da mostrare a schermo
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


@cmd_blueprint.route('/export_to_xlsx', methods=['POST'])   # @mirko, non mi sembra funzioni con più DU. Se facessimo un foglio per ogni DU di cui si fa il dump?
@login_required
def generate_xlsx():
    import itertools, base64
    

    table = request.json.get('table').replace('[', '').replace(']', '')
    du = request.json.get('du').split('[')[1]
    du = du.split(']')[0].split(',')
    n_du = [x.replace(' ', '') for x in du] 
    du = 'DU'

    wb = Workbook()

    tables = table.split(',')
    for j, table in enumerate(tables):
        table = table.split()

        t1 = table[7][:6]
        t2 = table[7][6:]
        table[7] = t1
        table.insert(8, t2)

        t1 = table[16][:5]
        t2 = table[16][5:]
        table[16] = t1
        table.insert(17, t2)

        t1 = table[25][:4]
        t2 = table[25][4:]
        table[25] = t1
        table.insert(26, t2)
        
        rows = []

        t = []
        for r in itertools.islice(table, 8):
            t.append(r)
        rows.append(t)

        t = []
        for r in itertools.islice(table, 8, 17):
            t.append(r)
        rows.append(t)

        t = []
        for r in itertools.islice(table, 17, 26):
            t.append(r)
        rows.append(t)

        t = []
        for r in itertools.islice(table, 26, 35):
            t.append(r)
        rows.append(t)

        ws = wb.create_sheet(title=f'DU{n_du[j]}')

        for col in ('A','B','C','D','E','F','G','H','I'):
            ws.column_dimensions[col].width = 22
        for row in (1,2,3,4):
            ws.row_dimensions[row].height = 25
        
        ws.append([])
        for row,data in enumerate(rows):
            row += 1
            for i,cell_value in enumerate(data):
                i += 1
                if row == 1:
                    ws.cell(row=row, column=i+1).alignment = alin_centr
                    ws.cell(row=row, column=i+1, value=cell_value).font = txt_pry
                else:
                    ws.cell(row=row, column=i).alignment = alin_centr
                    ws.cell(row=row, column=i, value=cell_value).font = txt_cont
                if i == 1:
                    ws.cell(row=row, column=i).font = txt_pry
                
        
        #ws.cell(row=row+5, column=1, value=du).font = txt_data
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