#!/usr/bin/env python3
# Name: Joseph Olivier
# The purpose of this script is to analyze SWV files from 
# chips for the Italian Trip.

class PeakFinder():
	"""
	The purpose of this class is to find the beginning of the
	peak and to calculate the area under the curve as well as 
	to find the voltage where the peak starts and finishes in
	order to compare these values to the buffer (blank) solutions.
	"""
	def __init__(self,processedFile):
		self.fileMin = processedFile[1]
		self.endofPeak = processedFile[0].index(self.fileMin)
		self.currentFile = processedFile[0][0:self.endofPeak+1]

	def classController(self):
		#calls methods in order.
		startToEnd = self.lineReader()
		startToEnd.append(self.fileMin)
		areaUnderTheCurve = self.findArea(startToEnd)
		startToEnd.append(areaUnderTheCurve)

		return startToEnd

	def lineReader(self):
		"""
		This will read the file backwards. It will start at the end
		of the peak by looking at the position of the fileMin. It
		will record all of the values from the start to the end of the
		peak and will stop when all 3 "conditions" are met. 
		"""

		import sys
		# Condition 1: We find the top portion of the peak.
		# We do this by finding the first "flat surface" by
		# looking at the difference between adjacent points.
		# If there are 3 or more points next to each other with
		# less than a 10% difference this condition now becomes true.
		# We will then save the location of the top of the peak as topEnds
		condition1 = False
		condition1Counter = 0
		topEnds = []
		
		# Condition 2: We find where the top of the peak descends down
		# and to the left. We do this by checking to see if there are 3
		# consecutive points where the difference is greater than 10% of
		# the maximum value between the two points (ie, if point 1 is 10,
		# and point 2 is 15: the difference is 5, and 5 > 0.1(15))
		# We will save the location of the this as topBegins
		condition2 = False
		condition2Counter = 0
		topBegins = []
		
		# Condition 3: This is where the curve begins sharply rising
		# and I define this as the begining of the peak, and it will
		# be where we dictate the area under the curve and record
		# the "start" to be used for standard curves.
		# We will save this location as peakStarts
		condition3 = False
		condition3Counter = 0
		peakStarts = []

		# The first "previousLine" is the bottom of the dip
		# The subsequent for loop starts at the next line.
		previousLine = self.currentFile[::-1][0]
		for line in self.currentFile[::-1][1:]:
			
			if not condition1:
				# First, we check if condition 1 has been satisfied.
				# If not, we will continue searching for the top of the peak
				# Once Condition 1 has been satisfied, we move onto the next
				# segment.
				if abs(previousLine[1]-line[1]) < 0.1*max(previousLine[1],line[1]):
					if condition1Counter == 0:
						topEnds = previousLine
						condition1Counter+=1
					else:
						condition1Counter+=1

				if condition1Counter > 2:
					condition1 = True

			elif not condition2:
				# Here, we check if condition2 is satisfied which occurs
				# when the graph starts dipping down and to the left sharply
				# at the left side of the peak.
				# if not condition2:
				if abs(previousLine[1]-line[1]) > 0.1*max(previousLine[1],line[1]):
					if condition2Counter == 0:
						topBegins = previousLine
						condition2Counter = 1
					else:
						condition2Counter+=1

				if condition2Counter > 2:
					condition2 = True
			elif not condition3:
				# Here, we check when condition3 is satisfied. This
				# occurs when we reach the far left of the peak where 
				# values start to increase up and to the left.
				if line[1] > previousLine[1]:
					if condition3Counter == 0:
						peakStarts = previousLine
						condition3Counter = 1
					else:
						condition3Counter+=1
				
				if condition3Counter > 2:
					condition3 = True

			previousLine = line

		return [peakStarts,topBegins,topEnds]

	def findArea(self,values):
		"""
		This function finds the area under the peak by
		looking at all values in the range of the peak.
		It will look at each consecutive point and calculate
		the area between each point. If a value dips below 0
		(which may occur at the ends), then it will change the 
		value to 0 as to not add a negative area. This can be 
		changed later if we find value in the negative area.
		"""

		#Initializing variabesl. PreviousValue is the first point, and
		#the loops starts at the point after this.
		peakStart = self.currentFile.index(values[0])
		previousValue = self.currentFile[peakStart]	
		currentArea = float(0)

		for value in self.currentFile[peakStart+1:]:
			#Reduces a value to 0 if it is below 0 (may occur
			#at end of peak on either side).
			if previousValue[1] < 0:
				previousValue[1] = 0
			elif value[1] < 0:
				value[1] = 0
			#Area under the curve calculations. Again, it is the
			#triangle formed between two points + the area of the
			#rectangle below the formed triangle..
			horizontalDistance = abs(value[0]-previousValue[0])
			verticalDistance = abs(value[1]-previousValue[1])
			triangleArea = 1/2*horizontalDistance*verticalDistance
			rectangleArea = min(value[1],previousValue[1])*horizontalDistance
			currentArea+=triangleArea+rectangleArea

		return currentArea



class FileReader():
	"""
	The purpose of this class is to read in a file and to 
	make a list of the file line by line. It will convert
	each of the values from strings to floats and will truncate
	the data to only show the applied voltage values and the 
	square wave values (it takes out forward and reverse current
	values). In addition, it will do the first step of the data
	processing by finding the end of the peak (the file min).
	These values will be passed as a tuple back to the main 
	function to be read fed into the PeakFinder class.
	"""
	def __init__(self,currentFile):
		self.file = open(currentFile)

	def reader(self):
		import sys
		
		
		previousLine = []
		fileMin = ["inf",float("inf")]
		listofLines = []
		
		# This will separate the lines in the file by values.
		# Line[0] will be the applied voltage
		# Line[1] will be the resultant square wave current (Forward - Reverse Current)
		for line in self.file:
			line = line.rstrip("\n").split("\t")[0:2]

			lineAppliedVoltage = float(line[0])
			lineCurrent = float(line[1])

			if len(previousLine) > 0:
				# This finds the minimum in the entire graph.
				# NOTICEABLE PATTERN: The min occurs at the end
				# of the peak. Therefore, we will use this value
				# to figure out where to start looking.
				if lineCurrent < fileMin[1]:
					fileMin = [lineAppliedVoltage,lineCurrent]
				previousLine = [lineAppliedVoltage,lineCurrent]

			else:
				previousLine = [lineAppliedVoltage,lineCurrent]
			listofLines.append(previousLine)

		return (listofLines,fileMin)



def main():
	import os
	import sys
	fileListDir = os.getcwd() + "/CurrentBatch" 
	listofFiles = []
	masterList = []

	#os.walk will go into the hardcoded directory file name and will print out:
	# the full path (target directory), the directories within the target directory
	# (nestedDirectories) and a list of all of the files in the target directory
	# (fileList). This loop will initialize these values.
	for targetDirectory,nestedDirectories,filenames in os.walk(fileListDir):
		# This inner loop will take all of the files in the target directory
		# (hard coded as current batch within the current working directory)
		# and will append the full path names to the files making a list of 
		# full path files called listofFiles.
		for file in filenames:
			listofFiles.append(os.path.join(fileListDir,file))
	
	for filepath in listofFiles:
		originalLines = FileReader(filepath).reader()
		processedData = PeakFinder(originalLines).classController()
		
		#Data munging to create a list of lists
		addtoMaster = [x for x in processedData]
		addtoMaster.insert(0,os.path.basename(filepath))
		masterList.append(addtoMaster)

	#Data munging to create excel file
	for file in masterList:
		counter = 0
		for line in file:
			if counter == 1:
				print("Peak Begins:",end="\t")
			elif counter == 2:
				print("Start of Peak Top:",end="\t")
			elif counter == 3:
				print("End of Peak Top:",end="\t")
			elif counter == 4:
				print("End of Peak:",end="\t")
			elif counter == 5:
				print("Area Under the Curve:",end="\t")
			if counter > 0 and counter < 5:
				for value in line:
					print(value,end="\t")
				print("")
			else:
				print(line)
				if counter == 5:
					print("Width of Peak:",end="\t")
					print(file[4][0]-file[1][0])
					print("")

			counter+=1

if __name__ == "__main__":
	main()
