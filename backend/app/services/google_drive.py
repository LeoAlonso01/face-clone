from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        '/app/app/credentials.json',
        scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)


def upload_pdf_to_drive(file_bytes: bytes, acta_id: int):
    service = get_drive_service()

    filename = f"Acta_{acta_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    file_stream = io.BytesIO(file_bytes)

    file_metadata = {
        "name": filename,
        "parents": ["1vPpuWKBXKwKnwZkMoKAqiqsbCAcLuUk5"]
    }

    media = MediaIoBaseUpload(file_stream, mimetype='application/pdf')

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = uploaded.get('id')

    # 🔥 HACER PÚBLICO
    service.permissions().create(
        fileId=file_id,
        body={
            'role': 'reader',
            'type': 'anyone'
        }
    ).execute()

    # 🔥 TRANSFERIR PROPIEDAD (SOLUCIÓN AL QUOTA)
    service.permissions().create(
        fileId=file_id,
        body={
            'type': 'user',
            'role': 'owner',
            'emailAddress': 'entrega.recepcion@umich.mx'
        },
        transferOwnership=True
    ).execute()

    url = f"https://drive.google.com/file/d/{file_id}/view"

    return {
        "file_id": file_id,
        "url": url,
        "nombre_archivo": filename
    }