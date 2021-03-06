import os
import sys
import ast
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
import pandas as pd
from pandas import DataFrame

PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

pathToStatistics = "/Users/Roman/Documents/testtest_result"
methodPrefix = "statistics"
typeOfData = "cross_sections"

mainTitleText = "Medaka's report"

args = ast.literal_eval(sys.argv[1])

print ', '.join(args.keys())

subTitleText = "Comparison of phenotypes form %s classes" % (', '.join(["'%s'" % k for k in args.keys()]))

metricsInfo = {
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
    'EquivEllipseAr': 'Equivalent Ellipse Area = (Pi*Feret*Breadth)/4, this is the area of an ellipse with the same long and short axes as the particle.',
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

def titlePage(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Bold',32)
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, mainTitleText)
    canvas.setFont('Times-Bold',16)
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-130, subTitleText)
    canvas.restoreState()

def regularPage(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "%d" % (doc.page))
    canvas.restoreState()

def createPlotWithCol(dataFrames, column, args, doc):
    fig = plt.figure(figsize=(10, 4))
    ax = fig.add_subplot(111)

    for fishClass, fishNames in args.items():
        for fishName in fishNames:
            dataFrames[fishName][column].plot(label=fishName)

    plt.legend(loc="upper right")
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

def readDataFrames(inputPath, fishClasses):
    dataFrames = {}
    cols = []

    for fishClass, fishNames in args.items():
        for fishName in fishNames:
            dataPath = os.path.join(inputPath, fishName)
            files = [f for f in os.listdir(dataPath) if os.path.isfile(os.path.join(dataPath,f)) and f.startswith(methodPrefix + '_' + typeOfData)]

            if files:
                dataFrames[fishName] = pd.read_csv(os.path.join(dataPath, files[0]), sep='\t')

            if not cols:
                cols = dataFrames[fishName].columns.tolist()

    return dataFrames, cols


doc = SimpleDocTemplate("test4.pdf")
style = styles["Normal"]
styleH1 = styles["Heading1"]
styleH2 = styles["Heading2"]

Story = [Spacer(1,2*inch)]

data, columns = readDataFrames(pathToStatistics, args)

for column in columns:
    currentColumn = column.strip()

    p = Paragraph(currentColumn, styleH1)
    Story.append(p)

    if currentColumn in metricsInfo:
        p = Paragraph(metricsInfo[currentColumn], style)
        Story.append(p)

    newPlot = createPlotWithCol(data, column, args, doc)
    Story.append(newPlot)

    Story.append(Spacer(1,0.2*inch))

doc.build(Story, onFirstPage=titlePage, onLaterPages=regularPage)
