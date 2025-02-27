from flask import Flask, request, render_template, flash, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flashing messages

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return filename.endswith(".csv") or filename.endswith(".xlsx")

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file part!", "danger")  # "danger" for Bootstrap error styling
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No selected file!", "danger")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Invalid file type! Please upload a CSV or Excel file.", "warning")
        return redirect(url_for("index"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    flash(f"File '{file.filename}' uploaded successfully!", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
