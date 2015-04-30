import os
import sys
import ast
import matplotlib.pyplot as plt
import numpy as np
import itertools
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import matplotlib.ticker as mtick
import csv

import pandas as pd
from pandas import DataFrame

class FishData:
    def __init__(self, _label=None, _class=None, _volume=0, _surface=0, _length=0, _area=[], _perim=[], _width=[], _height=[], _normalize=True):
        self.volume = _volume
        self.surface = _surface
        self.length = _length
        self.label = _label
        self.fclass = _class
        self.area = _area
        self.perim = _perim
        self.width = _width
        self.height = _height

        if _normalize and self.volume:
            self.area = self.area / self.volume

    def getVolume(self):
        return self.volume

    def getSurface(self):
        return self.surface

    def getLength(self):
        return self.length

    def getWidth(self):
        return self.width.max()

    def getHeight(self):
        return self.height.max()

    def getCircularity(self):
        return 2.0*np.sqrt(self.area) / self.perim

    def getArea(self):
        return self.area

    def getLabel(self):
        return self.label

    def getDataByColumn(self, column):
        if column == 'Volume':
            return self.getVolume()
        elif column == 'Surface':
            return self.getSurface()
        elif column == 'Length':
            return self.getLength()
        elif column == 'Width':
            return self.getWidth()
        elif column == 'Height':
            return self.getHeight()
        elif column == 'Circularity':
            return self.getCircularity()
        elif column == 'Area':
            return self.getArea()
        else:
            return None

class FishDataConcatenator:
    def __init__(self, _args, _statisticsDir, _outputPath, _methodPrefix='statistics', _mandatoryStats=['Area', 'Circularity', 'Volume', 'Surface', 'Width', 'Height', 'Length']):
        self.statisticsDir = _statisticsDir
        self.mandatoryStats = _mandatoryStats
        self.outputPath = _outputPath
        self.args = ast.literal_eval(_args)
        self.methodPrefix = _methodPrefix

    def readFishData(self, inputPath, fishClasses):
        fishesData = []
        cols = []

        totalVolumeSize = 0.
        totalSurfaceSize = 0.
        totalVolumeLength = 0

        for fishClass, fishNames in self.args.items():
            for fishName in fishNames:
                dataPath = os.path.join(inputPath, fishName)
                files = [f for f in os.listdir(dataPath) if os.path.isfile(os.path.join(dataPath,f)) and f.startswith(self.methodPrefix)]

                if files:
                    name_comps = files[0].split('_')

                    if float(name_comps[1]):
                        totalVolumeSize = float(name_comps[1])

                    if float(name_comps[2]):
                        totalSurfaceSize = float(name_comps[2])

                    if float(name_comps[3][1:]) and float(name_comps[4][1:]):
                        totalVolumeLength = float(name_comps[4][1:]) - float(name_comps[3][1:])
                    
                    dataFrame = pd.read_csv(os.path.join(dataPath, files[0]), sep=';')

                    area = np.array(dataFrame['Area'], dtype=float)
                    perim = np.array(dataFrame['Perim.'], dtype=float)
                    width = np.array(dataFrame['Width'], dtype=float)
                    height = np.array(dataFrame['Height'], dtype=float)

                    fishEntry = FishData(fishName, fishClass, totalVolumeSize, totalSurfaceSize, totalVolumeLength, area, perim, width, height)
                    fishesData.append(fishEntry)

        return fishesData

    def generateSpreadsheet(self, data, column):
        with open(os.path.join(self.outputPath, column + '.csv'), 'wb') as fp:
            writer = csv.writer(fp, delimiter=';')

            if column == 'Volume' or column == 'Surface' or column == 'Width' or column == 'Height' or column == 'Length':
                writer.writerow([' ',column])

                for fish in data:
                    writer.writerow([fish.getLabel(),fish.getDataByColumn(column)])

            else:
                n_data = len(data[0].getDataByColumn(column))

                writer.writerow([fish.getLabel() for fish in data])

                for i in range(n_data):
                    writer.writerow([fish.getDataByColumn(column)[i] for fish in data])

    def generateSpreadsheets(self):
        data = self.readFishData(self.statisticsDir, self.args)

        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)

        for column in self.mandatoryStats:
            self.generateSpreadsheet(data, column)

def main(args):
    dataConcatenator = FishDataConcatenator(args, 'E:\Report generator\Results', 'E:\Report generator\Spreadsheets')
    dataConcatenator.generateSpreadsheets()

if __name__ == '__main__':
    args = "{'Wild':['fish200','fish202','fish204','fish214','fish215','fish221','fish223','fish224','fish226','fish228','fish230','fish231','fish233','fish235','fish236','fish237','fish238','fish239','fish243','fish244','fish245']}"
    main(args)
    #main(sys.argv[1])

