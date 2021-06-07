from InitSettings import RegulatorConf
from enum import Enum

class MotorDir(Enum):
    LEFT    = 0
    RIGHT   = 1
        
class PidState(Enum):
    OFF     = 0
    ON      = 1
        
class MsgRpmSubState(Enum):
    OFF     = 0
    ON      = 1
    
class MotorControlState(Enum):
    OFF         = 0
    PID         = 1
    FREE_RUN    = 3

class RegulatorState:
    kp                  = RegulatorConf.KP_INIT
    ki                  = RegulatorConf.KI_INIT
    kd                  = RegulatorConf.KD_INIT
    rpmSet              = RegulatorConf.RPM_INIT
    motorDir            = MotorDir.RIGHT
    pidState            = PidState.OFF
    msgRpmSubState      = MsgRpmSubState.OFF
    motorControlState   = MotorControlState.OFF
 
 
 
# main
def main():
    regulator = RegulatorState()
   
if __name__ == "__main__":
    main()
