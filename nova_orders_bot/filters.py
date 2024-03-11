import datetime

def time_delta(date_object, hours):
    if hours >= 0:
        return date_object + datetime.timedelta(hours=int(hours))
    else:
        return date_object - datetime.timedelta(hours=int(hours)* -1)

def format_datetime(date_object):
    return date_object.strftime('%Y-%m-%d %H:%M:%S')