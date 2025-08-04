from flask import Flask, request, send_from_directory, jsonify, send_file, render_template, redirect, url_for, session, flash
import os
from pathlib import Path
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pyngrok import ngrok 
import shutil
import time
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key
CORS(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

SHARED_DIR = os.path.abspath("shared")
if not os.path.exists(SHARED_DIR):
    os.makedirs(SHARED_DIR)

def get_root_dir():
    mode = session.get("root_mode", "shared")
    if mode == "full":
        if os.name == "nt":  # Windows
            # Return list of drives (C:\, D:\, etc.)
            # For simplicity, use C:\ as root
            return "C:\\"
        else:
            return "/"
    else:
        return SHARED_DIR

@app.route("/set_root")
def set_root():
    mode = request.args.get("mode", "shared")
    if mode not in ["shared", "full"]:
        return jsonify({"error": "Invalid mode"}), 400
    session["root_mode"] = mode
    return jsonify({"success": True, "mode": mode})

@app.route("/")
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('signup'))
            
        try:
            hashed_password = generate_password_hash(password, method='scrypt')
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                     (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
            return redirect(url_for('signup'))
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[0], password):
            session['username'] = username
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Add this decorator to all routes that need authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Protect existing routes by adding @login_required decorator
@app.route("/browse")
@login_required
def browse():
    rel_path = request.args.get("path", "")
    root_dir = get_root_dir()
    abs_path = os.path.abspath(os.path.join(root_dir, rel_path))

    if not abs_path.startswith(root_dir):
        return jsonify({"error": "Invalid path"}), 403

    contents = []
    for entry in os.scandir(abs_path):
        contents.append({
            "name": entry.name,
            "path": os.path.relpath(entry.path, root_dir),
            "is_dir": entry.is_dir()
        })

    return jsonify({
        "current_path": os.path.relpath(abs_path, root_dir),
        "contents": contents
    })

@app.route("/download")
@login_required
def download():
    rel_path = request.args.get("path", "")
    root_dir = get_root_dir()
    abs_path = os.path.abspath(os.path.join(root_dir, rel_path))

    if not abs_path.startswith(root_dir) or not os.path.isfile(abs_path):
        return "File not found", 404

    return send_file(abs_path, as_attachment=True)

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("file")
    current_path = request.form.get("current_path", "")
    root_dir = get_root_dir()
    upload_dir = os.path.join(root_dir, current_path)
    
    if not os.path.abspath(upload_dir).startswith(root_dir):
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
    root_dir = get_root_dir()
    abs_path = os.path.abspath(os.path.join(root_dir, rel_path))

    if not abs_path.startswith(root_dir):
        return jsonify({"error": "Invalid path"}), 403

    try:
        if os.path.isfile(abs_path):
            os.remove(abs_path)
        elif os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/create-folder", methods=["POST"])
def create_folder():
    data = request.json
    folder_path = os.path.join(get_root_dir(), data.get('path', ''), data.get('name', ''))
    
    if not os.path.abspath(folder_path).startswith(get_root_dir()):
        return jsonify({"error": "Invalid path"}), 403
        
    try:
        os.makedirs(folder_path, exist_ok=True)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/storage-info")
def storage_info():
    total_size = 0
    root_dir = get_root_dir()
    for dirpath, dirnames, filenames in os.walk(root_dir):
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
    root_dir = get_root_dir()
    abs_path = os.path.abspath(os.path.join(root_dir, rel_path))

    if not abs_path.startswith(root_dir) or not os.path.isfile(abs_path):
        return "File not found", 404

    try:
        with open(abs_path, 'r', encoding="utf-8") as file:
            content = file.read()
        return content
    except:
        return "Cannot preview this file type", 400

@app.route("/recent")
def recent_files():
    root_dir = get_root_dir()
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            rel_path = os.path.relpath(fp, root_dir)
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