
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime
# Función para autenticar y obtener el servicio de Google Drive
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive']


def get_drive_service():
    creds = None

    if os.path.exists('/app/app/token.pickle'):
        with open('/app/app/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/app/app/credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open('/app/app/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

# Función para subir un PDF a Google Drive y obtener su URL pública
def upload_pdf_to_drive(file_bytes:bytes, acta_id:int):
    service = get_drive_service()

    # nombre controlado para evitar colisiones
    filename = f"Acta_{acta_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    # Crear un stream de bytes para el archivo PDF
    file_stream = io.BytesIO(file_bytes)

    # Metadata del archivo en Drive
    file_metadata = {
        "name": filename,
        "parents" : ["1vPpuWKBXKwKnwZkMoKAqiqsbCAcLuUk5"] # carpeta de resumenes en drive
    }

    # Subir el archivo a Google Drive
    media = MediaIoBaseUpload(file_stream, mimetype='application/pdf')

    # Subir el archivo y obtener su ID
    uploades = service.files().create(
        body = file_metadata,
        media_body = media,
        fields = 'id'
    ).execute()

    # Obtener el ID del archivo subido
    file_id = uploades.get('id')

    # hacer el archivo publico
    service.permissions().create(
        fieldId = file_id,
        body = {
            'role': 'reader',
            'type': 'anyone'
        }
    ).execute()

    # obtener url de visualizacion
    url = f"https://drive.google.com/file/d/{file_id}/view"

    # Retornar el ID del archivo, la URL y el nombre del archivo
    return {
        "file_id": file_id,
        "url": url,
        "nombre_archivo": filename
    }
