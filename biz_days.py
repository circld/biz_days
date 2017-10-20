"""Calculate what day is `n` business days from any date (exclusive of start
date), or calculate how many business days are between two dates (inclusive
of start and end dates).

Note: all dates should be in YYYY-MM-DD format.

Usage:
  biz_days.py days_from [-s START_DATE] -n DAYS [SKIP]...
  biz_days.py in_interval [-s START_DATE] -e END_DATE [SKIP]...

Options:
  -h --help                         show this docstring.
  -v --version                      show version.
  -n DAYS                           number of days to count.
  -s START_DATE --start=START_DATE  start date [default: today].
  -e END_DATE --end=END_DATE        end date.
  SKIP                              dates to exclude.

"""
from datetime import date, timedelta
from docopt import docopt
import sys


__all__ = ['business_days_from_now', 'business_days_interval', 'holiday_count',
           'str_to_date', 'weekdays']


def business_days_from_now(days, start=None, skip=None):
    """Calculates when `days` business days have occurred and returns that date.
    E.g., business_days_from_now(2, start=date(2017, 10, 17)) returns
    date(2017, 10, 19).

    Args:
        days (int): number of business days

    Kwargs:
        start (date): date from which to count
        skip (iterable): datetimes to skip

    Returns: date

    """
    if days == 0:
        return start

    skip = skip if skip else []
    sign = 1 if days > 0 else -1

    def iterate_days(current, remaining):
        cur = current + timedelta(days=sign*1)
        if cur.weekday() < 5 and cur not in skip:
            remaining -= sign*1
        if remaining == 0:
            return cur
        return iterate_days(current + timedelta(days=sign*1), remaining)

    return iterate_days(start, days)


def business_days_interval(start, end, skip=None):
    """Calculate number of business days between two dates.

    Args:
        start (date): start date
        end (date): end date

    Kwargs:
        skip (iterable): datetimes to skip

    Returns: int

    """
    if start > end:
        return 0

    wks = (end - start).days // 7

    holidays = holiday_count(start, end, skip) if skip else 0

    return max(wks*5 + weekdays(start.weekday(), end.weekday()) - holidays, 0)


def holiday_count(start, end, skip):
    """Count number of skip days are in within range [start, end].

    Args:
        start (date): start date
        end (date): end date
        skip (iterable): datetimes to skip

    Returns: int

    """
    skip = skip if skip else []
    non_weekend = (d for d in skip if d.weekday() < 5)
    return len([e for e in non_weekend if e >= start and e <= end])


def weekdays(dow1, dow2):
    """Week days between day of the week 1 and day of the week 2 (`dow2` > `dow1`)

    Args:
        dow1 (int): 0-6 for monday-sunday
        dow2 (int): 0-6 for monday-sunday

    Returns: int

    """
    if dow1 < 0 or dow1 > 6 or dow2 < 0 or dow2 > 6:
        raise ValueError
    if dow1 == dow2:
        return 1 if dow1 < 5 else 0
    d2 = dow2 if dow2 > dow1 else dow2 + 7

    return len(tuple(i for i in range(dow1, d2 + 1) if i not in (5, 6)))


def str_to_date(text):
    return date(*map(int, text.split('-')))


def main(args):

    days = int(args['-n']) if args['-n'] is not None else args['-n']
    start = date.today() if args['--start'] == 'today' else str_to_date(args['--start'])
    end = str_to_date(args['--end']) if args['--end'] is not None else None
    skip = tuple(str_to_date(d) for d in args['SKIP']) if args['SKIP'] is not None else args['SKIP']

    if args['days_from']:
        return business_days_from_now(days, start, skip).strftime('%Y-%m-%d')

    if args['in_interval']:
        return business_days_interval(start, end, skip)


if __name__ == '__main__':

    args = docopt(__doc__, version='0.1.0')
    sys.exit(print(main(args)))
