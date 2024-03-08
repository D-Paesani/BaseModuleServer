
import sys

aaa = sys.argv[2]


if "GETALL" in aaa:

    print "Sending packet:"
    print "    Command code: SENSOR_VALUES_GETALL (raw data: 90)"
    print "    Request payload:"
    print 'Executing command: "./execute.sh BPSCmd 10.2.14.100 90 91 40 null'
    print 'Response:"4e80114077c077c0d3801b40018057c000000000"'
    print "Received packet:"
    print "    Response payload:"
    print "        MON_5V_I_VALUE = 20096 (2.08 A)"
    print "        MON_LBL_I_VALUE = 4416 (-0.00285 A)"
    print "        MON_DU_I_VALUE = 30656 (0.526 A)"
    print "        MON_DU_IRTN_VALUE = 30656 (0.526 A)"
    print "        MON_BPS_V_VALUE = 54144 (3.34e+02 V)"
    print "        MON_HYDRO_I_VALUE = 6976 (0.0352 A)"
    print "        MON_THEATSINK_VALUE = 384 (0.024 V (A.U.))"
    print "        MON_TBOARD_VALUE = 22464 (20.2 C)"
    
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