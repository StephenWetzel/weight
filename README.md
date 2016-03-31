Two quick programs I made to help me keep track of my weight and eating.

# weightLog.py

Run this script to log you weight.  Weigh yourself, then run the script, and it'll ask for you current weight.  Then it'll show you some averages and create some graphs.

Uses pandas, numpy, matplotlib, and seaborn for plotting.

One bug I'm aware of is that if you enter a weight very close to the previous weight (less than an hour), the smooth.png graph will show a huge swining motion.


# serving.py

This script I made to help keep track of the serving for things that aren't individually wrapped.  Run the script, it'll ask for a name, then the calories per serving, and the size of the serving (in grams or anything else, as long as you are consistent), and then the starting weight.  Then it'll loop asking you for the ending weight.  You eat some food, and weigh it, and enter that, and it'll tell you how much you've eaten so far.  It'll end when you enter 0 as the ending weight, but I just use Ctrl+C.

```markdown
Enter name: cheese
Enter calories per serving: 110
Enter the serving size: 28
Enter the starting weight: 457
Enter the ending weight: 412
That is 1.61 servings, for a total of 176.79 calories.
Enter the ending weight: 364
That is 3.32 servings, for a total of 365.36 calories.
Enter the ending weight: 327
That is 4.64 servings, for a total of 510.71 calories.
Enter the ending weight: 289
That is 6.0 servings, for a total of 660.0 calories.
```

# parseCalories.py

This script will parse the calories from the food diary report from myfitnesspal.com.  To get the report, go to: FOOD > Food Diary > View Full Report (Printable).  Then change the date range to the full range you want.  Save that file to your computer, and run this script in the same directory.  Currently it only gets the calorie totals, and I don't care about the other stuff.  It also ignores excercise, as I don't really log that.  I may change both of those things in the future.

I started out trying to parse the HTML with BeautifulSoup, but was having trouble with malformed HTML, so I just went with regex.