import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import difflib

Indent = 0

# ID of the Google Doc file to update
document_id = '19ne3LqvdYs2NaEuKoKqMFVBG-e_Pruvr3PEmp50iiQ0'

def authenticate(credentials_file, scopes):
    """Authenticate using the provided credentials file and scopes."""

    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=scopes
    )
    service = build('docs', 'v1', credentials=credentials)
    return service

def insert_word_count(service, document_id):
    """Inserts a line with the word count after each passage in the Google Doc."""

    document = service.documents().get(documentId=document_id).execute()
    requests = []
    
    for element in reversed(document['body']['content']):
        if 'paragraph' in element:
            text = element['paragraph']['elements'][0]['textRun']['content']
            if text == '\n':
                continue
            word_count = len(text.split())
            if word_count == 0:
                continue
            requests.append({
                'insertText': {
                    'location': {
                        'index': element['endIndex']
                    },
                    'text': f'Word Count: {word_count}\n',
                }
            })
            
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': element['endIndex'],
                        'endIndex': element['endIndex'] + len(f'\nWord Count: {word_count}')
                    },
                    'textStyle': {
                        'foregroundColor': {
                            'color': {
                                'rgbColor': {
                                    'red': 1.0,
                                    'green': 0.0,
                                    'blue': 0.0
                                }
                            }
                        }
                    },
                    'fields': 'foregroundColor',
                }
            })

            
    batch_request = service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}
    )
    batch_request.execute()
    print("Word count inserted successfully.")




# Provide the path to your credentials file and the document ID
credentials_file = 'test-user-1.json'
document_id = '19ne3LqvdYs2NaEuKoKqMFVBG-e_Pruvr3PEmp50iiQ0'

# Scopes required for accessing and modifying Google Docs
scopes = ['https://www.googleapis.com/auth/documents']

# Authenticate and create a service
service = authenticate(credentials_file, scopes)

if service:
    insert_word_count(service, document_id)


    