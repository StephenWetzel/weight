import csv
import fileinput
import re
from datetime import datetime, timedelta
import time
import os
import math
import statistics

log_filename = 'weight_two.tsv'
daily_log_filename = 'weight_two_daily.tsv'
height = 72 # height in inches
debug = False # Don't write data to file
MOVING_AVG_COUNT = 14
MAX_DELTA = 5 # Maximum weight change allowed before we ask to confirm
script_path = os.path.dirname(os.path.realpath(__file__)) + "/"

# calc BMI from weight
def calculate_bmi(weight):
  return round(weight * 703 / height / height, 2)  # http://www.cdc.gov/healthyweight/assessing/bmi/adult_bmi/

def read_log_file():
  try: # open log and read data, or create an empty list
    with open(script_path + log_filename, 'r') as in_file:
      reader = csv.DictReader(in_file, delimiter='\t', quotechar='"')
      weight_rows = list(reader) # get the data into a list
  except IOError:
    weight_rows = []
  return weight_rows

def save_records(weight_rows, daily_weights):
  if debug:
    print("\n *** WARNING: Debug mode, data not saved! ***\n\n")
  else: # write data to log
    with open(script_path + log_filename, 'w') as out_file:
      csv_writer = csv.DictWriter(out_file, weight_rows[0].keys(), delimiter='\t')
      csv_writer.writeheader()
      csv_writer.writerows(weight_rows)
    out_file.close()
    with open(script_path + daily_log_filename, 'w') as out_file:
      csv_writer = csv.writer(out_file, delimiter='\t')
      csv_writer.writerow(['date', 'weight'])
      for key, value in daily_weights.items():
        csv_writer.writerow([key, value])
    out_file.close()

def get_current_weight(weight_rows):
  current_weight = float(input("Enter current weight: "))
  if current_weight == 0:
    return False
  if len(weight_rows) > 1 and abs(float(weight_rows[-1]['weight']) - float(current_weight)) > MAX_DELTA:
    print("Are you sure?")
    time.sleep(0.5)
    current_weight = float(input("Re-enter current weight: "))
  print('')
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

def median(l):
  return round(statistics.median(l), 2)

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
  daily_weights = {}

  for weight_row in weight_rows:
    moving_avg_weights.append(float(weight_row['weight']))
    if len(moving_avg_weights) > MOVING_AVG_COUNT: moving_avg_weights.pop(0)
    weight_row['mean_weight'] = mean(moving_avg_weights)
    weight_row['median_weight'] = median(moving_avg_weights)
    row_date_time = datetime.strptime(weight_row['date_time'], '%Y-%m-%d %H:%M:%S')
    first_of_week = get_first_of_week(row_date_time)
    first_of_month = get_first_of_month(row_date_time)

    if first_of_week != current_week:
      week_buckets.append({
        'week': current_week,
        'mean': mean(week_weights),
        'delta': mean(week_weights) - week_buckets[-1]['mean'] if len(week_buckets) > 0 else 0,
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
          'delta': mean(month_weights) - month_buckets[-1]['mean'] if len(month_buckets) > 0 else 0,
          'mean_bmi': calculate_bmi(mean(month_weights)),
          'min': min(month_weights),
          'min_bmi': calculate_bmi(min(month_weights)),
          'count': len(month_weights)
        })
      month_weights = []
      current_month = first_of_month
    month_weights.append(float(weight_row['weight']))

    if float(weight_row['weight']) < daily_weights.get(row_date_time.date(), math.inf): daily_weights[row_date_time.date()] = float(weight_row['weight'])
  week_buckets.append({
    'week': current_week,
    'mean': mean(week_weights),
    'delta': mean(week_weights) - week_buckets[-1]['mean'] if len(week_buckets) > 0 else 0,
    'mean_bmi': calculate_bmi(mean(week_weights)),
    'min': min(week_weights),
    'min_bmi': calculate_bmi(min(week_weights)),
    'count': len(week_weights)
  })
  month_buckets.append({
    'month': current_month,
    'mean': mean(month_weights),
    'delta': mean(month_weights) - month_buckets[-1]['mean'] if len(month_buckets) > 0 else 0,
    'mean_bmi': calculate_bmi(mean(month_weights)),
    'min': min(month_weights),
    'min_bmi': calculate_bmi(min(month_weights)),
    'count': len(month_weights)
  })
  return daily_weights, week_buckets, month_buckets

def display_records(records):
  print('')
  if records['most_recent_lower'] is None:
    print("Highest weight ever!")
  else:
    age = get_age_of_date(records['most_recent_lower']['date'])
    if age > 10: print("Highest weight in {0} ({1})".format(pretty_age(age), records['most_recent_lower']['date']))

  if records['most_recent_higher'] is None:
    print("Lowest weight ever!")
  else:
    age = get_age_of_date(records['most_recent_higher']['date'])
    if age > 10: print("Lowest weight in {0} ({1})".format(pretty_age(age), records['most_recent_higher']['date']))

def display_weeks(week_buckets):
  print('{:>8}{:>9}{:>8}{:>10}{:>9}{:>9}{:>7}'.format('Week', 'Mean', 'Delta', 'Mean BMI', 'Min', 'Min BMI', 'Count'))
  for ii, week in enumerate(week_buckets[-14:]):
    print('{:%b %d}  {:9.2f}{:+8.2f}{:10.2f}{:9.1f}{:9.2f}{:7d}'.format(week['week'], week['mean'], week['delta'], week['mean_bmi'], week['min'], week['min_bmi'], week['count']))

def display_months(month_buckets):
  print("{:>8}{:>9}{:>8}{:>10}{:>9}{:>9}{:>7}".format('Month', 'Mean', 'Delta', 'Mean BMI', 'Min', 'Min BMI', 'Count'))
  for ii, month in enumerate(month_buckets):
    print("{:%Y %b}{:9.2f}{:+8.2f}{:10.2f}{:9.1f}{:9.2f}{:7d}".format(month['month'], month['mean'], month['delta'], month['mean_bmi'], month['min'], month['min_bmi'], month['count']))


def display_current_stats(month_buckets):
  most_recent_row = weight_rows[-1]
  print("Current weight: {}, BMI: {:5.3f} @ {}".format(most_recent_row['weight'], calculate_bmi(float(most_recent_row['weight'])), most_recent_row['date_time']))

weight_rows = read_log_file()
current_weight = get_current_weight(weight_rows)
if current_weight:
  weight_rows.append(current_weight)
records = find_records(weight_rows)
daily_weights, week_buckets, month_buckets = bucket_days(weight_rows)
display_months(month_buckets)
display_weeks(week_buckets)
display_current_stats(month_buckets)
display_records(records)

save_records(weight_rows, daily_weights)
