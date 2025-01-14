__author__ = 'tkucherera'

import datetime
from payroll.messages import InvalidDateError

class DeterminePayPeriod:
    """
    This class determines the Pay period based on this formula
        - determine when the  pay date is (always a friday)
            i. this date can be input, if not then the class will automatically determine coming up friday using date module
        - determine the pay period
            i. This is the period from the previous friday until the thursday before pay day

        - DATE FORMAT: M/DD/YYYY
    """
    def __init__(self, pay_date=None):
        self.date_format = "%-m/%d/%Y"
        if pay_date:
            self.pay_date = self.make_date_object(pay_date)
        else:
            self.pay_date = self._determine_pay_date()
        self.end_week_date = self._determine_end_week_date()
        self.stringified_pay_period = []
        self.pay_period = self.determine_pay_period()
        self.saturday_pay_date = self.pay_date + datetime.timedelta(1)
        self.to_be_paid_out_date = self.pay_date + datetime.timedelta(7)

        # Note there is definitely a better way but for now the order of attributes has to strictly be this way

    def _determine_pay_date(self):
        today = datetime.date.today()
        friday = today + datetime.timedelta((4 - today.weekday()) % 7)
        return friday

    def _determine_end_week_date(self):
        end_week_day = self.pay_date - datetime.timedelta(6)
        return end_week_day

    def determine_pay_period(self):
        start_pay_period = self.pay_date - datetime.timedelta(12)
        time_delta = self.end_week_date - start_pay_period + datetime.timedelta(1)
        days = []
        stringified_dates = []
        for i in range(time_delta.days):
            date = start_pay_period + datetime.timedelta(days=i)
            days.append(date)
            stringified_dates.append(date.strftime("%-m/%-d/%Y"))
        self.stringified_pay_period = stringified_dates
        return days

    def stringify_date(self, date, format=None):
        if format:
            try:
                return date.strftime(format)
            except Exception as error:
                raise Exception('failed to stringify date ', error)
        return date.strftime(self.date_format)

    def print_pay_date(self):
        return self.pay_date.strftime(self.date_format)

    def is_friday(self, date):
        return date.weekday() == 4

    def make_date_object(self, pay_date_str):
        try:
            pay_date = datetime.datetime.strptime(pay_date_str, "%m/%d/%y")
            if not self.is_friday(pay_date):
                raise InvalidDateError('Date has to be a Friday')
            return pay_date
        except ValueError as e:
            raise InvalidDateError('failed to convert given date please check the date format is MM/DD/YY')
