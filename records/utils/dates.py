import datetime
from collections import OrderedDict
from records.models import Schedule


def get_dates_between(start_date, end_date, delta_days=7):
    # returns list of dates between two provided dates
    dates = []
    while start_date < end_date:
        dates.append(start_date)
        start_date += datetime.timedelta(days=delta_days)
    return dates


def dates_diff(new_dates, old_dates):
    # returns differences between two dates lists
    # Note: returned lists are not sorted
    new_dates = set(new_dates)
    old_dates = set(old_dates)
    to_create = list(new_dates - old_dates)
    to_delete = list(old_dates - new_dates)
    return to_create, to_delete


def get_week_dates(date=None):
    # returns dates of whole week containing provided date or Today()
    # if none provided
    if not date:
        date = datetime.date.today()
    date_weekday = date.weekday()
    dates = [date + datetime.timedelta(days=x)
             for x in range(0-date_weekday, 7-date_weekday)]
    return dates


def get_weekday_names(dates):
    # returns OrderedDict with date as key and name of the day as value
    # for provided dates
    days = OrderedDict()
    for date in dates:
        weekday = date.weekday()
        name = Schedule.DAYS_OF_WEEK[weekday][1]
        days[date] = name
    return days
