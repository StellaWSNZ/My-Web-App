import os
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
# Read Google Drive credentials from environment variable
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

if GOOGLE_CREDENTIALS:
    credentials_info = json.loads(base64.b64decode(GOOGLE_CREDENTIALS).decode("utf-8"))
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
else:
    raise Exception("Google Drive credentials not found!")

drive_service = build("drive", "v3", credentials=credentials)  
