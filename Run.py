from AppGui import AppGui
from Manager import Manager
from Logger import Logger
from Logger import LogsSeverity
from Logger import PrintOption

def Run():
    logger = Logger(LogsSeverity.Regular, PrintOption.NoPrints)
    appCore = Manager(logger)
    appGui = AppGui(appCore, logger)

#Application main
if __name__ == "__main__":
    print("Application started")
    Run()
    print("Application exits")
