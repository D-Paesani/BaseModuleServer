#!/usr/bin/python3
"""
A minimal utility to send structured commands to the BPS board using Java BPS network utility
"""

import sys
import os
import re
sys.path.insert(0, '../codegen')


import commands
from utils import mls
from analogvariables import *
from entities.descriptors import PayloadFieldEnum, PayloadFieldU8, PayloadFieldU16, PayloadFieldU32
from commutils import *
import os

ASK_CONFIRM = False
SHOW_SENT_DATA = True
SHOW_RECEIVED_DATA = False

CLB_IPADDR = sys.argv[1]
# check it resembles an ip address
if not re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$").match(CLB_IPADDR):
    print ("IPADDR format error or missing")
    sys.exit(0)
# remove it from current list of parameters (historical reasons)
sys.argv.pop(1)


JSCRIPTFMT = './execute.sh NG_BPDCmd {} [REQCODE] [RESPCODE] [RESPLEN] [REQPAYLOAD]'.format(CLB_IPADDR)

def ask_confirm():
    answer = ""
    while answer not in ["y", "n"]:
        answer = raw_input("Confirm [Y/N]? ").lower()
    return answer == "y"


def mydirtyexec(_cmd):
    # like it dirty...
    os.system(_cmd + ' > __tmp')
    return open('__tmp', 'r').read()




def getconvertedvals(command, fields):
    vals = list()

    # the pork way (with great respect for porks)
    if command.name == 'SENSOR_GET_SINGLE':
        vn = fields[0]
        converter = None

        if vn == 'MON_DUL_BOARDTEMP':
            converter = convert_chn2meas_DUL_BOARDTEMP
            units = 'C'
        elif vn == 'MON_TEMP2':
            converter = convert_chn2meas_TEMP2
            units = 'C'
        elif vn == 'MON_TEMP1':
            converter = convert_chn2meas_TEMP1
            units = 'C'
        elif vn == 'MON_VEOC_RTN_I':
            converter = convert_chn2meas_VEOC_RTN_I
            units = 'A'
        elif vn == 'MON_VEOC_FWR_I':
            converter = convert_chn2meas_VEOC_FWR_I
            units = 'A'
        elif vn == 'MON_HYDRO_I':
            converter = convert_chn2meas_HYDRO_I
            units = 'mA'
        elif vn == 'MON_INPUT_V':
            converter = convert_chn2meas_INPUT_V
            units = 'V'
        elif vn == 'MON_LBL_I':
            converter = convert_chn2meas_LBL_I
            units = 'mA'
        elif vn == 'MON_GLRA_I':
            converter = convert_chn2meas_GLRA_I
            units = 'A'
        elif vn == 'MON_GLRB_I':
            converter = convert_chn2meas_GLRB_I
            units = 'A'
        elif vn == 'MON_PWB_I':
            converter = convert_chn2meas_PWB_I
            units = 'A'
        elif vn == 'FLAG_DUL_ALARMPOS1':
            pass
        elif vn == 'FLAG_DUL_ALARMPOS2':
            pass
        elif vn == 'FLAG_DUL_ALARMNEG1':
            pass
        elif vn == 'FLAG_DUL_ALARMNEG2':
            pass
        elif vn == 'FLAG_HYDRO_PWR_FAULT':
            pass
        elif vn == 'FLAG_LBL_PWR_FAULT':
            pass
        elif vn == 'FLAG_GLRA_FAULT':
            pass
        elif vn == 'FLAG_GLRB_FAULT':
            pass
        elif vn == 'FLAG_POWERBOARD_FAULT':
            pass
        elif vn == 'FLAG_GLRA_GOOD':
            pass
        elif vn == 'FLAG_GLRB_GOOD':
            pass
        elif vn == 'FLAG_POWERBOARD_GOOD':
            pass
        else:
            pass

        if converter:
            vals.append(['',''])
            vals.append([converter(fields[1]), units]) # VALUE
            vals.append([converter(fields[2]), units]) # OFFSET
            vals.append([converter(fields[3]), units]) # MAXVALUE
            vals.append([converter(fields[4]), units]) # MEANVALUE
        else:
            # to be verified
            pass

    elif command.name in ['SENSOR_VALUES_GETALL', 'SENSOR_AVERAGE_GETALL', 'SENSOR_OFFSETS_GETALL', 'SENSOR_MAXVALUES_GETALL']:
        
        vals.append([convert_chn2meas_DUL_BOARDTEMP(fields[0]), 'C']) # FIELD  0  : MON_DUL_BOARDTEMP_MEAN
        vals.append([convert_chn2meas_TEMP2(fields[1]), 'C']) # FIELD  1  : MON_TEMP2_MEAN
        vals.append([convert_chn2meas_TEMP1(fields[2]), 'C']) # FIELD  2  : MON_TEMP1_MEAN
        vals.append([convert_chn2meas_VEOC_RTN_I(fields[3]), 'A']) # FIELD  3  : MON_VEOC_RTN_I_MEAN
        vals.append([convert_chn2meas_VEOC_FWR_I(fields[4]), 'A']) # FIELD  4  : MON_VEOC_FWR_I_MEAN
        vals.append([convert_chn2meas_HYDRO_I(fields[5]), 'mA']) # FIELD  5  : MON_HYDRO_I_MEAN
        vals.append([convert_chn2meas_INPUT_V(fields[6]), 'V']) # FIELD  6  : MON_INPUT_V_MEAN
        vals.append([convert_chn2meas_LBL_I(fields[7]), 'mA']) # FIELD  7  : MON_LBL_I_MEAN
        vals.append([convert_chn2meas_GLRA_I(fields[8]), 'A']) # FIELD  8  : MON_GLRA_I_MEAN
        vals.append([convert_chn2meas_GLRB_I(fields[9]), 'A']) # FIELD  9  : MON_GLRB_I_MEAN
        vals.append([convert_chn2meas_PWB_I(fields[10]), 'A']) # FIELD  10 : MON_PWB_I_MEAN

    return vals

def getconvertedvals___OLD(command, fields):
    vals = list()

    # the pork way (with great respect for porks)
    if command.name == 'SENSOR_GET_SINGLE':
        vn = fields[0]
        converter = None
        if vn == 'MON_5V_I':
            converter = channel2current_MON_5V_I
            units = 'A'
        elif vn in ['MON_LBL_I', 'MON_HYDRO_I']:
            converter = channel2current_12V
            units = 'A'
        elif vn in ['MON_DU_I', 'MON_DU_IRTN']:
            converter = channel2current_MON_DU_I
            units = 'A'
        elif vn == 'MON_BPS_V':
            converter = channel2voltage_MON_BPS_V
            units = 'V'
        elif vn == 'MON_THEATSINK':
            converter = channel2temperature_THEATSINK
            units = 'V (A.U.)'
        elif vn == 'MON_TBOARD':
            converter = channel2temperature_TBOARD
            units = 'C'
        else:
            pass
        if converter:
            vals.append(['',''])
            vals.append([converter(fields[1]), units]) # VALUE
            vals.append([converter(fields[2]), units]) # OFFSET
            vals.append([converter(fields[3]), units]) # MAXVALUE
            vals.append([converter(fields[4]), units]) # MEANVALUE
    elif command.name in ['SENSOR_VALUES_GETALL', 'SENSOR_AVERAGE_GETALL', 'SENSOR_OFFSETS_GETALL', 'SENSOR_MAXVALUES_GETALL']:
        vals.append([channel2current_MON_5V_I(fields[0]), 'A']) # MON_5V_I_MEAN
        vals.append([channel2current_12V(fields[1]), 'A']) # MON_LBL_I_MEAN
        vals.append([channel2current_MON_DU_I(fields[2]), 'A']) # MON_DU_I_MEAN
        vals.append([channel2current_MON_DU_I(fields[3]), 'A']) # MON_DU_IRTN_MEAN
        vals.append([channel2voltage_MON_BPS_V(fields[4]), 'V']) # MON_BPS_V_MEAN
        vals.append([channel2current_12V(fields[5]), 'A']) # MON_HYDRO_I_MEAN
        vals.append([channel2temperature_THEATSINK(fields[6]), 'V (A.U.)']) # MON_THEATSINK_MEAN
        vals.append([channel2temperature_TBOARD(fields[7]), 'C']) # MON_TBOARD_MEAN

    return vals

if __name__ == '__main__':
    # command line options
    # example
    # python sendcommand.py COMMAND_NAME payload0 payload1 ...
    # COMMAND_NAME is the human readable name of the command (e.g.: )

    # redirect stdout to null in order to avoid the warnings during object creation
    stdout = sys.stdout
    f = open(os.devnull, 'w')
    sys.stdout = f

    switch_list = commands.SwitchList()

    analog_variable_list = commands.AnalogVariableList(
        _var_enum_index_start=1,
        _alarm_enum_index_start=1)

    digital_variable_list = commands.DigitalVariableList(
        _var_enum_index_start=max(analog_variable_list.get_var_enum_indexes())+1,
        _alarm_enum_index_start=max(analog_variable_list.get_alarm_enum_indexes())+1)

    user_pin_list = commands.UserPinList()
    commands = commands.CommandList(switch_list, analog_variable_list, digital_variable_list, user_pin_list)

    # restore normal stdout
    sys.stdout = stdout

    if len(sys.argv) <= 1:
        print("Command code missing")
        sys.exit(0)

    command_name = sys.argv[1].upper()

    filtered_commands = [command for command in commands.entries() if command.name.startswith(command_name)]

    if len(filtered_commands) == 0:
        print('No command found with name starting with: "{}"'.format(command_name))
    elif len(filtered_commands) != 1:
        print('More than one command found with name starting with: "{}":'.format(command_name))
        for command in filtered_commands:
            print('    {}'.format(command.name))
        sys.exit(0)

    # get the wanted command
    command = filtered_commands[0]

    # expected number of request fields:
    req_field_count = len(command.request_payload)

    if len(sys.argv) != req_field_count + 2:
        print('Number of request payload fields not correct. The {} command expects {} fields; {} where given.'.format(command.name, len(command.request_payload), len(sys.argv) - 2))
        sys.exit(0)

    # prepare the payload
    payload_data = list()
    payload_field_values = list()
    idx = 2
    for field in command.request_payload:
        val = int(sys.argv[idx])
        payload_field_values.append(val)
        if isinstance(field, PayloadFieldU8):
            assert val < 2**8, 'Too big value for uint8'
            payload_data.append(val)
        elif isinstance(field, PayloadFieldU16):
            assert val < 2 ** 16, 'Too big value for uint16'
            payload_data.append((val >> 8) & 0xff)
            payload_data.append(val & 0xff)
        elif isinstance(field, PayloadFieldU32):
            assert val < 2 ** 32, 'Too big value for uint32'
            payload_data.append((val >> 24) & 0xff)
            payload_data.append((val >> 16) & 0xff)
            payload_data.append((val >> 8) & 0xff)
            payload_data.append(val & 0xff)
        elif isinstance(field, PayloadFieldEnum):
            assert val < 2 ** 8, 'Too big value for enum'
            payload_data.append(val)
        else:
            assert False, 'Unmanaged type {}'.format(field.__class__.__name__)
        idx += 1

    print("Sending packet:")
    print('    Command code: {} (raw data: {})'.format(command.name, command.request_code))
    # print '    Payload data: {} (raw data: {})'.format(payload_field_values, payload_data)
    print('    Request payload:')
    idx = 0
    for field in command.request_payload:
        print('        {} = {}'.format(field.name, payload_field_values[idx]))
        idx += 1

    if ASK_CONFIRM:
        if not ask_confirm():
            print("Operation aborted by user")
            sys.exit()

    jcmd = JSCRIPTFMT
    jcmd = jcmd.replace('[REQCODE]', str(command.request_code))
    jcmd = jcmd.replace('[RESPCODE]', str(command.response_code))
    jcmd = jcmd.replace('[RESPLEN]', str(2 * command.get_response_payload_len()))

    if not payload_data:
        jcmd = jcmd.replace('[REQPAYLOAD]', 'null')
    else:
        pl = ''
        for b in payload_data:
            # print b.__class__
            n0, n1 = uint8_to_nibbles(b)
            pl += chr(n1)
            pl += chr(n0)
        jcmd = jcmd.replace('[REQPAYLOAD]', pl)

    print('Executing command: "{}"'.format(jcmd))
    r = mydirtyexec(jcmd)
    print('Response:"{}"'.format(r.strip()))

    # convert nibbles to bytes
    payload_bytes = list()
    for k in range(0, len(r)-1, 2):
        d = 16 * int(r[k], 16) + int(r[k+1], 16)
        payload_bytes.append(d)

    print("Received packet:")
    # print '    Command code: {}'.format(command_code)
    # print '    Payload data: {} (raw data: {})'.format(payload_field_values, payload_data)
    print('    Response payload:')
    byte_idx = 0
    rawvalues = list();
    for field in command.response_payload:
        value = -1
        if isinstance(field, PayloadFieldU8):
            value = payload_bytes[byte_idx]
            rawvalues.append(value)
            byte_idx += 1
        elif isinstance(field, PayloadFieldU16):
            value = payload_bytes[byte_idx] << 8
            value += payload_bytes[byte_idx+1]
            rawvalues.append(value)
            byte_idx += 2
        elif isinstance(field, PayloadFieldU32):
            value = payload_bytes[byte_idx] << 24
            value += payload_bytes[byte_idx+1] << 16
            value += payload_bytes[byte_idx+2] << 8
            value += payload_bytes[byte_idx+3]
            rawvalues.append(value)
            byte_idx += 4
        elif isinstance(field, PayloadFieldEnum):
            value = field.get_value_by_index(payload_bytes[byte_idx])
            rawvalues.append(value)
            byte_idx += 1
        else:
            assert False, 'Unmanaged type {}'.format(field.__class__.__name__)

    convertedvals = getconvertedvals(command, rawvalues)

    field_idx = 0
    for field in command.response_payload:
        s = '        {} = {} '.format(field.name, rawvalues[field_idx])
        if convertedvals and field_idx < len(convertedvals): 
            if convertedvals[field_idx][0]:
                s += '({:0.3} {})'.format(convertedvals[field_idx][0], convertedvals[field_idx][1])
        print(s)
        field_idx += 1

