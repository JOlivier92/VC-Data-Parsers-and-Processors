#!/usr/bin/env python3
# Name: Joseph Olivier
# longSquareWave.py
# The purpose of this script is to take in a CV (in the form of a .txt file) from the
# CHI and to convert it into a 6-7 point graph where it take the difference between values which are 
# 200 mV apart.
# Input: *.txt file that is a cyclic voltammagram from the CHI machine
# Output: *.txt file which gives 6 points, Delta current over a range of 200 mVs
class CalculatePseudoSquareWave:
	def __init__(self,IVValues):
		self.currentVoltageValues = IVValues
		self.rectificationValues = []
		self.topBottom = []

	def controller(self):
		import sys
		self.rectificationCalculator()
		self.topMinusBottom()

		return [self.rectificationValues,self.topBottom]

	def rectificationCalculator(self):
		import sys
		i = 0
		for IV in self.currentVoltageValues[0:int(len(self.currentVoltageValues)/2)]:
			self.rectificationValues.append([IV[0],IV[1]/self.currentVoltageValues[-i+1][1]])
			i+=1

	def topMinusBottom(self):
		import sys
		previousIV = self.currentVoltageValues[0]
		curentIV = []
		for IV in self.currentVoltageValues[1:]:
			currentIV = IV
			self.topBottom.append([currentIV[0],currentIV[1]-previousIV[1]])
			previousIV = IV





class FileReader:
	def __init__(self,file):
		self.file = open(file)
		self.output = []

	def reader(self):
		import sys
		for line in self.file:
			startingPoint = 1000*-float(line.lstrip().rstrip().split()[0])
			voltage = float(line.lstrip().rstrip().split()[0])
			current = float(line.lstrip().rstrip().split()[1])
			self.output.append([voltage,current])
			break
		i=0
		for line in self.file:
			if i > startingPoint*2-2:
				break
			voltage = float(line.lstrip().rstrip().split()[0])
			current = float(line.lstrip().rstrip().split()[1])
			#if voltage not in self.output:
			self.output.append([voltage,current])
			i+=1
			#else:
				#return self.output
		return self.output




def main():
	import os
	import sys
	import datetime
	import timeit
	start = timeit.default_timer()
	FileList = []
	outputRectification = []
	outputTopBottom = []
	
	#Location where the ATF files should be located (.../CWD/ATFFiles)
	refCHIin = os.getcwd() + '/CHIFiles'
	#Location where the output directory will be located (.../CWD/graphs_current_date_to_second)
	#graphOutput = os.getcwd() + '/' + 'CHIOutput' + datetime.datetime.now().strftime('_%Y_%b_%d_%H_%M_%S')
	#Creates output directory in current working directory
	#os.makedirs(graphOutput,0o777)
	
	#Iterates through the ATF File folder and find all of the names of the ATF files.
	#Adds ATF file names to list, parses data using graphOutput Function.
	for dirname, dirnames, filenames in os.walk(refCHIin):
		for filename in filenames:
			startfile = os.path.join(refCHIin,filename)
			print(startfile)
			#Convert all of the numerical items from strings to floats in current f ile
			currentFile = FileReader(startfile).reader()
			#Add fille to list of all Files
			FileList.append(currentFile)
	
	#Send list of files to dataParser
	for file in FileList:
		x,y = CalculatePseudoSquareWave(file).controller()
		outputRectification.append(x)
		outputTopBottom.append(y)
	
	end = timeit.default_timer()
	print(end-start)
	return outputRectification,outputTopBottom


def scanRectificationToCSV(listofRectified):
	import os
	import datetime
	import sys
	file1 = open("squareWaves"+datetime.datetime.now().strftime('_%Y_%b_%d_%H_%M_%S')+".txt","w")
	for experiment in listofSquareWaves:
		for i in range(len(experiment)):
			print(experiment[i][0],experiment[i][1])
			file1.write(str(experiment[i][0])+"\t"+str(experiment[i][1]))
			file1.write("\n")
		
	file1.close()

def scanSquareWaveToCSV(listofSquareWaves):
	import os
	import datetime
	import sys
	file1 = open("squareWaves"+datetime.datetime.now().strftime('_%Y_%b_%d_%H_%M_%S')+".txt","w")

	for experiment in listofSquareWaves:
		for i in range(len(experiment)):
			print(experiment[i][0],experiment[i][1])
			file1.write(str(experiment[i][0])+"\t"+str(experiment[i][1]))
			file1.write("\n")

	file1.close()

	pass


x,y = main()
scanSquareWaveToCSV(y)









