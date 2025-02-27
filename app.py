from flask import Flask, request, render_template, flash, redirect, url_for
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load Google Drive API Credentials
SERVICE_ACCOUNT_FILE = "drive_service_account.json"  # Your downloaded JSON file
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

# Google Drive Folder ID (Create a folder in Google Drive and paste its ID here)
GOOGLE_DRIVE_FOLDER_ID = "1ft_sZijjKaKzIbmvXeUPIaziQE6ayIZn"


def upload_to_drive(filepath, filename):
    """Uploads file to Google Drive inside the specified folder"""
    file_metadata = {
        "name": filename,
        "parents": [GOOGLE_DRIVE_FOLDER_ID]  # Store inside the Drive folder
    }
    media = MediaFileUpload(filepath, mimetype="application/octet-stream")
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    
    return uploaded_file.get("id")


@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload_file():
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


if __name__ == "__main__":
    app.run(debug=True)
