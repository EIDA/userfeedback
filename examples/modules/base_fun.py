#base functions module
import json,re

def directory_names(event):
  year_dir = str(event.origins[0].time.year)+'/'
  event_dir = re.sub('\d{2}\.\d{2,8}','',format_date(event.origins[0].time))
  return year_dir, event_dir

def format_date(date):
  strdate = \
    date.isoformat()\
        .replace('-','')\
        .replace(':','')\
        .replace('T','')
  return strdate

def read_json(path):
  with open(path, 'r') as file:
    return json.load(file)

def write_json(data, path):
  with open(path, 'w') as file:
   json.dump(data, file, indent=4)
