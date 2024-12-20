"""
- This file is mostly to be able to Standardise Data Parsing between Modules
this is for example of a put or get resource looks

- Additionally Exceptions will also be here to be able to enable having detailed
failure messages for example how a put failure looks
"""
__author__ = 'tkucherera'


class InvalidDateError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class PutSuccess:
    def __init__(self, status, sheet_range, sheet_name, message=None):
        """
        This is a resource with pertinent information for update success to a spreadsheet
        :param status:
        :param sheet_range:
        :param sheet_name:
        :param message:
        """
        self.status = status
        self.range = sheet_range
        self.sheet_name = sheet_name
        self.message = message


class Trip:
    def __init__(self, date=None, driver=None, broker=None, rate_con=None, rate=None):
        """
        Important values that we need from Trip Sheet
        :param date:
        :param driver:
        :param broker:
        :param rate_con:
        :param rate:
        """
        self.date = date
        self.driver = driver
        self.broker = broker
        self.rate_con = rate_con
        self.rate = rate  # Column U
        self.sheet_name = "Trip Sheet"

