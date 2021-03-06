#!/usr/bin/env python3
# Name: Joseph Olivier
# This program is intended to look at .ATF files generated from square wave voltammograms and to
# generate an output that can easily be made into an excel graph
# Some values are hard-coded as of now, but please feel free to contact me at joolivie@ucsc.edu
# with anything you think that may need to be changed for your uses. I am not sure if you want a simple
# tkinter GUI attached to this program or not.
class GraphMaker:
	"""
	The original purpose of this function was to create graphs in matplotlib,
	however it is much easier to create a tsv file and to export it to excel to 
	do graphing. Therefore this function creates a tsv file which can easily be
	graphed in excel or other like program.

	INPUT: The list of lists from the data parser function which has all parsed data
	OUTPUT: A TSV file which gives the change in current values for each tested voltage
	For example, if the input voltages were -800,-600,-400,-200,0,200,400,600,800 (mV)
	the first two lines output file would look something like this: 
	1	1051.9843769686279	1023.2758923596649	960.8348415495606	831.5518589320315	660.3487158206442	562.6935891975849	447.51339597342377	480.07905855778637	
	2	995.3943493952252	895.5654380543199	911.7346887625691	886.3100403323323	679.2107930267973	525.6701067063249	398.6525050744588	363.62718368171267	
	Where the numers on the left correlate to the sample number and the values correlate to the change in current at the voltage specified to the user.
	In this case, 1051.... and 995... would correlate to the change in currents generated by subtracting the median current at the top of the -800 mV Square wave from the bottom
	of that square wave (-1000 mV)
	This tsv is pasted into excel by the user and is used to make graphs and correlations at their discretion
	"""
	
	def __init__(self,listofCurrents):
		self.masterList = listofCurrents

	def grapher(self):
		overallMax = -float('inf')
		overallMin = float('inf')
		numberOfFiles = len(self.masterList)

		outputList = []
		"""
		LOGIC:
		Goes through each file in the list of files.
		For each file, looks at the current values at the specified voltages
		Normalizes current to the nearest 200 (so if the current value is 198.2 pA at 198.2 mV normalize this value to 200 pA)
		Adds the normalized current to the output list [each line contains change in currents specific to one file]
		"""
		for h in range(0,len(self.masterList)):
			print(h)
			if h != 0:
				prevXVals = xVals
				prevYVals = yVals
			xVals = []
			yVals = []
			file = self.masterList[h]
			firstDerivativeY = [0]
			stepList = []
			
			for i in range(0,len(file)-1):

				tple = file[i]
				nextTple = file[i+1]
				#Normalize value due to step size
				#ASSUMES STEP SIZES of 200
				currentVal = file[i][2]*(200/abs(tple[1][1]-tple[0][1]))
				print(file[i][2],tple[1][1],tple[0][1],currentVal)
				stepList.append(currentVal)
				
				if i == len(file)-2:
					nextVal = nextTple[2]*(20/abs(nextTple[1][1]-nextTple[0][1]))
					stepList.append(nextVal)

			outputList.append(stepList)


		"""
		Following loop parses all data to CSV file.
		"""
		counter = 1
		import datetime
		file1 = open("processedData"+datetime.datetime.now().strftime('_%Y_%b_%d_%H_%M_%S')+".txt","w")
		for i in range(len(outputList)):
			currentCurrents = outputList[i]
			for j in range(len(currentCurrents)):
				if j == 0:
					print(counter,end="\t")
					file1.write(str(counter)+"\t")
				print(currentCurrents[j],end="\t")
				file1.write(str(currentCurrents[j])+"\t")
			counter+=1
			print("\n")
			file1.write("\n")
		file1.close()

class DataParser:
	"""
	This function looks at each ATF file and grabs the important data used for analysis.
	It looks at the top of the square wave, takes the median of those values, then looks at the bottom of the 
	square wave and takes the median of those values. The output is the difference in the median current values.
	INPUT: The list containing all ATF Files
	OUTPUT: A list of lists. Each list containing the difference in current from the top and bottom portion of the square wave
	at different applied voltages. 
	"""

	def __init__(self,listofFiles):
		self.masterList = listofFiles

	def parser(self,steps=9,PulseWidth=100,offset=1000):
		listofCurrents = []
		import sys

		#Iterates through all of the files that is in the currentWorkingDirectory/ATFFiles
		firstStart=1411
		for wholeFile in self.masterList:
			internalFileList = []
			#Assuming 9 steps, will change with GUI. 
			for i in range(0,steps-1):
				#Finds position of median in sorted list (depends on pulse width)
				median = int(PulseWidth/2)
				#Sorts the currents at the top of the square wave
				sortedbyCurrentTop = sorted(wholeFile[firstStart+offset*i:(firstStart+100)+offset*i],key=lambda current:current[1])
				#Sorts the currents at the bottom of the square wave
				sortedbyCurrentBottom = sorted(wholeFile[firstStart+offset*i+100:(firstStart+100)+offset*i+150],key=lambda current:current[1])
				differenceInStep = sortedbyCurrentTop[median][1] - sortedbyCurrentBottom[median][1]
				internalFileList.append((sortedbyCurrentTop[int(PulseWidth/2)][1:],sortedbyCurrentBottom[int(PulseWidth/2)][1:],differenceInStep))
			listofCurrents.append(internalFileList)
		GraphMaker(listofCurrents).grapher()

class FileReader:
	"""
	Function used to convert numerical values in .atf files from strings to floats
	input: ATF File
	output: ATF file with floats instead of strings
	"""
	def __init__(self,fileToRead):
		self.file = open(fileToRead)
	
	def reader(self):
		listofLines = []

		#Skip the header lines of the file
		for i in range(0,11):
			self.file.readline()

		#Convert all items to floats in file instead of strings.
		for line in self.file:
			line = line.strip().split()
			line[0] = float(line[0])
			line[1] = float(line[1])
			line[2] = float(line[2])
			listofLines.append(line)

		return listofLines

def main():
	"""
	Main function of the program which finds all of the ATF files and organizes them according to name
	INPUTS: None, but have all ATFFiles in a folder in the CWD

	intermediate step: Send each file to the FileReader function which changes all numerical values in
	.ATF file from str to floats.

	OUTPUTS: Sends the modified ATFFiles to the data parser function.
	"""
	import os

	#Location where the ATF files should be located (.../CWD/ATFFiles)
	refATFin = os.getcwd() + '/ATFFiles'
	FileList = []
	filenameList = []
	#Iterates through the ATF File folder and find all of the names of the ATF files.
	#Adds ATF file names to list, parses data using graphOutput Function.
	for dirname, dirnames, filenames in os.walk(refATFin):
		for filename in filenames:
			startfile = os.path.join(refATFin,filename)
			currentFile = FileReader(startfile).reader()
			FileList.append(currentFile)
			filenameList.append(filename)

	#Send list of files to dataParser
	DataParser(FileList).parser()
main()