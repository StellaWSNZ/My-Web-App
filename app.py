import os
import base64
import json
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
from flask import Flask, request, render_template, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"
GOOGLE_DRIVE_FOLDER_ID = "1ft_sZijjKaKzIbmvXeUPIaziQE6ayIZn"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Read Google Drive credentials from environment variable
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

if GOOGLE_CREDENTIALS:
    credentials_info = json.loads(base64.b64decode(GOOGLE_CREDENTIALS).decode("utf-8"))
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
else:
    raise Exception("Google Drive credentials not found!")

drive_service = build("drive", "v3", credentials=credentials)

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload and send it to Google Drive"""
    if "file" not in request.files:
        flash("No file part!", "danger")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No selected file!", "danger")
        return redirect(url_for("index"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Upload file to Google Drive
    file_id = upload_to_drive(filepath, file.filename)

    flash(f"File '{file.filename}' uploaded to Google Drive!", "success")
    return redirect(url_for("index"))

def upload_to_drive(filepath, filename):
    """Uploads file to Google Drive"""
    file_metadata = {
        "name": filename,
        "parents": [GOOGLE_DRIVE_FOLDER_ID]  # Replace with your actual Google Drive folder ID
    }
    media = MediaFileUpload(filepath, mimetype="application/octet-stream")
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    
    return uploaded_file.get("id")

if __name__ == "__main__":  
    app.run(debug=True)
