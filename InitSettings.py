#Connection settings
class ConnectionConf:
    PORT_NAME   = 'COM4'
    SPEED_BAUD  = 115200
    TIME_OUT    = 1

#Regulator settings
class RegulatorConf:
    KP_INIT                 = '0.233'       #'0.178'
    KI_INIT                 = '4.66'        #'0.296'
    KD_INIT                 = '0.002796'    #'0.0053'
    RPM_INIT                = '2000'
    RPM_MSG_INTERVALS_MS    = 40
    MOTOR_DIR               = 'RIGHT'
    BASIC_PERCENT_SPEED     = '30'
    REVOLUTIONS_TO_AVG      = 1 
    TICKS_PER_REV           = 12
    
    NUM_OF_SAMPLES_TO_AVG   = REVOLUTIONS_TO_AVG * TICKS_PER_REV
    
    SERVO_ANGLE           = 30

#Gui Settings
class GuiConf:
    __regulatorConf         = RegulatorConf()
    RESOLUTION              = "1750x680"
    DISPLAY_TIME            = 10

#-------------------------------------------------------------
    #XAXEW = DISPLAY_TIME * __regulatorConf.RPM_MSG_INTERVALS_MS
    XAXEW = 500