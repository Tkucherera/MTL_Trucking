"""
Author: Tinashe Kucherera
Date: 12/04/2024
"""

import os.path
from pathlib import Path

from payroll.googleapiauth import GoogleApisAuthenticate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).parent


class GoogleSheetsApiHandler(GoogleApisAuthenticate):
    """
    This class is used for connecting, getting, and updating spreadsheets
    """
    def __init__(self):
        self.base_url = 'https://sheets.googleapis.com'
        self.v4_endpoint = '/v4/spreadsheets'
        GoogleApisAuthenticate.__init__(self)

    def get(self, spreadsheet_id, sheet_name=None):
        """
        Retrieves the google spreadsheet for the given id
        Can also retrieve a specific sheet is name specified
        :param spreadsheet_id:
        :param sheet_name:
        :return spreadsheet values:
        :raises HttpError
        """

        try:
            return_sheets = {}
            service = build("sheets", 'v4', credentials=self.creds)
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            if sheet_name and sheet_name in sheets:
                result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                             range=sheet_name).execute()
                values = result.get('values', [])
                return {sheet_name: values}
            for sheet in sheets:
                sheet_name = sheet['properties']['title']
                result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                             range=sheet_name).execute()
                values = result.get('values', [])
                return_sheets[sheet_name] = values
            return return_sheets
        except HttpError as error:
            print(error)
        return None

    def post(self, spreadsheet_id, sheet_range):
        """
        Appends values to a spread sheet
        :param spreadsheet_id:
        :param sheet_range:
        :return:
        """
        # Note this one we might not use much even though it is supposed to append
        return

    def put(self, spreadsheet_id, sheet_name, sheet_range, values, value_input_option="USER_ENTERED"):
        """
        Sets values in a range of SpreadSheet
        :param spreadsheet_id:
        :param sheet_name:
        :param sheet_range:
        :param values:
        :param value_input_option:
        :return result:
        """
        try:
            range_name = f'{sheet_name}!{sheet_range}'
            service = build("sheets", "v4", credentials=self.creds)
            body = {"values": values}
            result = (
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )
            print(f"{result.get('updatedCells')} cells updated.")
            return result
        except HttpError as error:
            raise Exception(error)

    def batch_put(self, spreadsheet_id, data: list, value_input_option="USER_ENTERED"):
        """
        Sets values in a range of SpreadSheet
        :param spreadsheet_id:
        :param data:
        :param value_input_option:
        :return result:
        """
        try:
            service = build("sheets", "v4", credentials=self.creds)
            body = {'valueInputOption': value_input_option, 'data': data}
            result = (
                service.spreadsheets()
                .values()
                .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
                .execute()
            )
            print(f"{result.get('totalUpdatedCells')} cells updated.")
            return result
        except HttpError as error:
            raise Exception(error)

