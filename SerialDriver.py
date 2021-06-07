import serial
from enum import Enum
from InitSettings import ConnectionConf as conf
from Logger import Logger
from Logger import LogsSeverity
from Logger import PrintOption 

class SerialConnectionState(Enum):
    NotConnected = 0
    Connected = 1
    Failed = 2
    
class ConnectionData:
    port        = conf.PORT_NAME
    baudrate    = conf.SPEED_BAUD
    byteSize    = serial.EIGHTBITS
    parity      = serial.PARITY_NONE
    stopBits    = serial.STOPBITS_ONE
    timeOut     = conf.TIME_OUT

class SerialDriver:
    # private variables
    __mConnectionData   = ConnectionData()
    __mState            = SerialConnectionState.NotConnected
    __logger            = None
    __mSerialPort       = None

    # methods
    def __init__(self, logger):
        self.__logger = logger
        self.__logger.debug("{0}: Created".format(self.__class__.__name__))

    def __del__(self):  
        if self.__mState == SerialConnectionState.Connected:
            self.disconnect() 

    def getState(self):
        return self.__mState
    
    def establishAndConnect(self):
        self.establishConnection()
        self.connect() 
    
    def changePort(self, newPort):
        self.__mConnectionData.port = newPort
        self.__logger.info("{0}::{1}: Connection port changed to: {2}"
                    .format(self.__class__.__name__, self.changePort.__name__, newPort)) 
        self.establishAndConnect()    

    def configureConnectionData(self, connectionData = ConnectionData()):
        self.__mConnectionData.port     = connectionData.port
        self.__mConnectionData.baudrate = connectionData.baudrate
        self.__mConnectionData.byteSize = connectionData.byteSize
        self.__mConnectionData.parity   = connectionData.parity
        self.__mConnectionData.stopBits = connectionData.stopBits
        self.__mConnectionData.timeOut  = connectionData.timeOut
        self.__logger.info("{0}::{1}: Connection configuration changed"
                    .format(self.__class__.__name__, self.configureConnectionData.__name__)) 
        self.establishAndConnect()

    def establishConnection(self):
        self.__logger.debug("{0}::{1}: <-".format(self.__class__.__name__, self.establishConnection.__name__))
        self.__mState = SerialConnectionState.NotConnected
        if self.__mSerialPort != None:
            del self.__mSerialPort
        try:
            self.__mSerialPort = serial.Serial(port=self.__mConnectionData.port, baudrate=self.__mConnectionData.baudrate,
                                              bytesize=self.__mConnectionData.byteSize, parity=self.__mConnectionData.parity,
                                              stopbits=self.__mConnectionData.stopBits, timeout=self.__mConnectionData.timeOut)
            if self.__mSerialPort.is_open:
                self.__mSerialPort.close()
                
            self.__logger.info("{0}::{1}: Connection established"
                    .format(self.__class__.__name__, self.establishConnection.__name__))
            return True
        except:
            self.__logger.warning("{0}::{1}: The connection establishing failed!"
                  .format(self.__class__.__name__, self.establishConnection.__name__))
            self.__mState = SerialConnectionState.Failed
            return False


    def connect(self):
        self.__logger.debug("{0}::{1}: <-".format(self.__class__.__name__, self.connect.__name__))
        if self.__CheckConnectionEstablishment():
            if not self.__CheckConnection():
                try:
                    self.__mSerialPort.open()
                except:
                    self.__logger.warning("{0}::{1}: Connecting failed"
                            .format(self.__class__.__name__, self.connect.__name__))
                    self.__mState = SerialConnectionState.Failed
                    return False
                
                if self.__mSerialPort.is_open:
                    self.__mState = SerialConnectionState.Connected
                    self.__logger.info("{0}::{1}: Connected"
                            .format(self.__class__.__name__, self.connect.__name__))
                    return True
                else:
                    self.__mState = SerialConnectionState.Failed
                    self.__logger.warning("{0}::{1}: Connecting failed"
                            .format(self.__class__.__name__, self.connect.__name__))   
            else:
                self.__logger.warning("{0}::{1}: Already Connected"
                        .format(self.__class__.__name__, self.connect.__name__)) 
        return False


    def disconnect(self):
        self.__logger.debug("{0}::{1}: <-".format(self.__class__.__name__, self.disconnect.__name__))
        if self.__CheckConnectionEstablishment():
            if self.__CheckConnection():
                self.__mSerialPort.close()
                self.__mState = SerialConnectionState.NotConnected
                self.__logger.info("{0}::{1}: Disconnected"
                        .format(self.__class__.__name__, self.disconnect.__name__))
                return True
        return False


    def writeData(self, dataToWrite):
        self.__logger.debug("{0}::{1}: <-".format(self.__class__.__name__, self.writeData.__name__))
        if self.__CheckConnectionEstablishment():
            if self.__CheckConnection():
                self.__mSerialPort.write(dataToWrite.encode())
                self.__logger.debug("{0}::{1}: Data sent"
                        .format(self.__class__.__name__, self.writeData.__name__))
                return True
        return False


    def readData(self, msgLen):
        out = ""
        if self.__CheckConnectionEstablishment():
            if self.__CheckConnection():
                while self.__mSerialPort.in_waiting > 0:
                    out += self.__mSerialPort.read(msgLen).decode('Asci')
        return out


    def readLine(self):
        out = ""
        if self.__CheckConnectionEstablishment():
            if self.__CheckConnection():
                if(self.__mSerialPort.in_waiting > 0):
                    out = self.__mSerialPort.readline().decode('Ascii')
        return out  
            
        
    #private methods    
    def __CheckConnection(self):
        if self.__mState == SerialConnectionState.Connected:
            return True
        else:
            self.__logger.info("{0}::{1}: Connection is Closed, no Data available!"
                    .format(self.__class__.__name__, self.__CheckConnection.__name__))
            return False
    
    def __CheckConnectionEstablishment(self):
        if self.__mSerialPort != None:
            return True
        else:
            self.__logger.error("{0}::{1}: Connection not established yet!"
                    .format(self.__class__.__name__, self.__CheckConnectionEstablishment.__name__))
            return False

# main
def main():
    # For testing due to lack of Unit Tests
    serialDriver = SerialDriver(Logger(LogsSeverity.Debug, PrintOption.PrintInPython))
    serialDriver.getState()
    serialDriver.writeData("TsT")
    serialDriver.readData(2)
    serialDriver.readLine()
    serialDriver.disconnect()
    confData = ConnectionData()
    confData.port = 'COM3'
    serialDriver.configureConnectionData(confData)
    serialDriver.establishConnection()
    serialDriver.connect()
    serialDriver.writeData("TsT")
    print("DONE!")


if __name__ == "__main__":
    main()
