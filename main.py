from flask import Flask, request, send_from_directory, jsonify, send_file, render_template
import os
from pathlib import Path
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pyngrok import ngrok
app = Flask(__name__, static_folder='static')
CORS(app)

ROOT_DIR = os.path.abspath("shared")

if not os.path.exists(ROOT_DIR):
    os.makedirs(ROOT_DIR)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/browse")
def browse():
    rel_path = request.args.get("path", "")
    abs_path = os.path.abspath(os.path.join(ROOT_DIR, rel_path))

    if not abs_path.startswith(ROOT_DIR):
        return jsonify({"error": "Invalid path"}), 403

    contents = []
    for entry in os.scandir(abs_path):
        contents.append({
            "name": entry.name,
            "path": os.path.relpath(entry.path, ROOT_DIR),
            "is_dir": entry.is_dir()
        })

    return jsonify({
        "current_path": os.path.relpath(abs_path, ROOT_DIR),
        "contents": contents
    })

@app.route("/download")
def download():
    rel_path = request.args.get("path", "")
    abs_path = os.path.abspath(os.path.join(ROOT_DIR, rel_path))

    if not abs_path.startswith(ROOT_DIR) or not os.path.isfile(abs_path):
        return "File not found", 404

    return send_file(abs_path, as_attachment=True)

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("file")
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(ROOT_DIR, filename)
            file.save(save_path)
    return "Files uploaded", 200

if __name__ == "__main__":
    port = 8000
    public_url = ngrok.connect(port)
    print(f" * ngrok tunnel: {public_url}")
    app.run(port=port)