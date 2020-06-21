import datetime
import json

# Utility Functions
def get_todays_date():
    today = datetime.date.today()
    today = str(today).replace('-', '_')
    return today

def get_todays_month():
    today = datetime.date.today()
    return today.month

def get_todays_year():
    today = datetime.date.today()
    return today.year

def save_record_to_json(file_path, record):
    with open(file_path, "w") as f:
        json.dump(record, f)