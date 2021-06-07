from Logger import Logger
import time
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.constants import TRUE
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
from Manager import Manager
import InitSettings
from RegulatorState import PidState , MotorDir, MotorControlState


class AppGui():
    #App fields
    root        = None
    __readJobId = None
    __mnr       = None
    __logger    = None

    #Animating plot fields
    xar = deque([0])
    yar = deque([0])
    __dataCounetr = 0 

    #Setup
    def __init__(self, appCore, logger):
        self.__logger = logger
        self.__logger.debug("{0}: Created"
                .format(self.__class__.__name__))
        self.root = tk.Tk()
        self.__mnr = appCore
        
        self.root.wm_title("PID motor prototyping")
        self.root.geometry(InitSettings.GuiConf.RESOLUTION)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.bind('<Return>', self.pressEnterCallback)
        #self.root.state('zoomed')
        self.create_widgets()
        self.__mnr.passGui(self)
            
        self.matplotCanvas()
        self.create_animated_plot_widget()
        animatiedPlot = animation.FuncAnimation(self.fig, self.animate, interval=100, blit=False)
        self.root.mainloop()
    
    def __del__(self):
        self.__logger.debug("{0}: Destroyed"
                .format(self.__class__.__name__))  
    
    
    #Widgets
    def create_animated_plot_widget(self):
        self.plotFrame = tk.Frame(self.root)
        self.plotFrame.grid(row=0, column=0, sticky=E+W+N+S)
        self.plotFrame.columnconfigure(0, weight=1)
        self.plotFrame.rowconfigure(0, weight=1)
        self.plotcanvas = FigureCanvasTkAgg(self.fig, self.plotFrame)
        self.plotcanvas.get_tk_widget().grid(row=0, column=0, sticky=E+W+N+S) 


    def create_widgets(self):
        self.controlPanelFrame = tk.Frame(self.root, width=100, height=100)
        self.controlPanelFrame.grid(row=0, column=1, sticky=E+W)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.labelPidkp = tk.Label(master=self.controlPanelFrame, text="Kp: ")
        self.entryPidkp = tk.Entry(master=self.controlPanelFrame)
        self.labelPidki = tk.Label(master=self.controlPanelFrame, text="Ki: ")
        self.entryPidki = tk.Entry(master=self.controlPanelFrame)
        self.labelPidkd = tk.Label(master=self.controlPanelFrame, text="Kd: ")
        self.entryPidkd = tk.Entry(master=self.controlPanelFrame)
        self.labelTargetRpm = tk.Label(master=self.controlPanelFrame, text="Set rpm: ")
        self.entryTargetRpm = tk.Entry(master=self.controlPanelFrame)
        self.separatorTop = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.separatorTop0 = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.labelMotorState = tk.Label(master=self.controlPanelFrame, text="Motor control state: ")
        self.labelValMotorState = tk.Label(master=self.controlPanelFrame, text="OFF")
        self.entryPercentMotSpeed = tk.Entry(master=self.controlPanelFrame)
        self.labelMotDir    = tk.Label(master=self.controlPanelFrame, text="Motor Direction: ")
        self.labelMotDirVal = tk.Label(master=self.controlPanelFrame, text=InitSettings.RegulatorConf.MOTOR_DIR)
        self.separatorMid = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.separatorMid0 = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.valueDescriptionLabel = tk.Label(master=self.controlPanelFrame, text="rpm now: ")
        self.valueLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.valueAvgDescriptionLabel =tk.Label(master= self.controlPanelFrame, text="rpm avg: ")
        self.valueAvgLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.valueStdDevDescriptionLabel =tk.Label(master= self.controlPanelFrame, text="rpm stdDev: ")
        self.valueStdDevLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.valueMedianDescriptionLabel =tk.Label(master= self.controlPanelFrame, text="rpm median: ")
        self.valueMedianLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.valueModeDescriptionLabel =tk.Label(master= self.controlPanelFrame, text="rpm mode: ")
        self.valueModeLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.valueAmplitudeDescriptionLabel =tk.Label(master= self.controlPanelFrame, text="rpm amplitude: ")
        self.valueAmplitudeLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.valueMinDescriptionLabel =tk.Label(master= self.controlPanelFrame, text="rpm min: ")
        self.valueMinLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.valueMaxDescriptionLabel =tk.Label(master= self.controlPanelFrame, text="rpm max: ")
        self.valueMaxLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.valueAbsoluteErrorDescriptionLabel =tk.Label(master= self.controlPanelFrame, text="rpm max absolute error: ")
        self.valueAbsoluteErrorLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.valueRelativeErrorDescriptionLabel =tk.Label(master= self.controlPanelFrame, text="rpm max relative error: ")
        self.valueRelativeErrorLabel = tk.Label(master=self.controlPanelFrame, text="0")
        self.readDescriptionLabel = tk.Label(master=self.controlPanelFrame, text="Raw read: ")
        self.readLabel = tk.Label(master=self.controlPanelFrame, text="Raw Read Input")
        self.separatorMid1 = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.separatorMid2 = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.setPidBtn = tk.Button(master=self.controlPanelFrame, text="Set PID", command=self.setPidValsBtnCallback)
        self.setRmpBtn = tk.Button(master=self.controlPanelFrame, text="Set RPM", command=self.setTargetRpmBtnCallback)
        self.startPidBtn = tk.Button(master=self.controlPanelFrame, text="Start", command=self.StartPIDBtnCallback)
        self.stopPidBtn = tk.Button(master=self.controlPanelFrame, text="Stop", command=self.StopPIDBtnCallback)
        self.changeMotDirBtn = tk.Button(master=self.controlPanelFrame, text="Change Motor Direction", command=self.changeMotDirBtnCallback)
        self.savePlotBtn = tk.Button(master=self.controlPanelFrame, text="Save plot", command=self.savePlotBtnCallback)
        self.setPercBtn = tk.Button(master=self.controlPanelFrame, text="Set speed", command=self.setPercBtnCallback)
        self.resetDevBtn = tk.Button(master=self.controlPanelFrame, text="Reset", command=self.resetReqBtnCallback)
        self.sendRmpLoopbackTestBtn = tk.Button(master=self.controlPanelFrame, text="Loopback Test", command=self.testRpmValLoopbackBtnCallback)
        self.quitBtn = tk.Button(master=self.controlPanelFrame, text="Quit", fg="black",command=self._quit)
        self.separatorBtn = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.separatorBtn0 = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.setServoBtn = tk.Button(master=self.controlPanelFrame, text="Set Servo", command=self.setServoBtnCallback)
        self.entryServo = tk.Entry(master=self.controlPanelFrame)
        self.separatorBtn1 = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.separatorBtn2 = ttk.Separator(master=self.controlPanelFrame, orient='horizontal')
        self.connectionStatus = tk.Label(master=self.controlPanelFrame, text="Connection Status: ")
        self.connectionStatusVal = tk.Label(master=self.controlPanelFrame, text="Not Connected")
        self.reconnectBtn = tk.Button(master=self.controlPanelFrame, text="Reconnect", command=self.reconnectReqBtnCallback)
        self.entryCOMName = tk.Entry(master=self.controlPanelFrame)

        self.entryPidkp.insert(-1, InitSettings.RegulatorConf.KP_INIT)
        self.entryPidki.insert(-1, InitSettings.RegulatorConf.KI_INIT)
        self.entryPidkd.insert(-1, InitSettings.RegulatorConf.KD_INIT)
        self.entryTargetRpm.insert(-1, InitSettings.RegulatorConf.RPM_INIT)
        self.entryPercentMotSpeed.insert(-1, InitSettings.RegulatorConf.BASIC_PERCENT_SPEED)
        self.entryCOMName.insert(-1, InitSettings.ConnectionConf.PORT_NAME)
        self.entryServo.insert(-1, InitSettings.RegulatorConf.SERVO_ANGLE)

        self.labelPidkp.grid(row=1, column=0, padx=(2), pady=2)
        self.entryPidkp.grid(row=2, column=0, padx=(2), pady=2)
        self.labelPidki.grid(row=1, column=1, padx=(2), pady=2)
        self.entryPidki.grid(row=2, column=1, padx=(2), pady=2)
        self.labelPidkd.grid(row=3, column=0, padx=(2), pady=2)
        self.entryPidkd.grid(row=4, column=0, padx=(2), pady=2)
        self.labelTargetRpm.grid(row=3, column=1, padx=(2), pady=2)
        self.entryTargetRpm.grid(row=4, column=1, padx=(2), pady=2)
        self.separatorTop.grid(row=5, column=1, padx=(2), pady=2, sticky="ew")
        self.separatorTop0.grid(row=5, column=0, padx=(2), pady=2, sticky="ew")
        self.labelMotorState.grid(row=6, column=1, padx=(2), pady=2)
        self.labelMotDir.grid(row=6, column=0, padx=(2), pady=2)
        self.labelValMotorState.grid(row=7, column=1, padx=(2), pady=2)
        self.labelMotDirVal.grid(row=7, column=0, padx=(2), pady=2)
        self.separatorMid.grid(row=8, column=1, padx=(2), pady=2, sticky="ew")
        self.separatorMid0.grid(row=8, column=0, padx=(2), pady=2, sticky="ew")
        self.valueDescriptionLabel.grid(row=9, column=0, padx=(2), pady=2)
        self.valueLabel.grid(row=9, column=1, padx=(2), pady=2)
        self.valueAvgDescriptionLabel.grid(row=10, column=0, padx=(2), pady=2)
        self.valueAvgLabel.grid(row=10, column=1, padx=(2), pady=2)
        self.valueStdDevDescriptionLabel.grid(row=11, column=0, padx=(2), pady=2)
        self.valueStdDevLabel.grid(row=11, column=1, padx=(2), pady=2)
        self.valueMedianDescriptionLabel.grid(row=12, column=0, padx=(2), pady=2)
        self.valueMedianLabel.grid(row=12, column=1, padx=(2), pady=2)
        self.valueModeDescriptionLabel.grid(row=13, column=0, padx=(2), pady=2)
        self.valueModeLabel.grid(row=13, column=1, padx=(2), pady=2)
        self.valueAmplitudeDescriptionLabel.grid(row=14, column=0, padx=(2), pady=2)
        self.valueAmplitudeLabel.grid(row=14, column=1, padx=(2), pady=2)
        self.valueMinDescriptionLabel.grid(row=15, column=0, padx=(2), pady=2)
        self.valueMinLabel.grid(row=15, column=1, padx=(2), pady=2)
        self.valueMaxDescriptionLabel.grid(row=16, column=0, padx=(2), pady=2)
        self.valueMaxLabel.grid(row=16, column=1, padx=(2), pady=2)
        self.valueAbsoluteErrorDescriptionLabel.grid(row=17, column=0, padx=(2), pady=2)
        self.valueAbsoluteErrorLabel.grid(row=17, column=1, padx=(2), pady=2)
        self.valueRelativeErrorDescriptionLabel.grid(row=18, column=0, padx=(2), pady=2)
        self.valueRelativeErrorLabel.grid(row=18, column=1, padx=(2), pady=2)
        self.separatorMid1.grid(row=19, column=1, padx=(2), pady=2, sticky="ew")
        self.separatorMid2.grid(row=19, column=0, padx=(2), pady=2, sticky="ew")
        self.setPidBtn.grid(row=20, column=0, padx=(2), pady=2, sticky="ew")
        self.setRmpBtn.grid(row=20, column=1, padx=(2), pady=2, sticky="ew")
        self.startPidBtn.grid(row=21, column=0, padx=(2), pady=2, sticky="ew")
        self.stopPidBtn.grid(row=21, column=1, padx=(2), pady=2, sticky="ew")
        self.changeMotDirBtn.grid(row=22, column=1, padx=(2), pady=2, sticky="ew")
        self.savePlotBtn.grid(row=22, column=0, padx=(2), pady=2, sticky="ew")
        self.resetDevBtn.grid(row=23, column=0, padx=(2), pady=2, sticky="ew")
        self.quitBtn.grid(row=23, column=1, padx=(2), pady=2, sticky="ew")
        self.separatorBtn.grid(row=24, column=0, padx=(2), pady=2, sticky="ew")
        self.separatorBtn0.grid(row=24, column=1, padx=(2), pady=2, sticky="ew")
        self.setPercBtn.grid(row=25, column=0, padx=(2), pady=2, sticky="ew")
        self.entryPercentMotSpeed.grid(row=25, column=1, padx=(2), pady=2)
        self.setServoBtn.grid(row=26, column=0, padx=(2), pady=2, sticky="ew")
        self.entryServo.grid(row=26, column=1, padx=(2), pady=2)
        self.separatorBtn1.grid(row=27, column=0, padx=(2), pady=2, sticky="ew")
        self.separatorBtn2.grid(row=27, column=1, padx=(2), pady=2, sticky="ew")
        self.connectionStatus.grid(row=28, column=0, padx=(2), pady=2, sticky="ew")
        self.connectionStatusVal.grid(row=28, column=1, padx=(2), pady=2, sticky="ew")
        self.reconnectBtn.grid(row=29, column=0, padx=(2), pady=2, sticky="ew")
        self.entryCOMName.grid(row=29, column=1, padx=(2), pady=2)
        
        #only for testing
        # self.readLabel.grid(row=10, column=0, padx=(2), pady=2)
        # self.readDescriptionLabel.grid(row=11, column=0, padx=(2), pady=2)
        # self.sendRmpLoopbackTestBtn.grid(row=12, column=0, padx=(2), pady=2)    



    #Button click event callbacks 
    def pressEnterCallback(self, event):
        self.setTargetRpmBtnCallback()
        time.sleep(0.001)
        self.setPidValsBtnCallback()

    def setPidValsBtnCallback(self):
        self.__mnr.setPidValsReq(float(self.entryPidkp.get()), float(
            self.entryPidki.get()), float(self.entryPidkd.get()))

    def setTargetRpmBtnCallback(self):
        self.__mnr.setTargetRpmValReq(abs(int(self.entryTargetRpm.get())))
        
    def setServoBtnCallback(self):
        self.__mnr.setServoAngleReq(abs(int(self.entryServo.get())))

    def StartPIDBtnCallback(self):
        self.__mnr.PidReq(PidState.ON)

    def StopPIDBtnCallback(self):
        self.__mnr.PidReq(PidState.OFF)
        
    def reconnectReqBtnCallback(self):
        self.__mnr.reconnectWithNewPort(self.entryCOMName.get())
    
    def setPercBtnCallback(self):
        self.__mnr.setPercentMotorSpeed(abs(int(self.entryPercentMotSpeed.get())))
    
    def changeMotDirBtnCallback(self):
        self.__mnr.motDirReq()
       
    # gui related btn callbacks
    def _quit(self):
        self.__logger.info("{0}::{1}: Appllication exits".format(self.__class__.__name__, self._quit.__name__))
        del self.__mnr
        self.root.quit()
        self.root.destroy()  
        
    def savePlotBtnCallback(self):
        plt.savefig('plot.png')  

    def resetReqBtnCallback(self):
        self.__mnr.resetDeviceReq()
        self.xar = deque([0])
        self.yar = deque([0])
        self.__dataCounetr = 0
        # self.entryPidkp.delete(0, 'end')
        # self.entryPidki.delete(0, 'end')
        # self.entryPidkd.delete(0, 'end')
        self.entryTargetRpm.delete(0, 'end')
        self.entryPercentMotSpeed.delete(0, 'end')
        self.entryCOMName.delete(0, 'end')
        self.entryServo.delete(0, 'end')
        # self.entryPidkp.insert(-1, InitSettings.RegulatorConf.KP_INIT)
        # self.entryPidki.insert(-1, InitSettings.RegulatorConf.KI_INIT)
        # self.entryPidkd.insert(-1, InitSettings.RegulatorConf.KD_INIT)
        self.entryTargetRpm.insert(-1, InitSettings.RegulatorConf.RPM_INIT)
        self.entryPercentMotSpeed.insert(-1, InitSettings.RegulatorConf.BASIC_PERCENT_SPEED)
        self.entryCOMName.insert(-1, InitSettings.ConnectionConf.PORT_NAME)
        self.entryServo.insert(-1, InitSettings.RegulatorConf.SERVO_ANGLE)
        self.labelMotDirVal.config(text='RIGHT')
        self.labelValMotorState.config(text='OFF')
        self.valueAvgLabel.config(text=0)
        self.valueStdDevLabel.config(text=0) 
        self.valueMedianLabel.config(text=0) 
        self.valueModeLabel.config(text=0) 
        self.valueAmplitudeLabel.config(text=0) 
        self.valueMinLabel.config(text=0) 
        self.valueMaxLabel.config(text=0) 
        self.valueAbsoluteErrorLabel.config(text=0)
        self.valueRelativeErrorLabel.config(text=0)    

    #only for testing
    def testRpmValLoopbackBtnCallback(self):
        self.__mnr.sendTestRpmLoopback(abs(int(self.entryTargetRpm.get())))


    #Animating plot methods
    def matplotCanvas(self):
        style.use('ggplot')
        self.fig = plt.figure(figsize=(14, 4.5), dpi=100)
        self.ax1 = self.fig.add_subplot(1, 1, 1)
        self.ax1.grid(b=True, which='major',color='#666666', linestyle='-')
        self.ax1.minorticks_on()
        self.ax1.grid(b=True, which='minor', color='#999999',linestyle='-', alpha=0.2)
        plt.xlabel("Time [s]")
        plt.ylabel("RPM")
        self.line, = self.ax1.plot(self.xar, self.yar)

    def animate(self, i):
        self.line.set_data(self.xar, self.yar)
        self.ax1.set_xlim(self.xar[0], self.xar[-1])
        self.ax1.set_ylim(min(self.yar)-0.1*min(self.yar),
                          max(self.yar)+0.1*max(self.yar))
     

    #Asynchronous serial read - periodic event
    def asyncRead(self):
        self.__mnr.handleRespMsg()
        self.__readJobId = self.root.after(2, self.asyncRead)
        
    def asyncReadCancel(self):
        if self.__readJobId != None:
            self.root.after_cancel(self.__readJobId) 
    
    
    #updates
    def updateMotorControlState(self, newState):
        if newState == MotorControlState.OFF:
            self.labelValMotorState.config(text='OFF')
        elif newState == MotorControlState.PID:
            self.labelValMotorState.config(text='PID')
        elif newState == MotorControlState.FREE_RUN:
            self.labelValMotorState.config(text='FREE RUN')
            
    def updateMotorDir(self, newDir):
        if newDir == MotorDir.RIGHT:
            self.labelMotDirVal.config(text='RIGHT')
        elif newDir == MotorDir.LEFT:
            self.labelMotDirVal.config(text='LEFT')
    
    def updateConnectionData(self, connectionState):
        if connectionState:
            if(self.connectionStatusVal.cget("text") == 'Not Connected'):
                self.connectionStatusVal.config(text='Connected')
        else:
            if(self.connectionStatusVal.cget("text") == 'Connected'):
                self.connectionStatusVal.config(text='Not Connected')   
    
    def updateStatistics(self, statisticsData):
        self.valueAvgLabel.config(text="{:.2f}".format(statisticsData.avgOfNSamples))
        self.valueStdDevLabel.config(text="{:.2f}".format(statisticsData.stdDev)) 
        self.valueMedianLabel.config(text=statisticsData.median) 
        self.valueModeLabel.config(text=statisticsData.mode) 
        self.valueAmplitudeLabel.config(text=statisticsData.amplitude) 
        self.valueMinLabel.config(text=statisticsData.minValue) 
        self.valueMaxLabel.config(text=statisticsData.maxValue) 
        self.valueAbsoluteErrorLabel.config(text=statisticsData.absoluteError)
        self.valueRelativeErrorLabel.config(text="{:.2f}".format(statisticsData.relativeError))          
     
    #adding new data to chart buffer          
    def handleNewData(self, val):
            self.valueLabel.config(text=val)
            self.__dataCounetr += InitSettings.RegulatorConf.RPM_MSG_INTERVALS_MS/1000
            self.yar.append(val)
            self.xar.append(self.__dataCounetr)
            while len(self.xar) > InitSettings.GuiConf.XAXEW :
                self.xar.popleft()
                self.yar.popleft()       



def main():
    logger = Logger()
    pyAppCore = Manager(logger)
    appGui = AppGui(pyAppCore, logger)

if __name__ == "__main__":
    main()
