from SerialDriver import SerialDriver
from SerialDriver import SerialConnectionState
from CsvHandler import CsvHandler
from Logger import Logger
from RegulatorState import PidState, RegulatorState, MotorDir, MsgRpmSubState, MotorControlState
from InitSettings import RegulatorConf
from Statistics import Statistics
import Protocol as pt
import numpy as np
import time


class Manager:
    #private handlers
    __serialDriver      = None
    __regulatorState    = None
    __statistics        = None
    __csvHandler        = None
    __guiHandler        = None
    __logger            = None
    
    #private variables
    __ReadEventsOngoing = False
    __avgIndex = 0
    __avgList = np.array(np.zeros(RegulatorConf.NUM_OF_SAMPLES_TO_AVG))

    #methods
    def __init__(self, logger):
        self.__logger = logger
        self.__logger.debug("{0}: Created"
                .format(self.__class__.__name__))
        self.__regulatorState   = RegulatorState()
        self.__statistics       = Statistics(logger)
        self.__serialDriver     = SerialDriver(logger)
        self.__csvHandler       = CsvHandler(logger)
        self.__csvHandler.writeNewData(0)
        
    def __del__(self):
        if self.__isConnected:
            self.resetDeviceReq()
        self.cancelAsyncReadEvents() 
        del self.__serialDriver
    
    def passGui(self, gui):
        self.__logger.info("{0}::{1}: GUI reference cached"
                .format(self.__class__.__name__, self.passGui.__name__))
        self.__guiHandler = gui
        self.__statistics.passHandler(gui)
        self.__statistics.setValOfTheTask(RegulatorConf.RPM_INIT)
        self.__serialDriver.establishAndConnect()
        if self.__isConnected():
            self.__guiHandler.updateConnectionData(self.__isConnected())
            self.requestAsyncReadEvents()
    
    #Reading event management    
    def requestAsyncReadEvents(self):
        self.__logger.debug("{0}::{1}: <-"
                .format(self.__class__.__name__, self.requestAsyncReadEvents.__name__))
        if self.__guiHandler != None and self.__ReadEventsOngoing == False:
            self.__guiHandler.asyncRead()
            self.__ReadEventsOngoing = True
            self.__logger.debug("{0}::{1}: Read requested"
                    .format(self.__class__.__name__, self.requestAsyncReadEvents.__name__))   
        
    def cancelAsyncReadEvents(self):
        self.__logger.debug("{0}::{1}: <-"
                    .format(self.__class__.__name__, self.cancelAsyncReadEvents.__name__))   
        if self.__guiHandler != None and self.__ReadEventsOngoing == True:
            self.__guiHandler.asyncReadCancel()
            self.__ReadEventsOngoing = False
            self.__logger.debug("{0}::{1}: Read cancelled"
                    .format(self.__class__.__name__, self.cancelAsyncReadEvents.__name__))   
        
    def __isConnected(self):
        if self.__serialDriver.getState() == SerialConnectionState.Connected:
            return True
        else:
            return False
    
    
    #Handling GUI callbacks
    #Value Change Requests
    def setPidValsReq(self, kp, ki, kd):
        self.__logger.info("{0}::{1}: Requested change of PID values: Kp: {2}, Ki: {3}, Kd: {4}."
                    .format(self.__class__.__name__, self.setPidValsReq.__name__, kp, ki, kd))   
        if self.__serialDriver.writeData(pt.buildCmd(pt.SET, pt.PID_KP_VAL, kp)):
            self.__regulatorState.kp = kp
            time.sleep(0.001)
        if self.__serialDriver.writeData(pt.buildCmd(pt.SET, pt.PID_KI_VAL, ki)):
            self.__regulatorState.ki = ki
            time.sleep(0.001)
        if self.__serialDriver.writeData(pt.buildCmd(pt.SET, pt.PID_KD_VAL, kd)):
            self.__regulatorState.kd = kd
        
    def setTargetRpmValReq(self, rpmSet):
        self.__logger.info("{0}::{1}: Requested change of rpm PID target value: {2}."
                    .format(self.__class__.__name__, self.setTargetRpmValReq.__name__, rpmSet))   
        if self.__serialDriver.writeData(pt.buildCmd(pt.SET, pt.TARGET_RPM, rpmSet)):
            self.__statistics.setValOfTheTask(rpmSet)
            self.__regulatorState.rpmSet = rpmSet
            
    def setPercentMotorSpeed(self, percentSpeed):
        self.__logger.info("{0}::{1}: Requested change of motor speed: {2}."
                    .format(self.__class__.__name__, self.setTargetRpmValReq.__name__, percentSpeed))
        self.PidReq(PidState.OFF)
        time.sleep(0.001)
        self.rpmSubscriptionReq(MsgRpmSubState.ON)
        if self.__serialDriver.writeData(pt.buildCmd(pt.SET, pt.MOT_PERC_SPEED, percentSpeed)): 
            self.__regulatorState.motorControlState = MotorControlState.FREE_RUN
            self.__guiHandler.updateMotorControlState(self.__regulatorState.motorControlState)   
            
    def setServoAngleReq(self, servoAngle):
        self.__logger.info("{0}::{1}: Requested change of servo value: {2}."
                    .format(self.__class__.__name__, self.setServoAngleReq.__name__, servoAngle))   
        self.__serialDriver.writeData(pt.buildCmd(pt.SET, pt.SERVO, servoAngle))
    
    #Special Requests
    def rpmSubscriptionReq(self, subscriptionState):
        self.__logger.info("{0}::{1}: Subscription data  {2}."
                    .format(self.__class__.__name__, self.rpmSubscriptionReq.__name__, \
                        "Request" if subscriptionState == MsgRpmSubState.ON else "Cancell"))
        if self.__serialDriver.writeData(pt.buildSpecialCmd\
                    (pt.SET_DATA_SUB_REQ if subscriptionState == MsgRpmSubState.ON else pt.CLEAR_DATA_SUB_REQ)):
            self.__regulatorState.msgRpmSubState=MsgRpmSubState.ON if subscriptionState == MsgRpmSubState.ON else MsgRpmSubState.OFF
    
    def PidReq(self, pidState):
        self.__logger.info("{0}::{1}: PID request  {2}."
                    .format(self.__class__.__name__, self.PidReq.__name__, "ON" if pidState == PidState.ON else "OFF"))
        self.__regulatorState.pidState = pidState
        if pidState == PidState.ON:
            self.__statistics.setValOfTheTask(self.__regulatorState.rpmSet)
        if self.__serialDriver.writeData(pt.buildSpecialCmd(pt.PID_START if pidState == PidState.ON else pt.PID_STOP)):
            time.sleep(0.001)
            self.rpmSubscriptionReq(MsgRpmSubState.ON if pidState == PidState.ON else MsgRpmSubState.OFF)  
            time.sleep(0.001)
            self.__serialDriver.writeData(pt.buildCmd(pt.SET, pt.MOT_PERC_SPEED, 0))
            self.__regulatorState.motorControlState = MotorControlState.PID if pidState == PidState.ON else MotorControlState.OFF
            self.__guiHandler.updateMotorControlState(self.__regulatorState.motorControlState)        
            
    def motDirReq(self):
        self.__logger.info("{0}::{1}: Motor direction change to the {2} request."
                    .format(self.__class__.__name__, self.motDirReq.__name__,\
                        "Left" if self.__regulatorState.motorDir == MotorDir.RIGHT else "Right"))
        if self.__serialDriver.writeData(pt.buildSpecialCmd \
                (pt.MOT_DIR_LEFT if self.__regulatorState.motorDir == MotorDir.RIGHT else pt.MOT_DIR_RIGHT)):
            self.__regulatorState.motorDir = MotorDir.LEFT if self.__regulatorState.motorDir == MotorDir.RIGHT else MotorDir.RIGHT 
            self.__guiHandler.updateMotorDir(self.__regulatorState.motorDir)
            
    def resetDeviceReq(self):
        self.__logger.info("{0}::{1}: Requested regulator reset!"
                    .format(self.__class__.__name__, self.resetDeviceReq.__name__))   
        if self.__serialDriver.writeData(pt.buildSpecialCmd(pt.RESET_SYS_REQ_MSG)):
            self.__statistics.resetStatistics()
            self.__avgList = np.array(np.zeros(RegulatorConf.NUM_OF_SAMPLES_TO_AVG))
    
    def sendTestRpmLoopback(self, data):
        self.__logger.info("{0}::{1}: Loopback Test!"
                    .format(self.__class__.__name__, self.sendTestRpmLoopback.__name__)) 
        self.__serialDriver.writeData(pt.buildRpmTestLoopbackResp(data))
        
    def reconnectWithNewPort(self, newPort):
        self.__logger.info("{0}::{1}: Requested reconnection"
                    .format(self.__class__.__name__, self.reconnectWithNewPort.__name__)) 
        self.PidReq(PidState.OFF)
        self.cancelAsyncReadEvents()
        self.__serialDriver.changePort(newPort)
        if self.__isConnected() :
            self.requestAsyncReadEvents()
            self.__logger.info("{0}::{1}: Successfully reconnected"
                    .format(self.__class__.__name__, self.reconnectWithNewPort.__name__)) 
        else:
            self.__logger.error("{0}::{1}: Reconnection Failed"
                    .format(self.__class__.__name__, self.reconnectWithNewPort.__name__))
        self.__guiHandler.updateConnectionData(self.__isConnected())
                      
                      
        
    # Response from regulator handle
    def handleRespMsg(self):
        #only returning rmp for now
        readData = self.__serialDriver.readLine()
        if readData != '':
            receivedValue = pt.processIncomingMsg(readData)
            
            if self.__avgIndex == RegulatorConf.NUM_OF_SAMPLES_TO_AVG:
                self.__avgIndex = 0
            self.__avgList[self.__avgIndex] = receivedValue
            self.__avgIndex += 1
            avgRun = int(sum(self.__avgList)/RegulatorConf.NUM_OF_SAMPLES_TO_AVG)
            
            self.__guiHandler.handleNewData(avgRun)
            if self.__regulatorState.pidState == PidState.ON:
                self.__statistics.handleNewData(avgRun)
                self.__csvHandler.writeNewData(avgRun)
     
    
    
# main
def main():
    manager = Manager(Logger())
    manager.resetDeviceReq()
    manager.setPidValsReq(1.2 , -0.1, 0.762)
    manager.setTargetRpmValReq(2000)
    manager.rpmSubscriptionReq(MsgRpmSubState.ON)
    manager.PidReq(True)
    print("DONE!")

if __name__ == "__main__":
    main()
