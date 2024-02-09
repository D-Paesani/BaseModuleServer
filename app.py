
from flask import Flask, Response, request, render_template, abort
from flask_debugtoolbar import DebugToolbarExtension
import jsc
import utils as uu
import pandas as pd
import time
import sys

def gettemplate(templ, msg=None):
    if msg != None: templ['msg'] = msg
    return render_template(templ['name'], **templ)

app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = 'pyrosoma'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['DEBUG_TB_PROFILER_ENABLED'] = True
app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True

toolbar = DebugToolbarExtension(app)

if __name__ == '__main__':
    #    app.run(host='0.0.0.0',port=5001)
    app.run()
    
@app.route('/help', methods = ['GET'])
@app.route('/', methods = ['GET'])
def f_help(): 
    return render_template('help.html')

@app.route('/cmdlog')
def f_showcmdlog():
    def generate():
        with open(jsc.cmdlogfile) as f:
            while True:
                yield f.read()
                # time.sleep(1)
    return app.response_class(generate(), mimetype='text/plain')

@app.route('/dumpsensor/<duid>', methods = ['GET'])
def f_dumpsensor(duid):
    resp = {}
    try:
        resp = jsc.commands['sensors'].exec(int(duid))
    except:
        abort(404)
    return resp
    
@app.route('/sensors', methods = ['GET', 'POST'])
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
                resp = jsc.commands['sensors'].exec(ii)
                ddt.append(int(resp['du']))
                resp.pop("du")
                dd.append(pd.DataFrame(resp, columns=[ii for ii in resp], index=jsc.commands['sensors'].index))
            except:
                return gettemplate(templ, msg=F'Error reading DU {ii}') 
        templ['table'] = '\n\n\n'.join(['<br>' + '-'*50 + F'   DU{ddt[iii]:04d}   ' + '-'*50 + dd[iii].to_html(index=True) for iii in range(len(dd))])
        return gettemplate(templ, msg=F'Reading sensors on DU={du} with response:')    
       
    else:
        return gettemplate(templ, msg=F'Waiting for user input')
    
@app.route('/swcontrol', methods = ['GET', 'POST'])
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
        if request.form['submit'] == 'WRITE':
            try:
                state =  templ['prefillstate'] = int(request.form.get('state'))
            except:
                return gettemplate(templ, msg='Error retrieving STATE value')
            
        for ii in sws:
            try: 
                resp = jsc.commands['switch'].exec(du)
                resp.pop('du')
                resp['switch'] = ii
                dd = pd.concat([dd, pd.DataFrame(resp, index=[''])])
                templ['table'] = dd.to_html(index=False)
            except:
                return gettemplate(templ, msg=F'Error {("writing to" if state<2 else "reading").lower()} SW {ii} ')  
                         
        msg = F'{"Writing to" if state<2 else "Reading"} DU{du:04d} switch{"es" if len(sws) > 1 else ""} {sws} {F"to STATE={state}" if state<2 else ""} with response:'
        return gettemplate(templ, msg)
                    
    else:
        return gettemplate(templ, msg='Waiting for user input')


@app.route('/rescue', methods = ['GET', 'POST'])
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
            resp = jsc.commands['rescue'].exec(du)
            resp.pop('du')
            dd = pd.concat([dd, pd.DataFrame(resp, index=[''])])
            templ['table'] = dd.to_html(index=False)
        except:
            return gettemplate(templ, msg=F'Error {("writing" if state<2 else "reading").lower()}') 
                         
        msg = F'{"Writing" if state<2 else "Reading"} DU{du:04d} rescue enable {F"to STATE={state}" if state<2 else ""} with response:'
        return gettemplate(templ, msg)
                    
    else:
        return gettemplate(templ, msg='Waiting for user input')

 
 