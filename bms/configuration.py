

class Config(object):
    WWRSA = '' #ip
    WWRSB = '' #ip
    DU = '0' #ip or 0 for default *.*.1.100
    TEMP_MONITORING_ALARM = False #if the temp > temp_alarm SET TRUE 
    TEMP_MONITORING_STATUS = False #temp monitoring status (not include if a temp alarm is set)
    TEMP_ALARM = 0 #temp limit alarm
    TEMP_OVER_LIMIT = False #a dictionary of last temps with at least one over limit
    NO_CONN = {'status' : False}

    @staticmethod
    def init_app(app):
        pass

class DUMMY(Config):
    USEDUMMY = True
    TDK_LAMBDA = True
    TDK_STATUS = "enabled"

class BMTEST(Config):
    USEDUMMY = False
    TDK_LAMBDA = True
    TDK_STATUS = "enabled"

class ONSHORE(Config):
    USEDUMMY = False
    TDK_LAMBDA = False
    TDK_STATUS = "disabled"

config = {
    'DEV' : DUMMY,
    'BMTEST' : BMTEST,
    'ONSHORE' : ONSHORE,
    'default' : DUMMY
}