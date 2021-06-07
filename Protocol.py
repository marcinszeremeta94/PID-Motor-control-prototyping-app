import numpy as np
from Logger import Logger
from Logger import LogsSeverity
from Logger import PrintOption
NUM_OF_REQ_SIGNS = 16
NUM_OF_RESP_SIGNS = 16

# GET = 'G'
SET = 'S'

# Set/Get commands - Only Set option is accepted
PID_KP_VAL = 'P'
PID_KI_VAL = 'I'
PID_KD_VAL = 'D'
TARGET_RPM = 'T'
MOT_PERC_SPEED = 'M'
SERVO = 's'

# Special Cmd's
PID_START = '+'
PID_STOP = '-'
SET_DATA_SUB_REQ = '>'  
CLEAR_DATA_SUB_REQ = '<' 
MOT_DIR_LEFT = 'L'
MOT_DIR_RIGHT = 'R'
RESET_SYS_REQ_MSG = '!'



def processIncomingMsg(incomingMsg):
    #Only messages with rpm values are accepted
    if incomingMsg[0] == 'R':
        return int(incomingMsg[1:len(incomingMsg)-1])
    return 0

def buildCmd(cmdType, cmd, value=0, logger = Logger()):
    tmpCmd = cmdType + cmd
    if value < 0:
        tmpCmd = tmpCmd + '-'
        value = abs(value)

    if __isInteger(value):
        value = int(value)
        valueStr = str(value)
        zeroesToFill = NUM_OF_REQ_SIGNS - \
            (len(tmpCmd) + len(valueStr) + len('\n'))
        if zeroesToFill < 0:
            logger.error("{0}: Value out of Range!".format(buildCmd.__name__))   
            return buildSpecialCmd(RESET_SYS_REQ_MSG)
        tmpCmd = __CmdFrontSupplement(tmpCmd, zeroesToFill)
        return tmpCmd + valueStr + '\n'

    elif __isFloat(value):
        if len(str(int(value))) > NUM_OF_REQ_SIGNS - (len(tmpCmd) + len('.') + len('\n')):
            logger.error("{0}: Value out of Range!".format(buildCmd.__name__))   
            return buildSpecialCmd(RESET_SYS_REQ_MSG)
        tmpCmd = tmpCmd + str(value)
        if len(tmpCmd) > NUM_OF_REQ_SIGNS - 1:
            tmpCmd = tmpCmd[:NUM_OF_REQ_SIGNS - 1]
        return __CmdBackSupplement(tmpCmd)

    else:
        logger.error("{0}: Passed Value Not a float!".format(buildCmd.__name__))   
        return buildSpecialCmd(RESET_SYS_REQ_MSG)


def buildSpecialCmd(sCmd):
    return __CmdBackSupplement(sCmd)


def buildRpmTestLoopbackResp(value):
    return 'R' + str(value) + '\n'


#helper functions
def __CmdBackSupplement(strToFill):
    while len(strToFill) != NUM_OF_REQ_SIGNS - 1:
        strToFill += '0'
    strToFill += '\n'
    return strToFill

def __CmdFrontSupplement(strToFill, numOfZeros):
    for i in range(numOfZeros):
        strToFill += '0'
    return strToFill

def __isInteger(n):
    if isinstance(n, int):
        return True
    if isinstance(n, float):
        return n.is_integer()
    return False

def __isFloat(n):
    if isinstance(n, float):
        return True
    return False


def main():
    #For testing due to lack of Unit Tests
    print(buildSpecialCmd(MOT_DIR_LEFT))
    print(buildSpecialCmd(MOT_DIR_RIGHT))
    print(buildSpecialCmd(PID_START))
    print(buildSpecialCmd(PID_STOP))
    print(buildSpecialCmd(SET_DATA_SUB_REQ))
    print(buildSpecialCmd(CLEAR_DATA_SUB_REQ))
    
    print(buildCmd(SET, TARGET_RPM, 212))
    print(buildCmd(SET, TARGET_RPM, -312))
    print(buildCmd(SET, TARGET_RPM, -312.12222))
    print(buildCmd(SET, TARGET_RPM, 212.1211))
    print(buildCmd(SET, TARGET_RPM, 0.12911))
    print(buildCmd(SET, TARGET_RPM, 0.12911333333333333333333333333333333333333333))
    print(buildCmd(SET, MOT_PERC_SPEED, 80))
    print(buildCmd(SET, PID_KD_VAL, 0.19116))
    print(buildCmd(SET, PID_KI_VAL, 2.1916))
    print(buildCmd(SET, PID_KP_VAL, 0.19116))
    
    print(buildRpmTestLoopbackResp(25010))
    print(buildCmd(SET, TARGET_RPM, 22232323232112))
    print("DONE!")

if __name__ == "__main__":
    main()
