import os
import requests
import json
from flask import Flask, request, render_template, flash, redirect, url_for, session
from msal import ConfidentialClientApplication

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load credentials from environment variables
CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID")
CLIENT_SECRET = os.getenv("ONEDRIVE_CLIENT_SECRET")
TENANT_ID = os.getenv("ONEDRIVE_TENANT_ID")
REDIRECT_URI = "http://localhost:5000/callback"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.ReadWrite", "offline_access"]
ONEDRIVE_FOLDER = "FOLDER"  # Change to your actual folder name in OneDrive

msal_app = ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/login")
def login():
    """Redirect user to Microsoft login"""
    auth_url = msal_app.get_authorization_request_url(SCOPES, redirect_uri=REDIRECT_URI)
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """Handle Microsoft login callback"""
    code = request.args.get("code")
    token_response = msal_app.acquire_token_by_authorization_code(code, SCOPES, redirect_uri=REDIRECT_URI)

    if "access_token" in token_response:
        session["access_token"] = token_response["access_token"]
        flash("Logged in successfully!", "success")
    else:
        flash("Login failed!", "danger")

    return redirect(url_for("index"))

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload and send to OneDrive"""
    if "file" not in request.files:
        flash("No file part!", "danger")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No selected file!", "danger")
        return redirect(url_for("index"))

    file_id = upload_to_onedrive(file)

    if file_id:
        flash(f"File '{file.filename}' uploaded to OneDrive!", "success")
    else:
        flash(f"Failed to upload '{file.filename}'", "danger")

    return redirect(url_for("index"))

def upload_to_onedrive(file):
    """Uploads file to OneDrive Business"""
    access_token = session.get("access_token")

    if not access_token:
        flash("You must log in first!", "danger")
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream"
    }
    
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{ONEDRIVE_FOLDER}/{file.filename}:/content"

    response = requests.put(upload_url, headers=headers, data=file.read())

    print("OneDrive Response:", response.status_code, response.json())

    if response.status_code in [200, 201]:
        return response.json().get("id")
    else:
        return None

if __name__ == "__main__":
    app.run(debug=True)
