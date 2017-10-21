# biz_days
A CLI utility to calculate the number of business days between two dates or to calculate what date `n` business days from now is.

This project was conceived of primarily to familiarize myself with two interesting python libraries:

- [hypothesis](https://github.com/HypothesisWorks/hypothesis-python)
- [docopt](https://github.com/docopt/docopt)

This README.md was lovingly crafted with the help of [grip](https://github.com/joeyespo/grip).

Finally, the project attempts to follow [semantic versioning guidelines](http://semver.org/).

## Usage

Thanks to `docopt`, CLI usage is clearly printed at the top of `biz_days.py`:
```
Calculate what day is `n` business days from any date (exclusive of start
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

```

So to find out what 10 business days from now would be, we would simply run the command (your output will vary based on what "today" is):

```
$ python biz_days.py days_from -n 10
2017-11-02
```

If instead we are curious how many business days there are in 2017:

```
$ python biz_days.py in_interval -s 2017-01-01 -e 2017-12-31
260
```

Note that holidays *are not* accounted for by default, but can be specified at the end of any command, e.g., you want to exclude 2017 US holidays:

```
$ python biz_days.py in_interval -s 2017-01-01 -e 2017-12-31 2017-01-01 2017-01-02 2017-01-16 2017-05-29 2017-07-04 2017-09-04 2017-10-09 2017-11-10 2017-11-23 2017-11-24 2017-12-25
250
```

## Run Tests

To run all tests, run the following command from the project root directory:

`$ python -m pytest test/`
