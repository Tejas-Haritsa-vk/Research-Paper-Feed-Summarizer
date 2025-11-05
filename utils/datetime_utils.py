from datetime import datetime, timezone, timedelta

def format_datetime_to_python(datetime_string):
    return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def get_datetimedelta(timedeltaindays):
    return datetime.now(timezone.utc) - timedelta(days=timedeltaindays)
