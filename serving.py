name = raw_input("Enter name: ")
while True: #loop until we get valid data from user
	try:
		caloriesPerServing = float(raw_input("Enter calories per serving: "))
		servingSize = float(raw_input("Enter the serving size: "))
		startWeight = float(raw_input("Enter the starting weight: "))
		break #if there hasn't been an exception then we have valid data
	except ValueError:
		print "Invalid data, try again"

endWeight = 1
while endWeight != 0:
	endWeight = float(raw_input("Enter the ending weight: "))
	deltaWeight = startWeight - endWeight
	numServings = deltaWeight / servingSize
	totalCalories = caloriesPerServing * numServings
	print "That is " + str(round(numServings,2)) + " servings, for a total of " + str(round(totalCalories,2)) + " calories."

