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
    def __init__(self, _args, _statisticsDir, _outputPath, _mandatoryStats=['Area', 'Circularity', 'Volume', 'Surface', 'Width', 'Height', 'Length']):
        self.statisticsDir = _statisticsDir
        self.mandatoryStats = _mandatoryStats
        self.outputPath = _outputPath

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

    def generateSpreadsheet(data, column, output_path):
        with open(os.path.join(output_path,column + '.csv'), 'w', newline='') as fp:
            writer = csv.writer(fp, delimiter=';')

            if column == 'Volume' or column == 'Surface' or column == 'Width' or column == 'Height' or column == 'Length':
                writer.writerow([;column])

                for fish in data:
                    writer.writerow([fish.getLabel();fish.getDataByColumn(column)])

            else:
                n_data = len(fish.getDataByColumn(column))
                writer.writerow([fish.getLabel() for fish in data])

                for fish in data:
                    row = []
                    colData = fish.getDataByColumn(column)
                    
                    for i in range(n_data):
                        row.append()
                        writer.writerow([fish.getLabel() for fish in data])

    data = [['Me', 'You'],
            ['293', '219'],
            ['54', '13']]
    a.writerows(data)

    def generate(self):
        data = self.readFishData(self.statisticsDir, self.args)

        for column in self.mandatoryStats:
            currentColumn = column.strip()

            p = Paragraph(currentColumn, self.styleH1)
            self.story.append(p)

            if currentColumn in self.metricsInfo:
                p = Paragraph(self.metricsInfo[currentColumn], self.style)
                self.story.append(p)

            newPlot = self.createPlotWithCol(data, column, self.args, self.doc)
            self.story.append(newPlot)

            self.story.append(Spacer(1, 0.1 * inch))

        self.doc.build(self.story, onFirstPage=self.titlePage, onLaterPages=self.regularPage)

class FishReport:
    def __init__(self, _args, _statisticsDir, _methodPrefix='statistics',
            _mainTitle="Medaka's report", _docName="fish-report.pdf", _mandatoryStats=['Area']):
        self.statisticsDir = _statisticsDir
        self.methodPrefix = _methodPrefix
        self.pageWidth = defaultPageSize[0]
        self.pageHeight = defaultPageSize[1]
        self.styles = getSampleStyleSheet()
        self.args = ast.literal_eval(_args)
        self.mainTitle = _mainTitle
        self.voxelSize = [1, 1, 1]
        self.normalize = True
        self.subTitleText = "Comparison of phenotypes form %s classes" % (', '.join(["'%s'" % k for k in self.args.keys()]))
        self.metricsInfo = {
            'CSIndex': 'Index if the current cross-section.',
            'Slice': 'Slice number in the stack.',
            'Number': 'Blob number in the slice.',
            'XStart': 'The x coordinate of the first scanned point in the particle.',
            'YStart': 'The y coordinate of the first scanned point in the particle.',
            'Perim': 'The Perimeter, calculated from the centres of the boundary pixles.',
            'Area': 'The Area inside the polygon defined by the Perimeter.',
            'Pixels': 'The number of pixels forming the blob.',
            'XM': 'X coordinate of the centre of mass or momentum.',
            'YM': 'Y coordinate of the centre of mass or momentum.',
            'ROIX1': 'X coordinate of the top-left corner of the ROI that encloses the particle.',
            'ROIY1': 'Y coordinate of the top-left corner of the ROI that encloses the particle.',
            'ROIX2': 'X coordinate of the bottom-right corner of the ROI that encloses the particle.',
            'ROIY2': 'Y coordinate of the bottom-right corner of the ROI that encloses the particle.',
            'MinR': 'Radius of the inscribed circle centred at the centre of mass.',
            'MaxR': 'Radius of the enclosing circle centred at the centre of mass.',
            'Feret': 'Largest axis length.',
            'FeretX1': 'X coordinate of the first point of the Feret.',
            'FeretY1': 'Y coordinate of the first point of the Feret.',
            'FeretX2': 'X coordinate of the second point of the Feret.',
            'FeretY2': 'Y coordinate of the second point of the Feret.',
            'FAngle': 'Angle (in degrees) of the Feret with the horizontal (0..180).',
            'Breadth': 'The largest axis perpendicular to the Feret (not necessarily colinear).',
            'BrdthX1': 'X coordinate of the first Breadth point.',
            'BrdthY1': 'Y coordinate of the first Breadth point.',
            'BrdthX2': 'X coordinate of the second Breadth point.',
            'BrdthY2': 'Y coordinate of the second Breadth point.',
            'CHull': 'Convex Hull or convex polygon calculated from pixel centres. (This value is the same as the perimeter only for rectangular particles).',
            'CArea': 'Area of the Convex Hull polygon.',
            'MBCX': 'X coordinate of the Minimal Bounding Circle centre.',
            'MBCY': 'Y coordinate of the Minimal Bounding Circle centre.',
            'MBCRadius': 'Radius of the Minimal Bounding Circle.',
            'CountCorrect': 'This is a correction factor for unbiased counting of particles calculated as CountCorrect=XY/(X-Fx)(Y-Fy), where X and Y are the width and height of the ROI and Fx and Fy are the maximum projected dimensions of the object in the X and Y axes (this is Fx=1+ROIX2-ROIX1 and Fy=1+ROIY2-ROIY1 respectively). This correction factor should be applied with data generated with "exclude edge particles" checked.',
            'AspRatio': 'Aspect Ratio = Feret/Breadth.',
            'Circ': 'Circularity = 4*Pi*Area/Perimeter2, sometimes called Form Factor or Thinnes ratio. Note that the value is slightly different from that calculated using the built-in Particle Analyzer because of the way the particle area is estimated.',
            'Roundness': 'Roundness = 4*Area/(Pi*Feret2).',
            'AreaEquivD': 'Area Equivalent Diameter = sqrt((4/Pi)*Area).',
            'PerimEquivD': 'Perimeter Equivalent Diameter = Area/Pi.',
            'EquivEllAr': 'Equivalent Ellipse Area = (Pi*Feret*Breadth)/4, this is the area of an ellipse with the same long and short axes as the particle.',
            'Compactness': 'Compactness = sqrt((4/Pi)*Area)/Feret or alternatively ArEquivD/Feret.',
            'Solidity': 'Solidity = Area/Convex_Area.',
            'Concavity': 'Concavity = Convex_Area-Area.',
            'Convexity': 'Convexity = Convex_Hull/Perimeter.',
            'Shape': 'Shape = Perimeter2/Area.',
            'RFactor': 'RFactor = Convex_Hull /(Feret*Pi).',
            'ModRatio': 'Modification Ratio = (2*MinR)/Feret.',
            'Sphericity': 'Sphericity = MinR/MaxR.',
            'ArBBox': 'ArBBox = Feret*Breadth. This is the area of the Bounding Box along the Feret diameter, but it is not necessarily the minimal bounding box! (Search the net for "rotating calipers algorithm").',
            'Rectang': 'Rectangularity = Area/ArBBox. This approaches 0 for cross-like objects, 0.5 for squares, pi/4=0.79 for circles and approaches 1 for long rectangles.'
        }
        self.unitsInfo = {
            'Area': 'SliceArea/FishVol',
            'Volume': 'Volume',
            'Surface': 'Surface',
            'Width': 'Width',
            'Height': 'Height',
            'Length': 'Length',
            'Circularity': 'Circularity'
        }
        self.mandatoryStats = _mandatoryStats
        self.docName = _docName
        self.doc = SimpleDocTemplate(self.docName)
        self.style = self.styles["Normal"]
        self.styleH1 = self.styles["Heading1"]
        self.styleH2 = self.styles["Heading2"]
        self.story = [Spacer(1, 2 * inch)]

    def titlePage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold',32)
        canvas.drawCentredString(self.pageWidth / 2.0, self.pageHeight - 108, self.mainTitle)
        canvas.setFont('Times-Bold',16)
        canvas.drawCentredString(self.pageWidth / 2.0, self.pageHeight - 130, self.subTitleText)
        canvas.restoreState()

    def regularPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "%d" % (doc.page))
        canvas.restoreState()

    def createPlotWithCol(self, fishData, column, args, doc):
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        ax.set_position([0.1, 0.35, .85, .6])

        fishes_names = [i for i in itertools.chain.from_iterable(args.values())]
        colors = cmx.hsv(np.linspace(0, 1, len(fishes_names)))

        if column == 'Area' or column == 'Circularity':
            for fish, color in zip(fishData, colors):
                data = fish.getDataByColumn(column)

                data_len = len(data)
                x_perc = np.linspace(0, 100, data_len)

                print data

                ax.plot(x_perc, data, label=fish.getLabel(), color=color)

            x_axix_format = '%.0f%%'
            xticks = mtick.FormatStrFormatter(x_axix_format)
            ax.xaxis.set_major_formatter(xticks)
            ax.grid(True)

            plt.xlabel('Number of slice (%)', labelpad=5)
            plt.ylabel(self.unitsInfo[column])
            
            ax.legend(loc='center', bbox_to_anchor=(0.5, -0.35), ncol=6, prop={'size': 12})
        else:
            data = []
            labels = []

            for fish in fishData:
                data.append(fish.getDataByColumn(column))
                labels.append(fish.getLabel())

            n_labels = np.arange(len(labels))
            ax.bar(n_labels, data)
            plt.xlabel('Fishes')
            plt.ylabel(self.unitsInfo[column])
            plt.xticks(n_labels, labels)
            ax.legend(loc='center', bbox_to_anchor=(0.5, -0.35), ncol=6, prop={'size': 12})

        imgdata = BytesIO()
        fig.savefig(imgdata, format='png')
        imgdata.seek(0)
        img = Image(imgdata)
        img._restrictSize(doc.width, doc.height)

        return img

    '''
    def createPlotWithCol_old(self, dataFrames, column, args, doc):
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        ax.set_position([0.1, 0.35, .85, .6])

        fishes_names = [i for i in itertools.chain.from_iterable(args.values())]
        colors = cmx.hsv(np.linspace(0, 1, len(fishes_names)))

        if column == 'Area' or column == 'Circularity':
            for fishName, color in zip(fishes_names, colors):
                data_len = len(getDataByColumn(fishName, column, dataFrames))
                x_perc = np.linspace(0, 100, data_len)
                ax.plot(x_perc, getDataByColumn(fishName, column, dataFrames), label=fishName, color=color)

            x_axix_format = '%.0f%%'
            xticks = mtick.FormatStrFormatter(x_axix_format)
            ax.xaxis.set_major_formatter(xticks)
            ax.grid(True)

            plt.xlabel('Number of slice (%)', labelpad=5)
            plt.ylabel(self.unitsInfo[column])
            
            ax.legend(loc='center', bbox_to_anchor=(0.5, -0.35), ncol=6, prop={'size': 12})

        elif:
            for fishName in fishes_names:
                ax.bar()

        imgdata = BytesIO()
        fig.savefig(imgdata, format='png')
        imgdata.seek(0)
        img = Image(imgdata)
        img._restrictSize(doc.width, doc.height)

        return img
    '''
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
                    
                    #dataFrame = pd.read_csv(os.path.join(dataPath, files[0]), sep=';')

                    #print dataFrame['Area']

                    #if totalVolumeSize and self.normalize:
                    #    dataFrame = dataFrame['Area'].div(totalVolumeSize)

                    fishEntry = FishData(fishName, fishClass, totalVolumeSize, totalSurfaceSize, totalVolumeLength, os.path.join(dataPath, files[0]))
                    fishesData.append(fishEntry)

        return fishesData

    '''
    def readFishData_old(self, inputPath, fishClasses):
        dataFrames = {}
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
                    
                    dataFrames[fishName] = pd.read_csv(os.path.join(dataPath, files[0]), sep=';')

                    if totalVolumeSize:
                        dataFrames[fishName]['Volume'] = 
                        dataFrames[fishName] = dataFrames[fishName].div(totalVolumeSize)

                    if totalSurfaceSize:


                if not cols:
                    cols = dataFrames[fishName].columns.tolist()

        return dataFrames, cols
    '''

    def generate(self):
        data = self.readFishData(self.statisticsDir, self.args)

        for column in self.mandatoryStats:
            currentColumn = column.strip()

            p = Paragraph(currentColumn, self.styleH1)
            self.story.append(p)

            if currentColumn in self.metricsInfo:
                p = Paragraph(self.metricsInfo[currentColumn], self.style)
                self.story.append(p)

            newPlot = self.createPlotWithCol(data, column, self.args, self.doc)
            self.story.append(newPlot)

            self.story.append(Spacer(1, 0.1 * inch))

        self.doc.build(self.story, onFirstPage=self.titlePage, onLaterPages=self.regularPage)

    '''
    def generate_old(self):
        data, columns = self.readFishData(self.statisticsDir, self.args)

        for column in self.mandatoryStats:
            currentColumn = column.strip()

            p = Paragraph(currentColumn, self.styleH1)
            self.story.append(p)

            if currentColumn in self.metricsInfo:
                p = Paragraph(self.metricsInfo[currentColumn], self.style)
                self.story.append(p)

            newPlot = self.createPlotWithCol(data, column, self.args, self.doc)
            self.story.append(newPlot)

            self.story.append(Spacer(1, 0.1 * inch))

        self.doc.build(self.story, onFirstPage=self.titlePage, onLaterPages=self.regularPage)
    '''
def main(args):
    fishReport = FishReport(args, '/Users/rshkarin/Documents/fish-report-generator/Results')
    fishReport.generate()

if __name__ == '__main__':
    #args = "{'Wild':['fish200','fish202','fish204','fish214','fish215','fish221','fish223','fish224','fish226','fish228','fish230','fish231','fish233','fish235','fish236','fish237','fish238','fish239','fish243','fish244','fish245']}"
    args = "{'Wild':['fish200','fish202','fish204','fish214','fish215','fish221','fish223','fish224']}"
    main(args)
    #main(sys.argv[1])

