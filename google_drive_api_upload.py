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
import io
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

    df = pd.read_csv("list_file.csv")

    #Download files from google drive
    file_ids = (df['id'])
    print(file_ids)
    file_names = (df['name'])
    mime_types = []

    for file_id, file_ids in zip(file_ids, file_names):
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        fh.seek(0)
        with open(os.path.join('./', file_names), 'wb') as f:
            f.write(fh.read())
            f.close()

    #upload files to google drive
    for file_name in zip(file_names, mime_types):
        file_metadata = {
            'name': file_name,
            'parents': [file_ids]
        }
        media = MediaFileUpload('./{0}'.format(file_name), mimetype=mime_types)
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

if __name__ == "__main__":
    main()
# [END drive_quickstart]
