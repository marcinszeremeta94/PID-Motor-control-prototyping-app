import csv

class CsvHandler:
    
    __logger = None
    __xValue = 0
    __csvWriter = None
    __fieldnames = ["ms", "rpm"]

    def __init__(self, logger):
        self.__logger = logger
        with open('data.csv', 'w') as csv_file:
            self.__csvWriter = csv.DictWriter(csv_file, fieldnames=self.__fieldnames)
            self.__csvWriter.writeheader()

    def writeNewData(self, newData):
        with open('data.csv', 'a') as csv_file:
            self.__csvWriter = csv.DictWriter(csv_file, fieldnames=self.__fieldnames)
            info = {
                "ms": self.__xValue,
                "rpm": newData,
            }
            self.__csvWriter.writerow(info)
            self.__xValue += 40
            self.__logger.debug("{0}::{1}: Mesured value saved to csv"
                    .format(self.__class__.__name__, self.writeNewData.__name__))  


# main
def main():
    csvHandler = CsvHandler()
    csvHandler.writeNewData(0)
    
if __name__ == "__main__":
    main()
    