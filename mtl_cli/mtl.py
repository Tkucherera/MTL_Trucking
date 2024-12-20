#!/usr/bin/env python
__author__ = 'tkucherera'

import argparse
import os
import json
import sys
import dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from payroll.payperiod import DeterminePayPeriod
from payroll.messages import InvalidDateError
from payroll.main import main


def main():
    argparser = argparse.ArgumentParser(description="This cli is used for making payroll calculations the \
                                                     <truckers> is required arg")
    argparser.add_argument('-t', '--truckers',
                           help='Comma separated list of drivers:sheetname with the sheet parsed as well: driver_percentage', )
    argparser.add_argument('-d', '--date', help='The pay date (should be a friday)', )
    argparser.add_argument('-l', '--loads', help='The name of the sheet with all the trips default is Trip Sheet',
                           default='Trip Sheet')
    argparser.add_argument('-p', '--prompt', action='store_true', help='Prompt for the required variables interactively')
    argparser.add_argument('-e', '--environment', type=str, metavar='.env',
                           help='Use an environment file to parse required arguments')
    argparser.add_argument('-j', '--json', type=str, metavar="args.json",
                           help='Use a json formatted file to parse required arguments (recommended)')


    args = argparser.parse_args()


    drivers = []
    pay_date = None

    if args.date:
        pay_date = args.date
        try:
            DeterminePayPeriod(pay_date)
        except InvalidDateError as e:
            print(f'[ERROR] {e}')
            sys.exit(1)

    if args.truckers:
        try:
            drivers_argument = args.truckers.split(',')
            for driver in drivers_argument:
                driver, sheet_name, driver_percentage = (driver.split(':')[0], driver.split(':')[1], driver.split(':')[2])
                try:
                    driver_percentage = float(driver_percentage)
                except ValueError:
                    print("Percentage has to be in integer or decimal format (Numeric)")
                    sys.exit(1)

                drivers.append({
                    'driver_name': driver,
                    'sheet_name': sheet_name,
                    'percentage': driver_percentage
                })
        except Exception as e:
            print(e)
            sys.exit(1)

    if args.prompt:
        print('MTL cli tool enter arguments interactively press c to cancel')
        while True:
            input_date = input("Enter the pay date (mm/dd/yy): ")
            if input_date.lower() == "c":
                sys.exit(0)
            try:
                DeterminePayPeriod(input_date)
                pay_date = input_date
                break
            except InvalidDateError as e:
                print(f'[ERROR] {e}')
        drivers = []
        while True:
            driver = input("Enter driver name (press n when done): ")
            if driver.lower() == "n":
                break
            driver_calculation_sheet = input(f"Enter the Sheet used to calculate pay for driver {driver}: ")
            while True:
                try:
                    driver_percentage = float(input(f"Enter driver percentage {driver}: "))
                    break
                except ValueError:
                    print("Percentage has to be in integer or decimal format (Numeric)")
            drivers.append({
                'driver_name': driver,
                'sheet_name': driver_calculation_sheet,
                'percentage': driver_percentage
            })

    if args.json:
        file = args.json
        # confirm existence of file
        if os.path.exists(file):
            with open(file, 'r') as f:
                data = json.load(f)
            pay_date = data.get('pay_date', None)
            drivers = data.get('drivers', [])
            if pay_date:
                try:
                    DeterminePayPeriod(pay_date)
                except InvalidDateError as e:
                    print(f'[ERROR] {e}')
                    sys.exit(1)
        else:
            print('Could not find file try inputting full path: ', file)
            sys.exit(1)

    if args.environment:
        dotenv.load_dotenv()
        pay_date = os.environ.get('pay_date', None)
        drivers_env = os.environ.get('drivers', None)
        try:
            drivers_argument = drivers_env.split(',')
            for driver in drivers_argument:
                driver, sheet_name, driver_percentage = (driver.split(':')[0], driver.split(':')[1], driver.split(':')[2])
                try:
                    driver_percentage = float(driver_percentage)
                except ValueError:
                    print("Percentage has to be in integer or decimal format (Numeric)")
                    sys.exit(1)

                drivers.append({
                    'driver_name': driver,
                    'sheet_name': sheet_name,
                    'percentage': driver_percentage
                })
        except Exception as e:
            print(e)
            sys.exit(1)

    trip_sheet = args.loads

    if drivers:
        main(drivers, trip_sheet, pay_date)
    else:
        argparser.print_help()


