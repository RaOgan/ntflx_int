from __future__ import print_function
import os.path
from typing import ItemsView
from wsgiref.simple_server import WSGIRequestHandler
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from collections import Counter
import json
from itertools import groupby
import os
import pandas as pd
import csv


SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    folder_id = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V'
    parent_id = []
    query = f"parents = '{folder_id}'"

    response = service.files().list(
        q=query, 
        fields="nextPageToken, files(id, name, mimeType, parents)",
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True).execute()
    files = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = service.files(
        q=query, 
        fields="nextPageToken, files(id, name, mimeType, parents)",
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True).execute()
        files.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')

    df = pd.DataFrame(files)
    print(df)

if __name__ == "__main__":
    main()