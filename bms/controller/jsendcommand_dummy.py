
import sys

aaa = sys.argv[2]

if "_AVERAGE_" in aaa:
    
    print "Sending packet:" 
    print "Command code: SENSOR_AVERAGE_GETALL (raw data: 100)" 
    print 'Request payload: Executing command: "./execute.sh NG_BPDCmd 10.0.1.100 100 101 44 null"' 
    print 'Response:"64b39aaba818716378ed01806fb8017e5f605c892828"'
    print "Received packet:"
    print "    Response payload:" 
    print "        MON_DUL_BOARDTEMP_MEAN = 25779 (30.6 C)" 
    print "        MON_TEMP2_MEAN = 39595 (31.7 C)"
    print "        MON_TEMP1_MEAN = 43032 (36.7 C)" 
    print "        MON_VEOC_RTN_I_MEAN = 29027 (0.433 A)"
    print "        MON_VEOC_FWR_I_MEAN = 30957 (0.547 A)" 
    print "        MON_HYDRO_I_MEAN = 384 (0.00213 mA)"
    print "        MON_INPUT_V_MEAN = 28600 (3.58e+02 V)" 
    print "        MON_LBL_I_MEAN = 382 (0.00371 mA)" 
    print "        MON_GLRA_I_MEAN = 24416 (2.25 A)"
    print "        MON_GLRB_I_MEAN = 23689 (2.18 A)"
    print "        MON_PWB_I_MEAN = 10280 (0.464 A)"
    
if "SENSOR_MAXVALUES_GETALL" in aaa:
    
    print "Sending packet:" 
    print "Command code: SENSOR_AVERAGE_GETALL (raw data: 100)" 
    print 'Request payload: Executing command: "./execute.sh NG_BPDCmd 10.0.1.100 100 101 44 null"' 
    print 'Response:"64b39aaba818716378ed01806fb8017e5f605c892828"'
    print "Received packet:"
    print "    Response payload:" 
    print "        MON_DUL_BOARDTEMP_MAXVALUE = 25779 (30.6 C)" 
    print "        MON_TEMP2_MAXVALUE = 39595 (31.7 C)"
    print "        MON_TEMP1_MAXVALUE = 43032 (36.7 C)" 
    print "        MON_VEOC_RTN_I_MAXVALUE = 29027 (0.433 A)"
    print "        MON_VEOC_FWR_I_MAXVALUE = 30957 (0.547 A)" 
    print "        MON_HYDRO_I_MAXVALUE = 384 (0.00213 mA)"
    print "        MON_INPUT_V_MAXVALUE = 28600 (3.58e+02 V)" 
    print "        MON_LBL_I_MAXVALUE = 382 (0.00371 mA)" 
    print "        MON_GLRA_I_MAXVALUE = 24416 (2.25 A)"
    print "        MON_GLRB_I_MAXVALUE = 23689 (2.18 A)"
    print "        MON_PWB_I_MAXVALUE = 10280 (0.464 A)"

# if "GETALL" in aaa:

#     print "Sending packet:"
#     print "    Command code: SENSOR_VALUES_GETALL (raw data: 90)"
#     print "    Request payload:"
#     print 'Executing command: "./execute.sh BPSCmd 10.2.14.100 90 91 40 null'
#     print 'Response:"4e80114077c077c0d3801b40018057c000000000"'
#     print "Received packet:"
#     print "    Response payload:"
#     print "        MON_5V_I_VALUE = 20096 (2.08 A)"
#     print "        MON_LBL_I_VALUE = 4416 (-0.00285 A)"
#     print "        MON_DU_I_VALUE = 30656 (0.526 A)"
#     print "        MON_DU_IRTN_VALUE = 30656 (0.526 A)"
#     print "        MON_BPS_V_VALUE = 54144 (3.34e+02 V)"
#     print "        MON_HYDRO_I_VALUE = 6976 (0.0352 A)"
#     print "        MON_THEATSINK_VALUE = 384 (0.024 V (A.U.))"
#     print "        MON_TBOARD_VALUE = 22464 (20.2 C)"
    
elif "SWITCH_CONTROL" in aaa:
    
    print "Received packet:"
    print "    Response payload:"
    print "        SWITCHNUM = SWITCH_VEOC_DIRECT"
    print "        SWITCHSTATE = CLOSED"
    

elif "RESCUE" in aaa:

    print "Sending packet:"
    print "    Command code: RESCUE_ENABLE (raw data: 110)"
    print "    Request payload:"
    print "        ENABLESTATE_NC = 2"
    print "Executing command: ./execute.sh BPSCmd 10.2.10.100 110 111 2 02"
    print "Response:00"
    print "Received packet:"
    print "    Response payload:"
    print "        ENABLESTATE = DISABLED" 
    
    
    
    

# import sys

# aaa = sys.argv[2]


# if "GETALL" in aaa:

#     print("Sending packet:")
#     print("    Command code: SENSOR_VALUES_GETALL (raw data: 90)")
#     print("    Request payload:")
#     print('Executing command: "./execute.sh BPSCmd 10.2.14.100 90 91 40 null')
#     print('Response:"4e80114077c077c0d3801b40018057c000000000"')
#     print("Received packet:")
#     print("    Response payload:")
#     print("        MON_5V_I_VALUE = 20096 (2.08 A)")
#     print("        MON_LBL_I_VALUE = 4416 (-0.00285 A)")
#     print("        MON_DU_I_VALUE = 30656 (0.526 A)")
#     print("        MON_DU_IRTN_VALUE = 30656 (0.526 A)")
#     print("        MON_BPS_V_VALUE = 54144 (3.34e+02 V)")
#     print("        MON_HYDRO_I_VALUE = 6976 (0.0352 A)")
#     print("        MON_THEATSINK_VALUE = 384 (0.024 V (A.U.))")
#     print("        MON_TBOARD_VALUE = 22464 (20.2 C)")
    
# elif "SWITCH_CONTROL" in aaa:
    
#     print("Received packet:")
#     print("    Response payload:")
#     print("        SWITCHNUM = SWITCH_VEOC_DIRECT")
#     print("        SWITCHSTATE = CLOSED")
    

# elif "RESCUE" in aaa:

#     print("Sending packet:")
#     print("    Command code: RESCUE_ENABLE (raw data: 110)")
#     print("    Request payload:")
#     print("        ENABLESTATE_NC = 2")
#     print("Executing command: ./execute.sh BPSCmd 10.2.10.100 110 111 2 02")
#     print("Response:00")
#     print("Received packet:")
#     print("    Response payload:")
#     print("        ENABLESTATE = DISABLED" )