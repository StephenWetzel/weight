import re
import os
from datetime import datetime


calorieReportFilename = "cal.html"
calorieLogFilename    = "cal.log"

dataMode = False

scriptPath = os.path.dirname(os.path.realpath(__file__)) + "/"
with open(scriptPath + calorieLogFilename, 'w') as outFile:
	outFile.write("date;calories\n")
	with open(scriptPath + calorieReportFilename, 'rb') as inFile:
		for line in inFile:
			match = re.search('id="date">(.+)</h2>', line)
			if match:
				dateStr = match.group(1)
				#February 5, 2016
				dateObj = datetime.strptime(dateStr, '%B %d, %Y')
				print dateObj
			match = re.search('<td class="first">TOTAL:</td>', line)
			if match:
				dataMode = True
			if dataMode:
				match = re.search('<td>(.+)</td>', line)
				if match:
					calories = match.group(1)
					calories = re.sub('[\D]', '', calories)
					dataMode = False
					outFile.write(str(dateObj) + ";" + calories + "\n")
