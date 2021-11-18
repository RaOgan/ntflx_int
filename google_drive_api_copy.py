from __future__ import print_function
import os.path
from typing import ItemsView
from wsgiref.simple_server import WSGIRequestHandler, server_version
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from collections import Counter
import json
import requests
import os
import pandas as pd
import csv

# If modifying these scopes, delete the file token.json.
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

    df = pd.read_csv("list_file.csv").astype(str)
    dff = pd.read_csv("list_folder.csv").astype(str)

    #Copy files from google drive to different folder
    for file_id in df['id']:
        file_metadata = {
            'name': df['name'],
            'parents': dff['parents'],
            'mimeType': df['mimeType']
        }
        service.files().copy(fileId=file_id, body=file_metadata).execute()

if __name__ == "__main__":
    main()
# [END drive_quickstart]
