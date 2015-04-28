import os
import sys
import ast
import matplotlib.pyplot as plt
import numpy as np
import itertools
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import matplotlib.ticker as mtick

import pandas as pd
from pandas import DataFrame

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
            'Area': 'SliceVol/FishVol'
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


    def createPlotWithCol(self, dataFrames, column, args, doc):
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        #ax.set_position([0.1, 0.1, .85, .85])
        ax.set_position([0.1, 0.35, .85, .6])

        fishes_names = [i for i in itertools.chain.from_iterable(args.values())]
        colors = cmx.hsv(np.linspace(0, 1, len(fishes_names)))

        for fishName, color in zip(fishes_names, colors):
            data_len = len(dataFrames[fishName][column])
            x_perc = np.linspace(0, 100, data_len)
            ax.plot(x_perc, dataFrames[fishName][column], label=fishName, color=color)

        x_axix_format = '%.0f%%'
        xticks = mtick.FormatStrFormatter(x_axix_format)
        ax.xaxis.set_major_formatter(xticks)
        ax.grid(True)
        #fig.tight_layout()

        plt.xlabel('Number of slice (%)', labelpad=5)
        plt.ylabel(self.unitsInfo[column])
        
        ax.legend(loc='center', bbox_to_anchor=(0.5, -0.35), ncol=6, prop={'size': 12})

        imgdata = BytesIO()
        fig.savefig(imgdata, format='png')
        imgdata.seek(0)
        img = Image(imgdata)
        img._restrictSize(doc.width, doc.height)

        return img

    def createPlotWithCol2(self, dataFrames, column, args, doc):
        fig = plt.figure(figsize=(10, 4))
        ax = fig.add_subplot(111)

        nfishes = 0
        for fishClass, fishNames in args.items():
            nfishes = nfishes + len(fishNames)

        cmap = self.get_cmap(nfishes)

        i_color = 0
        for fishClass, fishNames in args.items():
            for fishName in fishNames:
                ax = dataFrames[fishName][column].plot(ax=ax, label=fishName, color=cmap(i_color))
                i_color = i_color + 1

        plt.legend(loc='center left')
        plt.xlabel('Number of slice (%)')
        plt.ylabel('Units')
        plt.grid(True)
        plt.tight_layout()

        imgdata = BytesIO()
        fig.savefig(imgdata, format='png')
        imgdata.seek(0)
        img = Image(imgdata)
        img._restrictSize(doc.width, doc.height*0.3)

        return img

    def readDataFrames(self, inputPath, fishClasses):
        dataFrames = {}
        cols = []
        totalVolumeSize = 0.

        for fishClass, fishNames in self.args.items():
            for fishName in fishNames:
                dataPath = os.path.join(inputPath, fishName)
                files = [f for f in os.listdir(dataPath) if os.path.isfile(os.path.join(dataPath,f)) and f.startswith(self.methodPrefix)]

                if files:
                    name_comps = files[0].split('_')

                    if float(name_comps[1]):
                        totalVolumeSize = float(name_comps[1])
                    
                    dataFrames[fishName] = pd.read_csv(os.path.join(dataPath, files[0]), sep=';')

                    if totalVolumeSize:
                        dataFrames[fishName] = dataFrames[fishName].div(totalVolumeSize)

                if not cols:
                    cols = dataFrames[fishName].columns.tolist()

        return dataFrames, cols

    def generate(self):
        data, columns = self.readDataFrames(self.statisticsDir, self.args)

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

def main(args):
    fishReport = FishReport(args, 'E:\Report generator\Results')
    fishReport.generate()

if __name__ == '__main__':
    args = "{'Wild':['fish200','fish202','fish204','fish214','fish215','fish221','fish223','fish224','fish226','fish228','fish230','fish231','fish233','fish235','fish236','fish237','fish238','fish239','fish243','fish244','fish245']}"
    main(args)
    #main(sys.argv[1])

