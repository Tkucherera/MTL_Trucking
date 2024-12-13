"""
Author: Tinashe Kucherera
Date: 12/04/2024
"""

from payroll.googlesheethandler import GoogleSheetsApiHandler
from payroll.googledocshandler import GoogleDocsApiHandler
from payroll.payperiod import DeterminePayPeriod
import datetime
import dotenv
import sys
import os
from payroll.messages import Trip
from payroll.docs_writer import write_google_doc
dotenv.load_dotenv()


class AdminExpenses:
    def __init__(self, balance):
        self.balance = balance
        self.mtl_percentage = 0.10
        self.dispatch_percentage = 0.10
        self.admin_percentage = 0.05
        self.mtl_fee = round(self.balance * self.mtl_percentage, 2)
        self.dispatch_fee = round(self.balance * self.dispatch_percentage, 2)
        self.admin_fee = round(self.balance * self.admin_percentage, 2)
        self.total_admin = round(self.admin_fee + self.dispatch_fee + self.mtl_fee,2)
        self.balance_after_admin = round(self.balance - self.total_admin, 2)


class OperatingExpenses:
    def __init__(self, sheet_values: list, working_column_index):
        self.sheet_values = sheet_values
        self.start_row, self.operating_expense_row_index = self.get_start_and_end_operating_exp_row()
        self.operating_expense_row = self.operating_expense_row_index + 1
        self.working_column_index = working_column_index
        self.total_expenses = self.calculate_total_operating_expense()

    def get_start_and_end_operating_exp_row(self):
        """
        For now we shall assume that the row that has the fuel tag in column 1
        We might be able to convince the Customer to be consistent with the spreadsheets
        :return: row
        """
        row_count = 0
        start_row = None
        end_row = None
        for row in self.sheet_values:
            if len(row) > 2:
                if 'fuel' == row[0].lower():
                    start_row = row_count
                elif 'operating expenses' == row[0].lower():
                    end_row = row_count
                    return start_row, end_row

            row_count += 1

    def calculate_total_operating_expense(self):
        total = 0.00
        for i in range(self.start_row, self.operating_expense_row_index):
            try:
                fee = self.sheet_values[i][self.working_column_index]
            except IndexError:
                continue
            if fee:
                expense = fee.strip(',$')
                value = float(expense.replace(',', ''))
                total += value
        return round(total, 2)


# Fist things first l need to determine the week that we are looking at
class Driver:
    def __init__(self, name):
        self.name = name
        self.truck = ''
        self.trips = []
        self.total_money = 0.00
        self.pay = 0.00
        self.balance_after_factoring_fee = 0.00
        self.balance_after_admin_fee = 0.00
        self.balance_after_ach_fee = 0.00
        self.factoring_fee = 0.00
        self.admin_fee = 0.00
        self.balance = 0.00   # This is the balance after removing calculating pay

    def add_trip(self, trip):
        if isinstance(trip, Trip):
            self.trips.append(trip)
        else:
            raise Exception('trip has to be an instance of trip')

    def calculate_total(self):
        for trip in self.trips:
            if trip.rate:
                # TODO Need to come back and add a try block here
                trip_rate = trip.rate.strip(',$')
                value = float(trip_rate.replace(',', ''))
                self.total_money += value

        return self.total_money

    def calculate_driver_fee(self, percentage):
        """
        This deducts all the fees from the total money attribute
        :the deductions are
            5% FACTORING FEE
            5% ADMIN FEE
        FROM THE REMAINDER THEN THE DRIVER GETS PERCENTAGE PARSED
        SUBTRACT ACH FEE
        :param percentage:
        :return:
        """
        FACTORING_FEE = 0.05
        ADMIN_FEE = 0.05
        ACH_FEE = 3.00

        # Calculate factoring fee
        self.factoring_fee = round((self.total_money * FACTORING_FEE), 2)

        # remove factoring fee
        self.balance_after_factoring_fee = round(self.total_money * (1 - FACTORING_FEE), 2)
        # calculate admin fee
        self.admin_fee = round((self.balance_after_factoring_fee * ADMIN_FEE), 2)

        # remove admin fee from the running total
        self.balance_after_admin_fee = round(self.balance_after_factoring_fee * (1 - ADMIN_FEE), 2)

        # Calculate the driver fee and remove ach fee
        self.balance_after_ach_fee = (self.balance_after_admin_fee * percentage) - ACH_FEE
        self.pay = round(self.balance_after_ach_fee, 2)

        # The remaining money for in business
        self.balance = round((self.balance_after_admin_fee - self.pay), 2)




class ValuesParser:
    def __init__(self, values):
        """
        This class is responsible consuming a sheet and the returns Rows with a specific date and or Driver
        :param values:
        """
        self.values = values

    def seek(self, driver: Driver = None, dates: list = None):
        """
        This is now going to then search date and driver column for given stuff
        :param driver: string
        :param dates: string
        :return:
        """
        needed_rows = []
        for row in self.values:
            if row[0] in dates:
                if driver and row[1] == driver.name:
                    needed_rows.append(row)
                elif driver is None:
                    needed_rows.append(row)
        return needed_rows


class CellModification:
    def __init__(self, row: int, column: str, value):
        self.row = row
        self.column = column
        self.cell = f'{column}{row}'
        self.value = value


class DriverCalculationSheet(Driver, OperatingExpenses):

    def __init__(self, name, pay_date: str, sheet_values):
        """
        This class is the one that actually prepares the data to be writen to the spreadsheet
        :param name:
        """
        self.name = name
        self.date = pay_date
        self.sheet_values = sheet_values
        self.dates_row = 2
        self.dates_row_index = 1
        self.total_row = 12
        self.working_column_index = self._get_working_column()
        self.total_income_row = self.get_total_income_row()
        self.working_column = self._working_column()
        self.modification_values = []
        Driver.__init__(self, name)
        OperatingExpenses.__init__(self, sheet_values, self.working_column_index)  # Probably not the best idea


    def _get_working_column(self):
        # TODO This did not work 1 make sure that date is a stirng but also has the same format MM/DD/YY likely culprit is format
        dates_row = self.sheet_values[self.dates_row_index]
        try:
            working_index = dates_row.index(self.date)
        except ValueError:
            # if index is not found then we will just have to create the date
            working_index = len(dates_row)
        finally:
            # here we then take the working_index and figure out the Alpha value ABCD
            return working_index

    def create_modification_values(self):
        row = 3
        for trip in self.trips:
            self.modification_values.append(CellModification(row, self.working_column, trip.rate))
            row += 1

        self.modification_values.append(CellModification(self.total_row, self.working_column, f'${self.total_money}'))

        # Start adding salary calculation data
        self.modification_values.append(CellModification(self.total_income_row, self.working_column, f'${self.total_money}'))

        row = self.total_income_row + 1
        # Less factoring value
        self.modification_values.append(CellModification(row, self.working_column, f'${self.factoring_fee}'))
        row += 1

        # Balance after removing factoring value
        self.modification_values.append(CellModification(row, self.working_column, f'${self.balance_after_factoring_fee}'))
        row += 1

        # Less Admin Fee
        self.modification_values.append(CellModification(row, self.working_column, f'${self.admin_fee}'))
        row += 1

        # Balance after removing admin value
        self.modification_values.append(CellModification(row, self.working_column, f'${self.balance_after_admin_fee}'))
        row += 1

        # Driver fee
        driver_fee = self.pay + 3
        self.modification_values.append(CellModification(row, self.working_column, f'${driver_fee}'))
        row += 1

        # Driver fee
        self.modification_values.append(CellModification(row, self.working_column, f'${self.balance}'))
        row += 1

        # Less ACH fee
        self.modification_values.append(CellModification(row, self.working_column, '$3.00'))
        row += 1

        # Actual Salary
        self.modification_values.append(CellModification(row, self.working_column, f'${self.pay}'))

        # Total Operating Expense
        self.modification_values.append(CellModification(self.operating_expense_row, self.working_column,
                                                         f'${self.total_expenses}'))

        return self.modification_values

    def add_admin_modification_values(self, admin_expenses: AdminExpenses):
        row = self.operating_expense_row + 1

        # Balance after removing expenses
        self.modification_values.append(CellModification(row, self.working_column,
                                                         f'${round(self.balance - self.total_expenses, 2)}'))
        row += 2

        # mtl fee
        self.modification_values.append(CellModification(row, self.working_column, f'${admin_expenses.mtl_fee}'))
        row += 1

        # dispatch fee
        self.modification_values.append(
            CellModification(row, self.working_column, f'${admin_expenses.dispatch_fee}'))
        row += 1

        # admin fee (rev)
        self.modification_values.append(CellModification(row, self.working_column, f'${admin_expenses.admin_fee}'))
        row += 1

        # total admin fees
        self.modification_values.append(
            CellModification(row, self.working_column, f'${admin_expenses.total_admin}'))

        overall_balance = round(self.balance - (self.total_expenses + admin_expenses.total_admin), 2)
        self.modification_values.append(
            CellModification(row, self.working_column, f'${overall_balance}'))

        return self.modification_values

    def get_total_income_row(self):
        row_index = 0
        for row in self.sheet_values:
            if len(row) > 1:
                if 'Total Income' == row[0]:
                    return row_index + 1
                    break
            row_index += 1

        # otherwise just return we could do some more tricks here to figure out but this is fine for now
        return 15

    def _working_column(self):
        """
        This one takes on a column index and return what the actual alpha value is
        Converts a zero-based index to the corresponding Google Sheets column label.
        :return aplha value:
        """

        result = []
        index = self.working_column_index
        while index >= 0:
            result.append(chr(index % 26 + ord('A')))  # Find the letter for this position
            index = index // 26 - 1  # Move to the next "digit" in base 26 (like carrying in base 10)

        # Reverse the result to get the correct order (e.g., 'A' then 'B' instead of 'B' then 'A')
        return ''.join(result[::-1])

# NOTE The pay date is now going to be separated from the
# TODO Some decimal values are quite being rounded well to two decimal places this might result in a figure that is 0.01 cents off discuss with client
# TODO Also now go fo cli if customer needs something different discuss with them
# TODO need to also need to look extensively into the who google cloud, authentication, billing and verify app situation
# TODO Looking into logging reports stdout, stderror
# Figure out the Pay date thing





def main(drivers: list, trip_sheet_name: str, pay_date=None):
    MTL_Dispatch_Tracker_SPREADSHEET_ID = os.getenv("MTL_Dispatch_Tracker_SPREADSHEET_ID")
    handler = GoogleSheetsApiHandler()

    sheet_dict = handler.get(MTL_Dispatch_Tracker_SPREADSHEET_ID, trip_sheet_name)
    sheet_values = sheet_dict[trip_sheet_name]
    parser = ValuesParser(sheet_values)


    # Pay Period We want
    d = DeterminePayPeriod(pay_date)
    dates = d.stringified_pay_period

    drivers_calculation_objects = []
    for driver in drivers:
        driver, sheet_name, driver_percentage = (driver['driver_name'], driver['sheet_name'], driver['percentage'])
        try:
            driver_percentage = driver_percentage / 100
        except Exception as e:
            raise Exception(e)

        calculation_sheet_dict = handler.get(MTL_Dispatch_Tracker_SPREADSHEET_ID, sheet_name)
        calculation_sheet_values = calculation_sheet_dict[sheet_name]
        trucker = DriverCalculationSheet(driver, d.stringify_date(d.saturday_pay_date, "%m/%d/%y"), calculation_sheet_values)
        drivers_calculation_objects.append(trucker)

        # need to get all the drivers and then create driver objects
        # These driver objects and dates are then used for a grander skeem
        rows = parser.seek(driver=trucker, dates=dates)
        if len(rows) == 0:
            print(f"Could Not find any loads for {trucker.name} from {dates[0]} to {dates[-1]}")
            continue
        for row in rows:
            if len(row) > 20:
                try:
                    trucker.add_trip(Trip(date=row[0], driver=row[1], broker=row[3], rate_con=row[4], rate=row[20]))
                except Exception as e:
                    raise Exception(f'Adding trip for driver {trucker.name} failed with error {e}')

        trucker.calculate_total()
        trucker.calculate_driver_fee(driver_percentage)
        trucker.create_modification_values()
        admin_expenses = AdminExpenses(trucker.balance)
        trucker.add_admin_modification_values(admin_expenses)

        update_data = []
        for additional_mod in trucker.modification_values:
            print(f'{sheet_name}!{additional_mod.cell}: {additional_mod.value}')
            update_data.append(
                {"range": f'{sheet_name}!{additional_mod.cell}', "values": [[additional_mod.value]]})

        sys.exit()

        handler.batch_put(MTL_Dispatch_Tracker_SPREADSHEET_ID, update_data)
        write_google_doc(trucker, d.stringify_date(d.saturday_pay_date, "%m/%d/%y"), d.stringify_date(d.to_be_paid_out_date, "%m/%d/%y"))







