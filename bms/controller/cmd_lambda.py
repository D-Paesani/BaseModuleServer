import subprocess, re
from flask import jsonify, Blueprint
from flask_login import login_required

tdk_blueprint = Blueprint('tdk', __name__)


def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def to_json(text):
    match = re.search(r"([\d.]+)", text)
    if match:
        key = text[:match.start()].strip()  # Prende il testo prima del numero
        value = float(match.group()) if '.' in match.group() else int(match.group())  # Determina se è un float o int
        return key, value
    return None, None


@tdk_blueprint.route('/lambda_status')
@login_required
def lambda_status():
    command = ['/app/bms/tdk_lambda.py', 'status']
    print(command)
    output = subprocess.check_output(command, universal_newlines=True).split('=>')[1].strip()
    print(output) #OFF | #ON
    return jsonify ({'response' : 'ok'})

@tdk_blueprint.route('/lambda_on')
@login_required
def lambda_on():
    command = ['/app/bms/tdk_lambda.py', 'power_on']
    print(command)
    output = subprocess.check_output(command, universal_newlines=True).split('=>')[1].strip()
    print(output) #OK
    return jsonify ({'response' : 'ok'})

@tdk_blueprint.route('/lambda_off')
@login_required
def lambda_off():
    command = ['/app/bms/tdk_lambda.py', 'power_off']
    print(command)
    output = subprocess.check_output(command, universal_newlines=True).split('=>')[1].strip()
    print(output) #OK
    return jsonify ({'response' : output})

@tdk_blueprint.route('/lambda_dvc')
@login_required
def lambda_dvc():
    command = ['/app/bms/tdk_lambda.py', 'dvc']
    print(command)
    output = subprocess.check_output(command, universal_newlines=True).strip()
    output = remove_ansi_escape_sequences(output).split('\n')
    print(output)
    #output dummy
    output= ["Measured Voltage 363.12              ",
    "Programmed Voltage 363.04              ",
    "Measured Current 0.0000              ",
    "Programmed Current 2.7004              ",
    "Over Voltage Set point 393              ",
    "Under Voltage Set point 310",
    ""]
    result = {}
    for text in output:
        key, value = to_json(text)
        if key:
            result[key] = value
    return jsonify ({'response' : result})