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

    drive_api_ref = build('drive', 'v3', credentials=creds)

    #get folders in root folder
    page_token = None
    max_allowed_page_size = 1000
    just_folders = "trashed = false and mimeType = 'application/vnd.google-apps.folder'"
    while True:
        results_fl = drive_api_ref.files().list(
            pageSize=max_allowed_page_size,
            fields="nextPageToken, files(id, name, mimeType, parents)",
            includeItemsFromAllDrives=True, supportsAllDrives=True,
            pageToken=page_token,
            q=just_folders).execute()
        jfl_results = json.dumps(results_fl)
        jfl_results = jfl_results.replace('["','"').replace('"]', '"')

        #print(jfl_results)
        folder_count = jfl_results.count('"id"')
        print("Number of Folders: ", folder_count)

        #Write to a JSON file for folders
        with open('folder_list.json', 'w') as f:
            f.write(jfl_results)

        #Write to a CSV file for folders
        with open ("folder_list.json", "r") as f: 
            data = json.load(f) 
            files = data["files"] 
        with open ("list_folder.csv", "w",newline="") as f: 
            fieldnames  = files[0].keys() 
            writer = csv.DictWriter(f, fieldnames=fieldnames) 
            writer.writeheader() 
            for file in files: 
                writer.writerow(file)

        #Get files in each folder
        just_files = "mimeType != 'application/vnd.google-apps.folder' and trashed = false"
        while True:
            results = drive_api_ref.files().list(
                pageSize=max_allowed_page_size,
                fields="nextPageToken, files(id, name, mimeType, parents)",
                includeItemsFromAllDrives=True, supportsAllDrives=True,
                pageToken=page_token,
                q=just_files).execute()
            jfi_results = json.dumps(results)
            jfi_results = jfi_results.replace('["','"').replace('"]', '"')
            #print(jfi_results)
            file_count = jfi_results.count('"id"')
            print("Number of Files: ", file_count)

            #Write to a JSON file for files
            with open('file_list.json', 'w') as f:
                f.write(jfi_results)

            #Write to a CSV file for files
            with open ("file_list.json", "r") as f: 
                data = json.load(f) 
                files = data["files"] 
            with open ("list_file.csv", "w",newline="") as f: 
                fieldnames  = files[0].keys() 
                writer = csv.DictWriter(f, fieldnames=fieldnames) 
                writer.writeheader() 
                for file in files: 
                    writer.writerow(file) 
            
            file_folder = pd.concat([pd.read_csv("list_file.csv"), pd.read_csv("list_folder.csv")])
            print(file_folder.to_csv("file_folder.csv", index=False))

            df = pd.read_csv("file_folder.csv")
            print(df.groupby(['mimeType'])['parents'].count())
            print(df.groupby(['mimeType', 'parents'])['id'].count())
            
            page_token = results.get('nextPageToken', None)
            if page_token is None:
                break
        return

if __name__ == "__main__":
    main()