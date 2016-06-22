import json
import time
import os
from datetime import datetime

servingFileName = 'servingData.json'

scriptPath = os.path.dirname(os.path.realpath(__file__)) + "/"

try:
	with open(scriptPath + servingFileName, 'r') as iFile:
		data = json.load(iFile)
except (IOError, ValueError): #file does not exist, so create an empty foods obj
	data = json.loads('{"foods": []}')

name = raw_input("Enter name (type 'list' to show stored foods): ")

while name == "list":
	for ii, food in enumerate(data['foods']):
		print "Name: " + str(food['name']) + " (" + str(food['calories']) + " cal)"

	name = raw_input("Enter name (type 'list' to show stored foods): ")

#check to see if that food has been entered in the past
for ii, food in enumerate(data['foods']):
	if name == food['name']:
		caloriesPerServing = food['calories']
		servingSize        = food['serving']
		createdTime        = food['created']
		lastUsedTime       = food['used']
		foodIndex          = ii
		break

try: #try to display the found info to user
	print "Calories Per Serving: " + str(caloriesPerServing)
	print "Serving Size: " + str(servingSize)
	print "Created Time: " + datetime.fromtimestamp(createdTime).strftime('%Y-%m-%d %H:%M:%S')
	print "Last Used:    " + datetime.fromtimestamp(lastUsedTime).strftime('%Y-%m-%d %H:%M:%S')
except NameError: #we didn't find this food before, so we need the data from the user
	foodIndex = len(data['foods']) #this is a new food, so it'll be at the end
	data['foods'].append({}) #append the empty obj to be populated later
	createdTime = int(time.time())
	while True: #loop until we get valid data from user
		try:
			caloriesPerServing = float(raw_input("Enter calories per serving: "))
			servingSize = float(raw_input("Enter the serving size: "))
			break #if there hasn't been an exception then we have valid data
		except ValueError:
			print "Invalid data, try again"

while True: #we always need the starting weight
	try:
		startWeight = float(raw_input("Enter the starting weight (enter 0 to edit data): "))
		if startWeight == 0:
			while True: #loop until we get valid data from user
				try:
					caloriesPerServing = float(raw_input("Enter calories per serving: "))
					servingSize = float(raw_input("Enter the serving size: "))
					break #if there hasn't been an exception then we have valid data
				except ValueError:
					print "Invalid data, try again"
		if startWeight > 0:
			break #if there hasn't been an exception then we have valid data
	except ValueError:
		print "Invalid data, try again"

#save data
data['foods'][foodIndex]['name']     = name
data['foods'][foodIndex]['calories'] = caloriesPerServing
data['foods'][foodIndex]['serving']  = servingSize
data['foods'][foodIndex]['created']  = createdTime
data['foods'][foodIndex]['used']     = int(time.time())

with open(scriptPath + servingFileName, 'w+') as oFile:
	json.dump(data, oFile, indent=2)

endWeight = 1
while endWeight != 0:
	endWeight = float(raw_input("Enter the ending weight: "))
	deltaWeight = startWeight - endWeight
	numServings = deltaWeight / servingSize
	totalCalories = caloriesPerServing * numServings
	print "That is " + str(round(numServings,2)) + " servings, for a total of " + str(round(totalCalories,2)) + " calories."

