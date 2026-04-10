from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive']

flow = InstalledAppFlow.from_client_secrets_file(
    '/app/app/credentials.json',
    SCOPES
)

auth_url, _ = flow.authorization_url(prompt='consent')

print("\n👉 Abre esta URL en tu navegador:\n")
print(auth_url)

code = input("\n🔑 Pega aquí el código de autorización: ")

flow.fetch_token(code=code)

creds = flow.credentials

with open('/app/app/token.pickle', 'wb') as token:
    pickle.dump(creds, token)

print("\n✅ TOKEN GENERADO CORRECTAMENTE")