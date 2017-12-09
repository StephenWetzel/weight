import csv
import fileinput
import re
from datetime import datetime, timedelta
import os

log_filename = 'weight_two.tsv'
height = 72 # height in inches
debug = False # Don't write data to file
MOVING_AVG_COUNT = 10
script_path = os.path.dirname(os.path.realpath(__file__)) + "/"

# calc BMI from weight
def calculate_bmi(weight):
  return round(weight * 703 / height / height, 2)  # http://www.cdc.gov/healthyweight/assessing/bmi/adult_bmi/

def read_log_file():
  try: # open log and read data, or create an empty list
    with open(script_path + log_filename, 'rb') as in_file:
      reader = csv.DictReader(in_file, delimiter='\t', quotechar='"')
      weight_rows = list(reader) # get the data into a list
  except IOError:
    weight_rows = []
  return weight_rows

def save_records(weight_rows):
  if debug:
    print "WARNING: Debug mode, data not saved!"
  else: # write data to log
    with open(script_path + log_filename, 'w') as out_file:
      csv_writer = csv.DictWriter(out_file, weight_rows[0].keys(), delimiter='\t')
      csv_writer.writeheader()
      csv_writer.writerows(weight_rows)
    out_file.close()

def get_current_weight():
  current_weight = float(raw_input("Enter current weight: "))
  print ""
  new_row = {
    'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'weight': current_weight,
    'bmi': calculate_bmi(current_weight)
  }
  return new_row

def find_records(weight_rows):
  most_recent_higher = None
  most_recent_lower  = None
  current_weight = float(weight_rows[-1]['weight'])
  for weight_row in reversed(weight_rows[:-1]):
    if current_weight < float(weight_row['weight']) and most_recent_lower is None:
      most_recent_lower = {'date': weight_row['date_time'], 'weight': weight_row['weight']}
    if current_weight > float(weight_row['weight']) and most_recent_higher is None:
      most_recent_higher = {'date': weight_row['date_time'], 'weight': weight_row['weight']}
    if most_recent_higher is not None and most_recent_lower is not None: break
  return {'most_recent_lower': most_recent_lower, 'most_recent_higher': most_recent_higher}

def get_age_of_date(date_str):
  old_date_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
  current_date_time = datetime.now()
  age = current_date_time - old_date_time
  return age.days

def pretty_age(days):
  if days > 365:
    return "{0} years".format(round(days / 365.0, 2))
  elif days > 30:
    return "{0} months".format(round(days / 30.0, 2))
  else:
    return "{0} days".format(round(days / 1.0, 2))


def get_first_of_week(dt):
  return dt.date() - timedelta(days=dt.date().weekday())

def get_first_of_month(dt):
  return dt.date() - timedelta(days=dt.date().day - 1)

def mean(l):
  return round(sum(l) / len(l), 2)

def min(l):
  if len(l) > 3:
    return sorted(l)[1]
  else:
    return sorted(l)[0]

def bucket_days(weight_rows):
  moving_avg_weights = []
  week_buckets = []
  week_weights = []
  current_week = get_first_of_week(datetime.strptime(weight_rows[0]['date_time'], '%Y-%m-%d %H:%M:%S'))
  month_buckets = []
  month_weights = []
  current_month = get_first_of_week(datetime.strptime(weight_rows[0]['date_time'], '%Y-%m-%d %H:%M:%S'))

  for weight_row in weight_rows:
    moving_avg_weights.append(float(weight_row['weight']))
    weight_row['avg_weight'] = mean(moving_avg_weights)
    if len(moving_avg_weights) > MOVING_AVG_COUNT: moving_avg_weights.pop(0)
    row_date_time = datetime.strptime(weight_row['date_time'], '%Y-%m-%d %H:%M:%S')
    first_of_week = get_first_of_week(row_date_time)
    first_of_month = get_first_of_month(row_date_time)

    if first_of_week != current_week:
      week_buckets.append({
        'week': current_week,
        'mean': mean(week_weights),
        'mean_bmi': calculate_bmi(mean(week_weights)),
        'min': min(week_weights),
        'min_bmi': calculate_bmi(min(week_weights)),
        'count': len(week_weights)
      })
      week_weights = []
      current_week = first_of_week
    week_weights.append(float(weight_row['weight']))

    if first_of_month != current_month:
      if len(month_weights) > 0:
        month_buckets.append({
          'month': current_month,
          'mean': mean(month_weights),
          'mean_bmi': calculate_bmi(mean(month_weights)),
          'min': min(month_weights),
          'min_bmi': calculate_bmi(min(month_weights)),
          'count': len(month_weights)
        })
      month_weights = []
      current_month = first_of_month
    month_weights.append(float(weight_row['weight']))
  week_buckets.append({
    'week': current_week,
    'mean': mean(week_weights),
    'mean_bmi': calculate_bmi(mean(week_weights)),
    'min': min(week_weights),
    'min_bmi': calculate_bmi(min(week_weights)),
    'count': len(week_weights)
  })
  month_buckets.append({
    'month': current_month,
    'mean': mean(month_weights),
    'mean_bmi': calculate_bmi(mean(month_weights)),
    'min': min(month_weights),
    'min_bmi': calculate_bmi(min(month_weights)),
    'count': len(month_weights)
  })
  return week_buckets, month_buckets

def display_records(records):
  print ""
  if records['most_recent_lower'] is None:
    print "Highest weight ever!"
  else:
    age = get_age_of_date(records['most_recent_lower']['date'])
    if age > 10: print "Highest weight in {0} ({1})".format(pretty_age(age), records['most_recent_lower']['date'])

  if records['most_recent_higher'] is None:
    print "Lowest weight ever!"
  else:
    age = get_age_of_date(records['most_recent_higher']['date'])
    if age > 10: print "Lowest weight in {0} ({1})".format(pretty_age(age), records['most_recent_higher']['date'])

def display_weeks(week_buckets):
  print "{0}\t\t{1}\t{2}\t{3}\t{4}\t{5}".format('Week', 'Mean', 'Mean BMI', 'Min', 'Min BMI', 'Count')
  for week in week_buckets[-10:]:
    print "{0}\t{1}\t{2}\t\t{3}\t{4}\t{5}".format(week['week'], week['mean'], week['mean_bmi'], week['min'], week['min_bmi'], week['count'])

def display_months(month_buckets):
  print "{0}\t\t{1}\t{2}\t{3}\t{4}\t{5}".format('Month', 'Mean', 'Mean BMI', 'Min', 'Min BMI', 'Count')
  for month in month_buckets:
    print "{0}\t{1}\t{2}\t\t{3}\t{4}\t{5}".format(month['month'], month['mean'], month['mean_bmi'], month['min'], month['min_bmi'], month['count'])


weight_rows = read_log_file()
weight_rows.append(get_current_weight())
records = find_records(weight_rows)
week_buckets, month_buckets = bucket_days(weight_rows)

display_months(month_buckets)
display_weeks(week_buckets)
display_records(records)

save_records(weight_rows)