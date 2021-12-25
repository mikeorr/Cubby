#!/usr/bin/env python
"""Calculate monthly ORCA use from bank CSV export."""

import argparse
import calendar
import collections
import csv
import datetime
import statistics
import time

DATEFMT = "%m/%d/%Y"
PASS_THRESHOLD = 99
SKIP_CURRENT_MONTH_THRESHOLD = 20

def get_cli():
    parser = argparse.ArgumentParser()
    parser.description = __doc__.splitlines()[0]
    a = parser.add_argument
    a("src", metavar="SOURCE.csv")
    return parser

def get_skip_current_month(today):
    return today.day < SKIP_CURRENT_MONTH_THRESHOLD

def parse_csv(src):
    with open(src) as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert headers[0] == "Date"
        assert headers[2] == "Description"
        assert headers[3] == "Debit"
        data = []   # ``[(date, amount)]``
        for r in reader:
            if "SOUND TRANSIT" not in r[2].upper():
                continue
            date = datetime.datetime.strptime(r[0], DATEFMT)
            amount = abs(int(r[3]))
            data.append((date, amount))
    return data

def get_monthly(data):
    dic = collections.defaultdict(int)
    for date, amount in data:
        key = date.year, date.month
        dic[key] += amount
    monthly = list(dic.items())
    monthly = []
    for key in dic:
        monthly.append((key[0], key[1], dic[key]))
    monthly.sort(reverse=True)
    return monthly

def get_average(monthly, skip_current, today):
    amounts = []
    for year, month, amount in monthly:
        if skip_current and year == today.year and month == today.month:
            continue
        amounts.append(amount)
    average = statistics.mean(amounts)
    return round(average)

def print_report(monthly, average):
    sep = " " * 3
    print("Year", "Mon", "  $", sep=sep)
    print("----", "---", "---", sep=sep)
    fmt = "{:<4}   {:<3}   {:>3}"
    for year, month, amount in monthly:
        month = calendar.month_abbr[month]
        amount = str(amount).rjust(3)
        print(year, month, amount, sep=sep)
    print()
    print("Average:", average)

def main():
    parser = get_cli()
    opts = parser.parse_args()
    today = datetime.date.today()
    skip_current = get_skip_current_month(today)
    data = parse_csv(opts.src)       
    monthly = get_monthly(data)
    average = get_average(monthly, skip_current, today)
    print_report(monthly, average)

if __name__ == "__main__":  main()
