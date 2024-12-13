"""
Author: Tinashe Kucherera
Date: 12/04/2024
"""

import os.path
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from payroll.googleapiauth import GoogleApisAuthenticate

BASE_DIR = Path(__file__).parent


class GoogleDocsApiHandler(GoogleApisAuthenticate):
    """
        This class is used for connecting, getting, and updating documents
    """

    def __init__(self):
        self.base_url = 'https://docs.googleapis.com'
        self.v4_endpoint = '/v1/documents'
        GoogleApisAuthenticate.__init__(self)

    def create(self, document_name):
        try:
            service = build("docs", "v1", credentials=self.creds)
            body = {'title': document_name}
            result = (
                service.documents()
                    .create(body=body)
                    .execute()
            )
            print(f"file created with id: {result.get('documentId')}")
            return result.get('documentId')
        except HttpError as error:
            raise Exception(error)

    def batch_put(self, document_id, data: list, ):
        """
        Sets values in a range of SpreadSheet
        :param document_id:
        :param data:
        :param value_input_option:
        :return result:
        """
        try:
            service = build("docs", "v1", credentials=self.creds)
            body = {'requests': data}
            result = (
                service.documents()
                .batchUpdate(documentId=document_id, body=body)
                .execute()
            )
            #print(f"{result.get('totalUpdatedCells')} cells updated.")
            return result
        except HttpError as error:
            raise Exception(error)






