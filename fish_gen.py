import os
import sys
import csv
import operator
import numpy as np

class FishMaker:
	def __init__(self, _fishNumbers=[], _statColumns=[], _fishPrefix='fish', _numSlices=50, _sigma=5.5, _mu=10):
		if _fishNumbers:
			self.fishNumbers = _fishNumbers
		else:
			self.fishNumbers = [202, 205, 214, 220, 221, 235, 238, 240, 252, 253, 254, 266]

		if _statColumns:
			self.statColumns = _statColumns
		else:
			self.statColumns = [' CSIndex ', ' XStart ', ' YStart ', ' Perim ', ' Area ', ' Pixels ', ' XM ', ' YM ', ' ROIX1 ', ' ROIY1 ', ' ROIX2 ', ' ROIY2 ', ' MinR ', ' MaxR ', ' Feret ', ' FeretX1 ', ' FeretY1 ', ' FeretX2 ', ' FeretY2 ', ' FAngle ', ' Breadth ', ' BrdthX1 ', ' BrdthY1 ', ' BrdthX2 ', ' BrdthY2 ', ' CHull ', ' CArea ', ' MBCX ', ' MBCY ', ' MBCRadius ', ' CountCorrect ', ' AspRatio ', ' Circ ', ' Roundness ', ' ArEquivD ',  ' PerEquivD ', ' EquivEllAr ', ' Compactness ', ' Solidity ', ' Concavity ', ' Convexity ', ' Shape ', ' RFactor ', ' ModRatio ', ' Sphericity ', ' ArBBox ', ' Rectang ']

		self.numSlices = _numSlices
		self.sigma = _sigma
		self.mu = _mu
		self.fishPrefix = _fishPrefix

	def generate_csv(self, outputDir):
		for fishNumber in self.fishNumbers:
			outputPath = os.path.join(outputDir, self.fishPrefix + str(fishNumber))
			if not os.path.exists(outputPath):
				os.makedirs(outputPath)

			outputFile = "statistics_cross_sections_%s%s_8bit_129x256x256.csv" % (self.fishPrefix, str(fishNumber))

			scv_file = csv.writer(open(os.path.join(outputPath, outputFile), "w"), delimiter='\t', quoting=csv.QUOTE_ALL)

			print "%s is generating..." % os.path.join(outputPath, outputFile)

			scv_file.writerow(self.statColumns)
			
			for sliceIdx in range(self.numSlices):
				for statIdx in range(len(self.statColumns)):
					scv_file.writerow(reduce(operator.add, [[statIdx], [self.sigma * np.random.randn() + self.mu for _ in range(len(self.statColumns) - 1)]]))

def main():
	fishMaker = FishMaker()
	fishMaker.generate_csv('/Users/Roman/Documents/testtest_result')

if __name__ == '__main__':
	main()




