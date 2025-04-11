from flask import Flask, request, send_from_directory, jsonify, send_file, render_template
import os
from pathlib import Path
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pyngrok import ngrok 
import shutil
import time

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
    current_path = request.form.get("current_path", "")
    upload_dir = os.path.join(ROOT_DIR, current_path)
    
    if not os.path.abspath(upload_dir).startswith(ROOT_DIR):
        return jsonify({"error": "Invalid path"}), 403
        
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(upload_dir, filename)
            file.save(save_path)
    return "Files uploaded", 200

@app.route("/delete", methods=["DELETE"])
def delete_file():
    rel_path = request.args.get("path", "")
    abs_path = os.path.abspath(os.path.join(ROOT_DIR, rel_path))

    if not abs_path.startswith(ROOT_DIR):
        return "Invalid path", 403

    try:
        if os.path.isfile(abs_path):
            os.remove(abs_path)
        elif os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        return "Item deleted", 200
    except Exception as e:
        return str(e), 500

@app.route("/create-folder", methods=["POST"])
def create_folder():
    data = request.json
    folder_path = os.path.join(ROOT_DIR, data.get('path', ''), data.get('name', ''))
    
    if not os.path.abspath(folder_path).startswith(ROOT_DIR):
        return jsonify({"error": "Invalid path"}), 403
        
    try:
        os.makedirs(folder_path, exist_ok=True)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/storage-info")
def storage_info():
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    # For demo purposes, we'll set a fixed total storage capacity
    total_capacity = 1024 * 1024 * 1024 * 10  # 10 GB
    
    return jsonify({
        "used": total_size,
        "total": total_capacity
    })

@app.route("/preview")
def preview_file():
    rel_path = request.args.get("path", "")
    abs_path = os.path.abspath(os.path.join(ROOT_DIR, rel_path))

    if not abs_path.startswith(ROOT_DIR) or not os.path.isfile(abs_path):
        return "File not found", 404

    try:
        with open(abs_path, 'r') as file:
            content = file.read()
        return content
    except:
        return "Cannot preview this file type", 400

@app.route("/recent")
def recent_files():
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            rel_path = os.path.relpath(fp, ROOT_DIR)
            files.append({
                "name": f,
                "path": rel_path,
                "is_dir": False,
                "modified": os.path.getmtime(fp)
            })
    
    # Sort by modification time (most recent first)
    files.sort(key=lambda x: x["modified"], reverse=True)
    
    # Return only the 20 most recent files
    return jsonify({"files": files[:20]})

if __name__ == "__main__":
    port = 8000
    app.run(port=port)