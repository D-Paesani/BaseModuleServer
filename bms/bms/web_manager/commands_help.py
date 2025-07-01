

help_reset_maxvalues = """COMMAND NAME : "SENSOR_MAXVALUE_RESET"
      DESCRIPTION      : Reset the max value of one sensor (or all sensors)
      REQUEST CODE     : 96
      RESPONSE CODE    : 97
      REQUEST PAYLOAD  :
          LENGTH : 1 fields, 1 bytes
          FIELD #0  (uint8_t ) : VARIABLE_NUMBER_ALL, Variable number
              VARIABLE_NUMBER_ALL indexing:
                  [1] --> MON_DUL_BOARDTEMP
                  [2] --> MON_TEMP2
                  [3] --> MON_TEMP1
                  [4] --> MON_VEOC_RTN_I
                  [5] --> MON_VEOC_FWR_I
                  [6] --> MON_HYDRO_I
                  [7] --> MON_INPUT_V
                  [8] --> MON_LBL_I
                  [9] --> MON_GLRA_I
                  [10] --> MON_GLRB_I
                  [11] --> MON_PWB_I
                  [12] --> FLAG_DUL_ALARMPOS1
                  [13] --> FLAG_DUL_ALARMPOS2
                  [14] --> FLAG_DUL_ALARMNEG1
                  [15] --> FLAG_DUL_ALARMNEG2
                  [16] --> FLAG_HYDRO_PWR_FAULT
                  [17] --> FLAG_LBL_PWR_FAULT
                  [18] --> FLAG_GLRA_FAULT
                  [19] --> FLAG_GLRB_FAULT
                  [20] --> FLAG_POWERBOARD_FAULT
                  [21] --> FLAG_GLRA_GOOD
                  [22] --> FLAG_GLRB_GOOD
                  [23] --> FLAG_POWERBOARD_GOOD
                  [24] --> ALL_VARIABLES
      RESPONSE PAYLOAD :
          LENGTH : 0 fields, 0 bytes"""

help_alarm_threshold_get = """Details of commands starting with "ALARM_THRESHOLD_GET":

  COMMAND NAME : "ALARM_THRESHOLD_GET"
      DESCRIPTION      : Get the threshold value of one analog alarm
      REQUEST CODE     : 78
      RESPONSE CODE    : 79
      REQUEST PAYLOAD  :
          LENGTH : 1 fields, 1 bytes
          FIELD #0  (uint8_t ) : ALARM_NUMBER_ANALOG, Alarm number
              ALARM_NUMBER_ANALOG indexing:
                  [1] --> ALARM_SLOW_MON_VEOC_RTN_I
                  [2] --> ALARM_FAST_MON_VEOC_RTN_I
                  [3] --> ALARM_SLOW_MON_VEOC_FWR_I
                  [4] --> ALARM_FAST_MON_VEOC_FWR_I
                  [5] --> ALARM_SLOW_MON_HYDRO_I
                  [6] --> ALARM_FAST_MON_HYDRO_I
                  [7] --> ALARM_SLOW_MON_LBL_I
                  [8] --> ALARM_FAST_MON_LBL_I
      RESPONSE PAYLOAD :
          LENGTH : 2 fields, 3 bytes
          FIELD #0  (uint8_t ) : ALARM_NUMBER_ANALOG, Alarm number
              ALARM_NUMBER_ANALOG indexing:
                  [1] --> ALARM_SLOW_MON_VEOC_RTN_I
                  [2] --> ALARM_FAST_MON_VEOC_RTN_I
                  [3] --> ALARM_SLOW_MON_VEOC_FWR_I
                  [4] --> ALARM_FAST_MON_VEOC_FWR_I
                  [5] --> ALARM_SLOW_MON_HYDRO_I
                  [6] --> ALARM_FAST_MON_HYDRO_I
                  [7] --> ALARM_SLOW_MON_LBL_I
                  [8] --> ALARM_FAST_MON_LBL_I
          FIELD #1  (uint16_t) : THRESHOLD, Threshold value"""

help_alarm_threshold_set = """Details of commands starting with "ALARM_THRESHOLD_SET":

  COMMAND NAME : "ALARM_THRESHOLD_SET"
      DESCRIPTION      : Set the threshold value of one analog alarm
      REQUEST CODE     : 76
      RESPONSE CODE    : 77
      REQUEST PAYLOAD  :
          LENGTH : 2 fields, 3 bytes
          FIELD #0  (uint8_t ) : ALARM_NUMBER_ANALOG, Alarm number
              ALARM_NUMBER_ANALOG indexing:
                  [1] --> ALARM_SLOW_MON_VEOC_RTN_I
                  [2] --> ALARM_FAST_MON_VEOC_RTN_I
                  [3] --> ALARM_SLOW_MON_VEOC_FWR_I
                  [4] --> ALARM_FAST_MON_VEOC_FWR_I
                  [5] --> ALARM_SLOW_MON_HYDRO_I
                  [6] --> ALARM_FAST_MON_HYDRO_I
                  [7] --> ALARM_SLOW_MON_LBL_I
                  [8] --> ALARM_FAST_MON_LBL_I
          FIELD #1  (uint16_t) : THRESHOLD, Threshold value
      RESPONSE PAYLOAD :
          LENGTH : 0 fields, 0 bytes"""