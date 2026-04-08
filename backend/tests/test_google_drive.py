# test_drive.py

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(
    '/app/app/credentials.json',
    scopes=SCOPES
)

service = build('drive', 'v3', credentials=creds)

results = service.files().list(pageSize=5).execute()

print("Conexión exitosa 🚀")
print(results)