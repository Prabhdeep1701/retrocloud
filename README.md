
a📂 RETRO CLOUD

A simple web-based file upload and management system built using FastAPI. Users can:

Upload files via a web interface
View uploaded files
Delete files from the server (and the office folder)
📸 Preview
🧑‍💻 Web UI:
File Upload Form
File List with Delete Buttons
🚀 Features
📤 Upload files from browser
📁 Store files in a designated office folder
❌ Delete files via UI
📄 Clean HTML interface using Jinja2
🔒 Easily extensible for authentication & file type validation
🧱 Tech Stack
FastAPI
Uvicorn
Jinja2 Templates
Python 3.7+
📁 Project Structure
your_project/
│
├── app.py                  # Main FastAPI backend
├── templates/
│   └── index.html          # Frontend HTML using Jinja2
├── static/                 # (Optional) CSS, JS, assets
├── uploads/                # Temporary upload folder
└── README.md
⚙️ Setup Instructions
1. 📦 Install dependencies

pip install fastapi uvicorn jinja2
2. 📁 Set your office folder

In app.py, modify this line to your actual office path:

OFFICE_FOLDER = "/path/to/your/office/folder"
3. ▶️ Run the server

uvicorn app:app --reload
4. 🌐 Open in browser

Visit: http://localhost:8000

✨ Example Screenshot
Not included here — but you can easily add one by taking a screenshot of the running app and placing it in a /screenshots folder, then referencing it in this README:
![App Screenshot](screenshots/homepage.png)
🛡️ Security Notes
🚫 No auth is implemented — restrict access or add login before public deployment.
✅ Supports deletion of files via browser.
🔐 You can extend it with:
API Key or OAuth2 authentication
File size/type restrictions
Logging user uploads
📌 Future Improvements
File download button
User authentication
Progress bar on file upload
Upload file to cloud (S3, GDrive)
Scheduled auto-cleanup
👨‍💻 Author
Prabhdeep Singh
Open to collaborations on full-stack, DevOps, and cloud projects!

