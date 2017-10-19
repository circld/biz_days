import biz_days
from biz_days import business_days_from_now, business_days_interval,  \
    holiday_count, main, str_to_date, weekdays
from datetime import date
from docopt import docopt, DocoptExit
import hypothesis as h
import hypothesis.strategies as st
import pytest as pt


@st.composite
def list_of_dates(draw):
    return draw(st.iterables(st.dates(), min_size=1, max_size=100))


@st.composite
def days_from_cli_args(draw):
    return [
        'days_from',
        '-s', draw(st.dates()).strftime('%Y-%m-%d'),
        '-n', draw(st.integers(min_value=-500, max_value=500))
    ], draw(st.builds(
        lambda e: list(map(lambda d: d.strftime('%Y-%m-%d'), e)),
        st.lists(st.dates(), min_size=1, max_size=100))
    )


@st.composite
def in_between_cli_args(draw):
    return [
        'in_interval',
        '-s', draw(st.dates()).strftime('%Y-%m-%d'),
        '-e', draw(st.dates()).strftime('%Y-%m-%d')
    ], draw(st.builds(
        lambda e: list(map(lambda d: d.strftime('%Y-%m-%d'), e)),
        st.lists(st.dates(), min_size=1, max_size=100))
    )


@h.given(days=st.integers(min_value=-500, max_value=500), start=st.dates(),
         skip=list_of_dates())
def test_business_days_from_now_general(days, start, skip):
    if days >= 0:
        assert business_days_from_now(days, start, skip) >= start
    else:
        assert business_days_from_now(days, start, skip) <= start
    if not (start.weekday() >= 5 and days == 0):
        assert (business_days_from_now(days, start, skip)).weekday() < 5


def test_business_days_from_now_specific_cases():
    assert business_days_from_now(-5, date(2000, 1, 1)) == date(1999, 12, 27)
    assert business_days_from_now(0, date(2000, 1, 1)) == date(2000, 1, 1)
    assert business_days_from_now(1, date(2017, 1, 1)) == date(2017, 1, 2)
    assert business_days_from_now(1, date(2017, 1, 3)) == date(2017, 1, 4)


@h.given(start=st.dates(), end=st.dates(), skip=list_of_dates())
def test_business_days_interval_general(start, end, skip):
    biz_days = business_days_interval(start, end, skip)
    assert biz_days >= 0


def test_business_days_interval_specific_cases_no_skips():
    assert business_days_interval(date(2000, 1, 1), date(2000, 1, 2)) == 0
    assert business_days_interval(date(2016, 1, 1), date(2015, 1, 2)) == 0
    assert business_days_interval(date(2016, 12, 31), date(2017, 1, 14)) == 10
    assert business_days_interval(date(2016, 12, 31), date(2017, 1, 15)) == 10
    assert business_days_interval(date(2016, 12, 31), date(2017, 1, 16)) == 11


def test_business_days_interval_specific_cases_with_skips():
    """Should skip weekday holidays only, if provided"""
    assert business_days_interval(
        date(2000, 1, 1), date(2000, 1, 2), []
    ) == 0
    assert business_days_interval(
        date(2016, 1, 1), date(2015, 1, 2), [date(2016, 1, 1)]
    ) == 0
    assert business_days_interval(
        date(2016, 12, 31), date(2017, 1, 14), [date(2017, 1, 1)]
    ) == 10
    assert business_days_interval(
        date(2016, 12, 31), date(2017, 1, 14), [date(2017, 1, 3)]
    ) == 9
    assert business_days_interval(
        date(2016, 12, 31), date(2017, 1, 15), [date(2017, 1, 3), date(2017, 1, 5)]
    ) == 8


@h.given(dow1=st.integers(), dow2=st.integers())
def test_weekdays_general_cases(dow1, dow2):
    if (0 <= dow1 <= 6) and (0 <= dow2 <= 6):
        assert 7 >= weekdays(dow1, dow2) >= 0
    else:
        with pt.raises(ValueError):
            weekdays(dow1, dow2)


def test_weekdays_specific_cases():
    assert weekdays(0, 6) == 5
    assert weekdays(6, 0) == 1
    assert weekdays(5, 0) == 1
    assert weekdays(1, 4) == 4
    assert weekdays(5, 6) == 0
    assert weekdays(4, 3) == 5
    assert weekdays(5, 5) == 0


@h.given(start=st.dates(), end=st.dates(), skip=list_of_dates())
def test_holiday_count_general_cases(start, end, skip):
    assert holiday_count(start, end, skip) >= 0


def test_holiday_count_specific_cases():
    assert holiday_count(date(2015, 1, 1), date(2017, 1, 1), [date(2018, 1, 1)]) == 0
    assert holiday_count(date(2015, 1, 1), date(2017, 1, 1), [date(2017, 1, 1)]) == 0
    assert holiday_count(date(2015, 1, 1), date(2017, 1, 1), [date(2016, 12, 30)]) == 1
    assert holiday_count(date(2015, 1, 1), date(2017, 1, 1), (date(2016, 12, 30),)) == 1
    assert holiday_count(date(2015, 1, 1), date(2017, 1, 1),
                         [date(2016, 12, 30), date(2019, 1, 1)]) == 1
    assert holiday_count(date(2015, 1, 1), date(2017, 1, 1),
                         [date(2016, 12, 30), date(2016, 12, 1)]) == 2


@h.given(d=st.dates())
def test_str_to_date(d):
    assert str_to_date(d.strftime('%Y-%m-%d')) == d


def test_cli_implementation_in_interval():
    doc = biz_days.__doc__
    args = docopt(doc, ['in_interval', '-s', '2017-10-01', '-e', '2017-10-31'])
    assert args['--start'] == '2017-10-01'
    assert args['--end'] == '2017-10-31'
    assert args['-n'] == None
    assert args['SKIP'] == []
    assert not args['days_from']
    assert args['in_interval']

    with pt.raises(DocoptExit):
        args = docopt(doc, ['days_from', '-s', '2017-10-01', '-e', '2017-10-31'])


def test_cli_implementation_biz_days_from_now():
    doc = biz_days.__doc__
    args = docopt(doc, ['days_from', '-s', '2017-10-01', '-n', '10',
                        '2017-10-10', '2017-01-01'])
    assert args['--start'] == '2017-10-01'
    assert args['--end'] == None
    assert args['-n'] == '10'
    assert args['SKIP'] == ['2017-10-10', '2017-01-01']
    assert not args['in_interval']
    assert args['days_from']

    with pt.raises(DocoptExit):
        args = docopt(doc, ['in_interval', '-s', '2017-10-01', '-n', '20'])


@h.given(arguments=in_between_cli_args())
def test_cli_in_between_general_cases(arguments):
    doc = biz_days.__doc__
    args = arguments[0] + arguments[1]
    parsed = docopt(doc, args)

    assert parsed['--start']
    assert not parsed['days_from']
    assert main(parsed) >= 0


@h.given(arguments=days_from_cli_args())
def test_cli_days_from_general_cases(arguments):
    doc = biz_days.__doc__
    args = arguments[0] + arguments[1]
    parsed = docopt(doc, args)

    assert parsed['--start']
    assert parsed['days_from']
    assert len(main(parsed)) == 10
