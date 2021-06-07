from enum import Enum

class LogsSeverity(Enum):
    Debug = 1
    Regular = 0
    WaningsAndErrors = 2
    ErrorsOnly = 3
    NoLogs = 4


class PrintOption(Enum):
    NoPrints = 0
    PrintInPython = 1


class Logger:
    class LogType(Enum):
        info    = 0
        debug   = 1
        warning = 2
        error   = 3
    
    #literals
    LOGS_TITLE = "MotorApp::Logs: Starts!"
    LOGS_SEPARATOR = '\n'
    INF_PREAMPULE = 'Info::'
    DBG_PREAMPULE = 'Debug::'
    WRN_PREAMPULE = 'Waring::'
    ERR_PREAMPULE = 'Error::'
    
    #variables
    severity = LogsSeverity.Regular
    printOptions = PrintOption.NoPrints
    valErrorRaise = False

    #methods
    def __init__(self, severity=LogsSeverity.Regular, printOptions=PrintOption.NoPrints, valErrorRaise=False):
        self.severity = severity
        self.printOptions = printOptions
        self.valErrorRaise = valErrorRaise
        with open('appLogs.log', 'w') as self.__logFile:
            self.__printStrict(self.LOGS_TITLE)
            self.__logFile.write(self.LOGS_TITLE + self.LOGS_SEPARATOR)

    def __del__(self):
        self.__logFile.close()
        
    def __writeToLogFile(self, inString):
        with open('appLogs.log', 'a') as self.__logFile:
            self.__logFile.write(inString + self.LOGS_SEPARATOR)


    #log types calls
    def info(self, inString):
        self.__loggerCall(self.LogType.info, inString)
                
    def debug(self, inString):
        self.__loggerCall(self.LogType.debug, inString)
            
    def warning(self, inString):
        self.__loggerCall(self.LogType.warning, inString)
                
    def error(self, inString):
        self.__loggerCall(self.LogType.error, inString)        
    
         
    #Private methods  
    def __loggerCall(self, logType, inString):
        if self.__isLogTypeOutOfSeverity(logType) or not self.__isStrType(inString):
            return
        preamble = self.__getLogTypePreamble(logType)
        logString = preamble + inString
        self.__writeToLogFile(logString)
        self.__printStrict(logString)
    
    def __getLogTypePreamble(self, logType):
        if logType == self.LogType.info:
            return self.INF_PREAMPULE
        elif logType == self.LogType.debug:
            return self.DBG_PREAMPULE
        elif logType == self.LogType.warning:
            return self.WRN_PREAMPULE
        elif logType == self.LogType.error:
            return self.ERR_PREAMPULE
        return ''    
        
    def __isLogTypeOutOfSeverity(self, logType):
        if logType == self.LogType.info:
            if not self.__isInfoSeverityScope():
                return True
        elif logType == self.LogType.debug:
            if not self.__isDebugSeverityScope():
                return True
        elif logType == self.LogType.warning:
            if not self.__isWarningSeverityScope():
                return True
        elif logType == self.LogType.error:
            if not self.__isErrorSeverityScope():
                return True
                
               
    def __isInfoSeverityScope(self):
        if self.severity == LogsSeverity.Regular or self.severity == LogsSeverity.Debug:
            return True
        else:
            return False
    
    def __isDebugSeverityScope(self):
        if self.severity == LogsSeverity.Debug:
            return True
        else:
            return False   
        
    def __isWarningSeverityScope(self):
        if self.severity != LogsSeverity.NoLogs and self.severity != LogsSeverity.ErrorsOnly: 
            return True
        else:
            return False     
        
    def __isErrorSeverityScope(self):
        if self.severity != LogsSeverity.NoLogs:
            return True
        else:
            return False     
        
    def __isStrType(self, string):
        if isinstance(string, str):
            return True
        else:
            if self.__isErrorSeverityScope():
                self.__printStrict(self.__LoggerTypeError())
                self.__writeToLogFile(self.__LoggerTypeError())
            if self.valErrorRaise:
                raise
            return False

    def __printStrict(self, string):
        if self.printOptions == PrintOption.PrintInPython:
            print(string)

    def __LoggerTypeError(self):
        return "{0}{1}: Passed variable is not a string!".format(self.ERR_PREAMPULE, self.__LoggerTypeError.__name__)


# main
def main():
    # Test due to lack of Unit tests
    logger = Logger(LogsSeverity.Debug, PrintOption.PrintInPython, )
    logger.info("{0}::{1}: Read requested"
                .format("Test", __name__))
    logger.info(2)
    
    logger.severity = LogsSeverity.Debug
    logger.info("Now severity debug!")
    logger.debug("Now severity debug!")
    logger.warning("Now severity debug!")
    logger.error("Now severity debug!")
    
    logger.severity = LogsSeverity.Regular
    logger.info("Now severity regular!")
    logger.debug("Now severity regular!")
    logger.warning("Now severity regular!")
    logger.error("Now severity regular!")
    
    logger.severity = LogsSeverity.WaningsAndErrors
    logger.info("Now severity wrn and err!")
    logger.debug("Now severity wrn and err!")
    logger.warning("Now severity wrn and err!")
    logger.error("Now severity wrn and err!")
    
    logger.severity = LogsSeverity.ErrorsOnly
    logger.info("Now severity err!")
    logger.debug("Now severity err!")
    logger.warning("Now severity err!")
    logger.error("Now severity err!")
    
    logger.severity = LogsSeverity.NoLogs
    logger.info("This should not be desplayed")
    logger.debug("This should not be desplayed")
    logger.warning("This should not be desplayed")
    logger.error("This should not be desplayed")
       
       
if __name__ == "__main__":
    main()
