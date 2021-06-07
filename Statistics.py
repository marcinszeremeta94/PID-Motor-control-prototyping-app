from Logger import Logger
from Logger import LogsSeverity
from Logger import PrintOption
import statistics
import numpy as np

class StatisticsData:
    lastValue           = 0
    avgOfNSamples       = 0
    stdDev              = 0 
    median              = 0
    mode                = 0
    maxValue            = 0
    minValue            = 0
    amplitude           = 0
    relativeError       = 0
    absoluteError       = 0 
     
     
class Statistics:
    __statisticsData = StatisticsData()
    __logger            = None
    __dataFillIndex     = 0
    __NSamples          = 500
    __dataBuffer        = np.array(np.zeros(__NSamples))
    __valOfTheTask      = None 
    __handler           = None
    
    #methods
    def __init__(self, logger):
        self.__logger = logger
        self.__logger.debug("{0}: Created".format(self.__class__.__name__))
    
    #interface    
    def handleNewData(self, receivedValue):
        self.__statisticsData.lastValue = receivedValue
        self.__dataBuffer[self.__dataFillIndex] = receivedValue
        self.__dataFillIndex += 1
        if self.__dataFillIndex == self.__NSamples:
            self.__dataFillIndex = 0
        self.__reCountStatisticsData()
        if self.__handler != None:
            self.__handler.updateStatistics(self.getStatistics())
    
    def passHandler(self, handler):
        self.__handler = handler
        
    #get values
    def getStatistics(self):
        return self.__statisticsData
    
    def getAvgValue(self):
        return self.__statisticsData.avgOfNSamples
    
    def getStdDevValue(self):
        return self.__statisticsData.stdDev
    
    def getModeValue(self):
        return self.__statisticsData.mode
    
    def getMedianValue(self):
        return self.__statisticsData.median
    
    def getAmplitudeValue(self):
        return self.__statisticsData.amplitude
    
    def getMinValue(self):
        return self.__statisticsData.minValue
    
    def getMaxValue(self):
        return self.__statisticsData.maxValue
    
    def getRelativeErrValue(self):
        return self.__statisticsData.relativeError
    
    def getAbsoluteErrValue(self):
        return self.__statisticsData.absoluteError
    
    def getLastVal(self):
        return self.__statisticsData.lastValue
    
    def getSamplesValue(self):
        return self.__NSamples

    def getValOfTheTask(self):
        return self.__valOfTheTask
    
    #Change state
    def setValOfTheTask(self, newVal):
        self.__valOfTheTask = newVal
        
    def setSamplesValue(self, newSamplesVal):
        self.__NSamples = newSamplesVal
        self.resetStatistics()
    
    def resetStatistics(self):
        self.__dataFillIndex = 0
        self.__clearStatistics()
        self.__clearBuffer()
        
    #Provate methods
    def __reCountStatisticsData(self):
        self.__countAverage()
        self.__countStdDev()
        self.__countMode()
        self.__countMedian()
        self.__countMin()
        self.__countMax()
        self.__countAmplitude()
        self.__countAbsoluteError()
        self.__countRelativeError()
    
    def __countAverage(self):
        self.__statisticsData.avgOfNSamples = statistics.mean(self.__dataBuffer)
    
    def __countStdDev(self):
        self.__statisticsData.stdDev = statistics.stdev(self.__dataBuffer)
        
    def __countMode(self):
        self.__statisticsData.mode = statistics.mode(self.__dataBuffer)
    
    def __countMedian(self):
        self.__statisticsData.median = statistics.median(self.__dataBuffer)
        
    def __countMin(self):
        self.__statisticsData.minValue = np.min(self.__dataBuffer)
        
    def __countMax(self):
        self.__statisticsData.maxValue = np.max(self.__dataBuffer)
        
    def __countAmplitude(self):
        self.__statisticsData.amplitude = self.__statisticsData.maxValue - self.__statisticsData.minValue
        
    def __countAbsoluteError(self):
        if self.__valOfTheTask == None:
            self.__statisticsData.absoluteError = 0
        absoluteFromMin = np.abs(float(self.__valOfTheTask) - float(self.__statisticsData.minValue))
        absoluteFromMax = np.abs(float(self.__valOfTheTask) - float(self.__statisticsData.maxValue))
        self.__statisticsData.absoluteError = absoluteFromMin if absoluteFromMin > absoluteFromMax else absoluteFromMax
        
    def __countRelativeError(self):
        if self.__valOfTheTask == None:
            self.__statisticsData.absoluteError = 0
        if self.__valOfTheTask != 0:
            self.__statisticsData.relativeError =  float(self.__statisticsData.absoluteError) / float(self.__valOfTheTask) * 100
        else:
            self.__statisticsData.absoluteError = 0
        
    def __clearStatistics(self):
        self.__statisticsData = StatisticsData()
        
    def __clearBuffer(self):
        self.__dataBuffer = np.array(np.zeros(self.__NSamples))

# main
def main():
    # Test due to lack of Unit tests
    logger = Logger(LogsSeverity.Debug, PrintOption.NoPrints)
    statistics = Statistics(logger)
    
    statistics.setSamplesValue(300)
    statistics.setValOfTheTask(100)
    
    for i in range(300):
        statistics.handleNewData(i)
        
    print(statistics.getStatistics())
    print(statistics.getAvgValue())
    print(statistics.getStdDevValue())
    print(statistics.getModeValue())
    print(statistics.getMedianValue())
    print(statistics.getMaxValue())
    print(statistics.getMinValue())
    print(statistics.getAmplitudeValue())
    print(statistics.getRelativeErrValue())
    print(statistics.getAbsoluteErrValue())
    print(statistics.getLastVal())
    print(statistics.getSamplesValue())
    print(statistics.getValOfTheTask())
    
    statistics.resetStatistics()
    print(statistics.getLastVal())
    print("statistics 2") 

       
if __name__ == "__main__":
    main()
