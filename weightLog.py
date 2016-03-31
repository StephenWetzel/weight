import csv
import fileinput
import re
from time import strftime
import time
import os

from collections import deque
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

logFilename = "weight.log"
avgWindow = 10
debug = False #set this to true to avoid saving any data (graphs are still generated)
keys = ['date', 'time', 'timestamp', 'weightAvg', 'weight']

secsInDay   = 60 * 60 * 24 *  1
secsInWeek  = 60 * 60 * 24 *  7
secsInMonth = 60 * 60 * 24 * 30

#find average of all values in a queue
def queAvg(q):
	s = 0
	for item in q:
		s += item
	s /= len(q)
	return s

scriptPath = os.path.dirname(os.path.realpath(__file__)) + "/"
try: #open log and read data, or create an empty list
	with open(scriptPath + logFilename, 'rb') as inFile:
		reader = csv.DictReader(inFile, delimiter=';', quotechar='"')
		weightData = list(reader) #get the data into a list
except IOError:
	weightData = []

currentTime = strftime("%H:%M:%S")
currentDate = strftime("%Y-%m-%d")
unixTime = int(time.time())
earliestTimestamp = float("inf")
minWeight = float("inf")
maxWeight = -1

pointsInThisWeek = 0
curWeekNum = 0
sumThisWeek = 0
weekAvgs = []
weightQueue = deque() #a FIFO queue

#find the max and min weights
for row in weightData:
	if float(row['timestamp']) < earliestTimestamp:
		earliestTimestamp = float(row['timestamp'])
	thisWeight = float(row['weight'])
	if thisWeight > maxWeight:
		maxWeight = thisWeight
	if thisWeight < minWeight:
		minWeight = thisWeight

#ensure that there's enough data for two windows of avgWidnow length
if avgWindow * 2 > len(weightData):
	avgWindow = int(len(weightData) / 2)
	if avgWindow == 0:
		avgWindow = 1 #prevent divide by zero later

#find avg of last avgWindow number of entries
tempSum = 0
for row in weightData[-avgWindow:]:
	tempSum += float(row['weight'])
recentAvg = tempSum / avgWindow

#find avg of the previous avgWindow number of entries
tempSum = 0
for row in weightData[-avgWindow * 2:-avgWindow]:
	tempSum += float(row['weight'])
prevAvg = tempSum / avgWindow

#show user the averages and get the current weight
print "Previous average: " + str(round(prevAvg, 2))
print "Current average:  " + str(round(recentAvg, 2))
currentWeight = raw_input("Enter current weight: ")
currentWeight = float(currentWeight)
print ""
newRow = [{'date': currentDate, 'timestamp': unixTime, 'weight': currentWeight, 'time': currentTime, 'weightAvg': currentWeight}]
weightData += newRow


#find weekly averages
for row in weightData:
	thisWeight = float(row['weight'])
	thisWeekNum = int((unixTime - float(row['timestamp'])) / secsInWeek)
	
	#calc running average:
	weightQueue.append(thisWeight)
	if len(weightQueue) > avgWindow:
		weightQueue.popleft()
	runningAvg = queAvg(weightQueue)
	row['weightAvg'] = round(runningAvg, 1)
	
	#calc weekly averages:
	if thisWeekNum == curWeekNum:
		pointsInThisWeek += 1
		sumThisWeek += thisWeight
	else: #a new week
		try:
			weekAvgs.append(sumThisWeek / pointsInThisWeek)
		except ZeroDivisionError:
			pass
		#the first point in this new week is this point
		curWeekNum = thisWeekNum
		sumThisWeek = thisWeight
		pointsInThisWeek = 1

weekAvgs.append(sumThisWeek / pointsInThisWeek)

#calc, and display weekly deltas
for ii, thisWeek in enumerate(weekAvgs):
	try:
		delta = thisWeek - lastWeek 
	except NameError:
		delta = 0
	lastWeek = thisWeek
	print "Week #" + str(ii) + " Average: " + str(round(thisWeek, 2)) + ", delta: " + str(round(delta, 2))
print ""

#skip plotting if we don't have enough data points
if len(weightData) > 2:
	#create the pandas dataframe which is used for plotting
	weightFrame = pd.DataFrame(weightData)
	weightFrame.weight    = weightFrame.weight.astype(float)
	weightFrame.weightAvg = weightFrame.weightAvg.astype(float)
	weightFrame.timestamp = weightFrame.timestamp.astype(float)
	weightFrame["datetime"] = weightFrame.date + " " + weightFrame.time
	weightFrame.datetime = pd.to_datetime(weightFrame.datetime)
	
	#here we convert from unix timestamp to # of days since start of data:
	convertToDays = lambda x: (x - earliestTimestamp) / secsInDay
	weightFrame.timestamp = weightFrame.timestamp.apply(convertToDays)

	#plotting code
	plot = weightFrame.plot(x='datetime', y='weight', figsize=(16, 10)).get_figure()
	plot.savefig(scriptPath + "line.png")
	plot = sns.lmplot(x='timestamp', y='weight', data=weightFrame, size=8, aspect=2, lowess=True)
	plot.set_axis_labels("Day", "Weight")
	plot.set(xlim=(0, None))
	plot.savefig(scriptPath + "scatter.png")

	#plot running average
	from scipy.interpolate import spline
	smoothTime = np.linspace(weightFrame.timestamp.min(), weightFrame.timestamp.max(), 500)
	weightSmooth = spline(weightFrame.timestamp, weightFrame.weightAvg, smoothTime)
	plot = sns.lmplot(x='timestamp', y='weight', data=weightFrame, size=8, aspect=2, fit_reg=False)
	plot.set_axis_labels("Day", "Weight")
	plot.set(xlim=(0, None))
	plt.plot(smoothTime, weightSmooth, sns.xkcd_rgb["electric blue"], lw=1)
	plt.savefig(scriptPath + "smooth.png")

	if currentWeight < minWeight:
		print "Lowest weight ever!"
	if currentWeight > maxWeight:
		print "Highest weight ever!"

if debug:
	print "WARNING: Debug mode, data not saved!"
else: #write data to log
	with open(scriptPath + logFilename, 'w') as outFile:
		csvWriter = csv.DictWriter(outFile, keys, delimiter=';')
		csvWriter.writeheader()
		csvWriter.writerows(weightData)
	outFile.close()
