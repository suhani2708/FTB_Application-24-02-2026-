#!/usr/bin/env python3
"""
EDU Toolbox - Multi-Module Flask Desktop Application
→ SECURITY HARDENED VERSION (Feb 2026)
→ FIXED: Critical Data Leak Vectors
→ All file access now REQUIRES login + strong path traversal protection
→ Role mismatch, expiry, and direct exposure completely blocked
"""

import os
import sys
import json
import sqlite3
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, send_from_directory, render_template_string
import webview
import traceback
import ctypes
import re
import hashlib
import hmac

# === UTF-8 Safety for Windows/.exe ===
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller compatibility"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(__file__).parent
    if os.name == 'nt':
        relative_path = relative_path.replace('/', '\\')
    return Path(base_path) / relative_path

# 🔑 LICENSE_SIGNING_KEY (MUST MATCH licence_generator.py!)
LICENSE_SIGNING_KEY = b"n1v1d_ultra_secure_key_2025_change_me_immediately_in_production!"

# 🔐 Verify activation code AND validate expiry from key
def verify_activation_code_new(activation_code):
    if not activation_code or len(activation_code) != 20 or activation_code[11] != '-':
        return None
       
    payload = activation_code[:11]      # anshT251226
    signature = activation_code[12:]    # UFBUGLGZ
   
    if len(payload) != 11 or len(signature) != 8:
        return None
       
    email_hint = payload[:4].lower()
    role_code = payload[4]
    exp_str = payload[5:11]  # 251226 (YYMMDD)
   
    if role_code not in ('S', 'T'):
        return None
       
    # ✅ EXTRACT AND VALIDATE EXPIRY FROM KEY
    try:
        year = int("20" + exp_str[:2])
        month = int(exp_str[2:4])
        day = int(exp_str[4:6])
       
        expiry_date = datetime(year, month, day).date()
        today = datetime.now().date()
       
        if expiry_date < today:
            print(f"❌ License expired: {expiry_date} < {today}")
            return None
    except (ValueError, IndexError) as e:
        print(f"❌ Invalid expiry format in key: {e}")
        return None
       
    # Verify signature
    expected_sig = generate_uppercase_signature(payload)
    if not hmac.compare_digest(signature, expected_sig):
        print("❌ Invalid signature")
        return None
       
    role = "teacher" if role_code == 'T' else "student"
    full_expiry = f"{year}-{month:02d}-{day:02d}"
    return email_hint, role, full_expiry

def generate_uppercase_signature(payload: str) -> str:
    """Generate 8-char uppercase signature from payload using HMAC-SHA256."""
    digest = hmac.new(
        LICENSE_SIGNING_KEY,
        payload.encode('utf-8'),
        hashlib.sha256
    ).digest()[:5]
    CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    num = int.from_bytes(digest, 'big')
    chars = []
    for _ in range(8):
        num, r = divmod(num, len(CHARS))
        chars.append(CHARS[r])
    return ''.join(reversed(chars))

# Get base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

app = Flask(__name__,
           template_folder=resource_path('ui'),
           static_folder=resource_path('static'))
app.secret_key = 'edu_toolbox_secure_key_2024_FIXED'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_PERMANENT'] = False

# ====================== SECURITY FIXES START ======================
def require_api_auth():
    """ALL file access (download + launch) now REQUIRES login"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "error": "Please login to access files"}), 401
    return None

def get_safe_file_path(filename: str):
    """STRONG Path Traversal Protection - prevents ../ attacks completely"""
    base_dir = resource_path("assets/models").resolve()
    
    # Sanitize filename
    safe_filename = os.path.normpath(filename).lstrip("/\\").replace("..", "_").replace("\\", "/")
    
    # Block absolute paths and dangerous patterns
    if os.path.isabs(safe_filename) or any(part in safe_filename for part in ["..", "~", ":", "*"]):
        raise ValueError("Access denied: Invalid path")
    
    full_path = (base_dir / safe_filename).resolve()
    
    # Critical check: must stay inside assets/models
    if not str(full_path).startswith(str(base_dir)):
        raise ValueError("Access denied: Path traversal attempt detected")
    
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    
    return full_path
# ====================== SECURITY FIXES END ======================

class EDUToolboxApp:
    def __init__(self):
        self.base_path = BASE_DIR
        self.data_path = (BASE_DIR / "data").resolve()
        self.data_path.mkdir(parents=True, exist_ok=True)
       
        self.ui_path = resource_path('ui')
        self.modules_path = resource_path('modules')
        self.assets_path = resource_path('assets')
        self.config_path = resource_path('config')
        self.config_path.mkdir(exist_ok=True)
        self.db_path = self.data_path / "user_data.db"
        self._ensure_directories()
        self.init_database()
        self.load_modules()
   
    def _ensure_directories(self):
        directories = [
            self.data_path,
            self.modules_path,
            self.assets_path,
            self.config_path,
            self.assets_path / "models",
            self.assets_path / "excel",
            self.assets_path / "guides",
            self.assets_path / "witness",
            self.assets_path / "icons"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
   
    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_key TEXT UNIQUE NOT NULL,
                    user_type TEXT NOT NULL,
                    name TEXT,
                    email TEXT,
                    password TEXT,
                    institution TEXT,
                    expiry TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    module_id TEXT,
                    title TEXT NOT NULL,
                    content TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    module_id TEXT,
                    due_date TEXT,
                    created_by INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    module_id TEXT,
                    progress_percentage INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    time_spent INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS module_access (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    module_id TEXT,
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exercise_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exercise_id INTEGER,
                    user_id INTEGER,
                    submission_text TEXT,
                    file_path TEXT,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    grade INTEGER,
                    feedback TEXT,
                    FOREIGN KEY (exercise_id) REFERENCES exercises (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
            except sqlite3.OperationalError:
                pass
            conn.commit()
        except Exception as e:
            print(f"ERROR initializing database: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
   
    def load_modules(self):
        modules_file = self.modules_path / "modules.json"
        if not modules_file.exists():
            default_modules = {
                "modules": [
                    {
                        "id": "line_balancing",
                        "name": "Line Balancing",
                        "description": "Production line optimization and workstation balancing",
                        "files": {
                            "excel": "Line balancing adv.xlsm",
                            "witness": "Line Balancing 3d clothing Mfg(after1).mod",
                            "guide": "User_Guide.pptx",
                            "problem": "Problem Statement_Line Balancing .docx",
                            "example": "Example Problem Statement & Step-by-step.docx",
                            "witness_export": "LB.wexp"
                        },
                        "access_level": ["student", "teacher"]
                    },
                    {
                        "id": "supply_chain",
                        "name": "Supply Chain Management",
                        "description": "Supply chain optimization and network design",
                        "files": {
                            "excel": "supply_chain_model.xlsm",
                            "guide": "Supply_Chain_Guide.pptx"
                        },
                        "access_level": ["student", "teacher"]
                    },
                    {
                        "id": "mrp",
                        "name": "Material Requirements Planning",
                        "description": "MRP calculations and inventory management",
                        "files": {
                            "excel": "mrp_calculator.xlsm",
                            "guide": "MRP_Guide.pptx"
                        },
                        "access_level": ["student", "teacher"]
                    }
                ]
            }
            with open(modules_file, 'w') as f:
                json.dump(default_modules, f, indent=2)
        try:
            with open(modules_file, 'r') as f:
                self.modules_config = json.load(f)
        except Exception as e:
            print(f"ERROR loading modules.json: {e}")
            self.modules_config = {"modules": []}
   
    def get_user_modules(self, user_type):
        accessible = []
        for mod in self.modules_config.get("modules", []):
            if user_type in mod.get("access_level", []) or "student" in mod.get("access_level", []):
                accessible.append(mod)
        return accessible
   
    def start_flask_server(self):
        app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False)
   
    def create_window(self):
        self.window = webview.create_window(
            title='Faculty Tool Box By Nivid Informatics Pvt Ltd',
            url='http://127.0.0.1:8080',
            width=1400,
            height=900,
            min_size=(1200, 800),
            resizable=True
        )
        try:
            icon_path = str(resource_path('ui/nividnewLogo.ico'))
            if Path(icon_path).exists():
                hwnd = webview.windows[0].hwnd
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, ctypes.wintypes.LPCWSTR(icon_path))
        except Exception as e:
            print(f"Icon set failed: {e}")
        return self.window
   
    def run(self):
        flask_thread = threading.Thread(target=self.start_flask_server, daemon=True)
        flask_thread.start()
        window = self.create_window()
        webview.start(debug=False)

edu_app = EDUToolboxApp()

def show_error_page(title, message, details=None, back_url="javascript:history.back()", logo_url="/static/Nividnewlogo.png"):
    details_html = ""
    if details:
        details_html = "<ul style='text-align: left; padding-left: 20px; margin: 10px 0;'>" + \
                      "".join(f"<li>{d}</li>" for d in details) + "</ul>"
   
    return render_template_string(f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html, body {{ height: 100%; overflow: hidden; font-family: Arial, sans-serif; }}
        .video-background {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; overflow: hidden; }}
        .video-background::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, rgba(255, 245, 235, 0.85) 0%, rgba(255, 228, 204, 0.85) 100%); z-index: 1; }}
        #bg-video {{ position: absolute; top: 50%; left: 50%; min-width: 100%; min-height: 100%; width: auto; height: auto; transform: translate(-50%, -50%); object-fit: cover; filter: brightness(0.6) contrast(1.2) saturate(1.3); z-index: 0; }}
        .overlay-particles {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; }}
        .particle {{ position: absolute; width: 4px; height: 4px; background: rgba(255, 140, 26, 0.6); border-radius: 50%; animation: floatParticle linear infinite; box-shadow: 0 0 8px rgba(255, 140, 26, 0.4); }}
        .particle:nth-child(1) {{ top: 20%; left: 10%; animation-duration: 15s; animation-delay: 0s; }}
        .particle:nth-child(2) {{ top: 40%; left: 30%; animation-duration: 12s; animation-delay: 2s; }}
        .particle:nth-child(3) {{ top: 60%; left: 50%; animation-duration: 18s; animation-delay: 4s; }}
        .particle:nth-child(4) {{ top: 30%; right: 20%; animation-duration: 14s; animation-delay: 1s; }}
        .particle:nth-child(5) {{ top: 70%; right: 40%; animation-duration: 16s; animation-delay: 3s; }}
        @keyframes floatParticle {{ 0% {{ transform: translateY(0) translateX(0) scale(1); opacity: 0; }} 10% {{ opacity: 1; }} 50% {{ transform: translateY(-50vh) translateX(30px) scale(1.5); }} 90% {{ opacity: 1; }} 100% {{ transform: translateY(-100vh) translateX(60px) scale(0.5); opacity: 0; }} }}
        .modal-container {{ display: flex; justify-content: center; align-items: center; height: 100vh; z-index: 3; position: relative; }}
        .modal {{ background: white; padding: 24px; border-radius: 8px; box-shadow: 0 6px 20px rgba(0,0,0,0.15); max-width: 420px; text-align: center; animation: modalFadeIn 0.5s ease-out forwards; }}
        @keyframes modalFadeIn {{ from {{ opacity: 0; transform: translateY(-20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .logo {{ width: 100px; height: 100px; margin-bottom: 16px; object-fit: contain; }}
        .modal h2 {{ color: #ff7b00; margin-top: 0; }}
        .modal p {{ line-height: 1.6; margin: 15px 0; }}
        .btn {{ background: #ff7b00; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 15px; font-weight: bold; }}
        .btn:hover {{ background: #e06d00; }}
        code {{ background: #f1f1f1; padding: 2px 4px; border-radius: 3px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="video-background">
        <video id="bg-video" autoplay loop muted playsinline>
            <source src="https://player.vimeo.com/external/374498877.sd.mp4?s=c4c731d99b0aa29909ec6893ac1f395e7db9d5f5&profile_id=165&oauth2_token_id=57447761" type="video/mp4">
        </video>
    </div>
    <div class="overlay-particles">
        <div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div>
    </div>
    <div class="modal-container">
        <div class="modal">
            <img src="{logo_url}" alt="Logo" class="logo">
            <h2>❌ {title}</h2>
            <p>{message}</p>
            {details_html}
            <a href="{back_url}" class="btn">Go Back</a>
        </div>
    </div>
</body>
</html>
''')

def get_user_id_from_session():
    if not session.get('logged_in'):
        return None, "User not logged in"
    raw_user_id = session.get('user_id')
    if raw_user_id is None:
        return None, "Session missing 'user_id'"
    try:
        user_id = int(raw_user_id)
        if user_id <= 0:
            raise ValueError("user_id must be positive")
    except (ValueError, TypeError):
        return None, f"Invalid user_id in session: {raw_user_id!r}"
    try:
        conn = sqlite3.connect(edu_app.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return None, f"User ID {user_id} not found in database"
    except Exception as e:
        return None, f"Database error during user validation: {e}"
    return user_id, None

# ✅ FIXED /login — Now includes role validation (student/teacher mismatch prevention)
@app.route('/login', methods=['POST'])
def login():
    try:
        activation_code = request.form.get('activation_code', '').strip()
        if not activation_code:
            return show_error_page(
                title="Activation Code Required",
                message="Please enter your 20-character activation code."
            ), 400
       
        result = verify_activation_code_new(activation_code)
        if not result:
            return show_error_page(
                title="Invalid or Expired License",
                message="Your activation code is invalid or has expired.",
                details=["Valid format: anshT251226-UFBUGLGZ", "Check if your license expiry date has passed"]
            ), 400
       
        email_hint, role, expiry_iso = result
       
        form_role = request.form.get('user_type')
        if form_role == 'student' and role != 'student':
            return show_error_page(
                title="Role Mismatch",
                message="This activation code is for a <strong>teacher</strong>, not a student.",
                details=["Please use the Teacher Login panel."]
            ), 403
        elif form_role == 'teacher' and role != 'teacher':
            return show_error_page(
                title="Role Mismatch",
                message="This activation code is for a <strong>student</strong>, not a teacher.",
                details=["Please use the Student Login panel."]
            ), 403
       
        conn = sqlite3.connect(edu_app.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, institution FROM users WHERE user_key = ?", (activation_code,))
        user_record = cursor.fetchone()
        if user_record:
            user_id, name, email, college = user_record
        else:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            college = request.form.get('college', '').strip()
            if not all([name, email, college]):
                conn.close()
                return show_error_page(
                    title="First-Time Login",
                    message="All fields are required for first-time activation:",
                    details=[" Full Name", " Email", " College"]
                ), 400
            # if not email.endswith('@gmail.com'):
            #     conn.close()
            #     return show_error_page(
            #         title="Invalid Email",
            #         message="Email must be a @gmail.com address."
            #     ), 400
            cursor.execute('''
                INSERT INTO users (user_key, user_type, name, email, institution, expiry)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (activation_code, role, name, email, college, expiry_iso))
            user_id = cursor.lastrowid
            conn.commit()
        conn.close()
       
        session.update({
            'logged_in': True,
            'role': role,
            'name': name,
            'email': email,
            'college': college,
            'user_id': user_id,
            'activation_code': activation_code,
            'expiry_date': expiry_iso
        })
        return redirect(f'/{role}/dashboard')
    except Exception as e:
        traceback.print_exc()
        return show_error_page(
            title="Server Error",
            message="An unexpected error occurred. Please try again."
        ), 500

# Flask Routes
@app.route('/')
def index():
    return render_template('Login.html')

def require_login(role=None):
    if not session.get('logged_in'):
        return redirect('/')
    if role and session.get('role') != role:
        return redirect('/')
    return None

@app.route('/student/dashboard')
def student_dashboard():
    if require_login('student'): return require_login('student')
    return render_template('Student Panel/Student_Dashboard.html')

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if require_login('teacher'): return require_login('teacher')
    return render_template('Teacher Panel/Teacher_Dashboard.html')

@app.route('/student/library')
def student_library():
    if require_login('student'): return require_login('student')
    return render_template('Student Panel/Model_Library.html')

@app.route('/student/notes')
def student_notes():
    if require_login('student'): return require_login('student')
    return render_template('Student Panel/My_Notes_Student.html')

@app.route('/student/exercises')
def student_exercises():
    if require_login('student'): return require_login('student')
    return render_template('Student Panel/Assignments_Student.html')

@app.route('/teacher/library')
def teacher_library():
    if require_login('teacher'): return require_login('teacher')
    return render_template('Teacher Panel/Model_Library.html')

@app.route('/teacher/students')
def teacher_students():
    if require_login('teacher'): return require_login('teacher')
    return render_template('Teacher Panel/Students_Data.html')

@app.route('/teacher/exercises')
def teacher_exercises():
    if require_login('teacher'): return require_login('teacher')
    return render_template('Teacher Panel/Assignments.html')

@app.route('/teacher/analytics')
def teacher_analytics():
    if require_login('teacher'): return require_login('teacher')
    return '<h1>Analytics</h1><p><a href="/teacher/dashboard">Back to Dashboard</a></p>'

# Redirect old HTML paths
@app.route('/Student_Dashboard.html')
def student_dashboard_html():
    return redirect('/student/dashboard')

@app.route('/Model_Library.html')
def student_model_library_html():
    return redirect('/student/library')

@app.route('/My_Notes_Student.html')
def student_notes_html():
    return redirect('/student/notes')

@app.route('/Assignments_Student.html')
def student_assignments_html():
    return redirect('/student/exercises')

@app.route('/Teacher_Dashboard.html')
def teacher_dashboard_html():
    return redirect('/teacher/dashboard')

@app.route('/teacher/Model_Library.html')
def teacher_model_library_html():
    return redirect('/teacher/library')

@app.route('/assignment.html')
def teacher_assignment_html():
    return redirect('/teacher/exercises')

@app.route('/api/modules')
def get_modules():
    user_type = session.get('role', 'student')
    modules = edu_app.get_user_modules(user_type)
    return jsonify({'modules': modules})

# ====================== FIXED FILE ACCESS ROUTES (CRITICAL) ======================
@app.route('/files/<path:filename>')
@app.route('/api/download_file/<path:filename>')
def serve_files(filename):
    # 1. Must be logged in
    auth = require_api_auth()
    if auth:
        return auth
    
    # 2. Strong path protection
    try:
        full_path = get_safe_file_path(filename)
        return send_file(str(full_path), as_attachment=True)
    except ValueError as e:
        return str(e), 403
    except FileNotFoundError:
        return "File not found", 404
    except Exception:
        return "Server error", 500

@app.route('/api/launch_file', methods=['POST'])
def launch_file():
    # 1. Must be logged in
    auth = require_api_auth()
    if auth:
        return auth
    
    data = request.get_json()
    file_path = data.get('file_path')
    if not file_path:
        return jsonify({"success": False, "error": "No file path"}), 400
    
    try:
        full_path = get_safe_file_path(file_path)
        if sys.platform == "win32":
            os.startfile(str(full_path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(full_path)])
        else:
            subprocess.Popen(["xdg-open", str(full_path)])
        return jsonify({"success": True})
    except (ValueError, FileNotFoundError) as e:
        return jsonify({"success": False, "error": str(e)}), 403 if "Access denied" in str(e) else 404
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to open file"}), 500
# ====================== END OF FIXED FILE ACCESS ======================

@app.route('/api/notes', methods=['GET', 'POST'])
@app.route('/api/notes/<int:note_id>', methods=['PUT', 'DELETE'])
def handle_notes(note_id=None):
    user_id, error = get_user_id_from_session()
    if error:
        return jsonify({"success": False, "error": error}), 401
    conn = sqlite3.connect(edu_app.db_path)
    cursor = conn.cursor()
    try:
        if request.method == 'GET':
            cursor.execute('SELECT id, title, content, tags, created_at FROM notes WHERE user_id = ? ORDER BY title', (user_id,))
            notes = [{"id": r[0], "title": r[1], "content": r[2], "tags": r[3] or "", "created_at": r[4]} for r in cursor.fetchall()]
            return jsonify({"notes": notes})
        elif request.method == 'POST':
            data = request.get_json()
            title = (data.get('title') or '').strip()
            content = (data.get('content') or '').strip()
            if not title or not content:
                return jsonify({"success": False, "error": "Title and content required"}), 400
            cursor.execute('INSERT INTO notes (user_id, module_id, title, content, tags) VALUES (?, ?, ?, ?, ?)', (user_id, 'general', title, content, data.get('tags', '')))
            note_id_new = cursor.lastrowid
            conn.commit()
            return jsonify({"success": True, "id": note_id_new})
        elif request.method == 'PUT' and note_id:
            data = request.get_json()
            title = (data.get('title') or '').strip()
            content = (data.get('content') or '').strip()
            if not title or not content:
                return jsonify({"success": False, "error": "Title and content required"}), 400
            cursor.execute('UPDATE notes SET title = ?, content = ?, tags = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?', (title, content, data.get('tags', ''), note_id, user_id))
            conn.commit()
            return jsonify({"success": cursor.rowcount > 0})
        elif request.method == 'DELETE' and note_id:
            cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
            conn.commit()
            return jsonify({"success": cursor.rowcount > 0})
        return jsonify({"error": "Invalid method"}), 405
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Logout</title>
        <script>
            history.replaceState(null, "", "/");
            window.location.replace("/");
        </script>
    </head>
    <body>
        <p>Logging out...</p>
        <noscript>
            <meta http-equiv="refresh" content="0;url=/">
            <p><a href="/">Go to Login</a></p>
        </noscript>
    </body>
    </html>
    '''

@app.route('/<path:filename>')
def catch_all(filename):
    static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico']
    if any(filename.endswith(ext) for ext in static_extensions):
        try:
            return send_from_directory(resource_path('static'), filename)
        except:
            return '', 404
    if filename.endswith('.html'):
        if 'Model_Library' in filename:
            return redirect('/student/library') if 'student' in filename.lower() else redirect('/teacher/library')
        elif 'My_Notes' in filename or 'Notes' in filename:
            return redirect('/student/notes')
        elif 'Assignments' in filename:
            return redirect('/student/exercises') if 'student' in filename.lower() else redirect('/teacher/exercises')
        elif 'Students_Data' in filename:
            return redirect('/teacher/students')
        elif 'Student_Dashboard' in filename:
            return redirect('/student/dashboard')
        elif 'Teacher_Dashboard' in filename:
            return redirect('/teacher/dashboard')
        elif 'Login' in filename:
            return redirect('/')
    return '', 404

if __name__ == '__main__':
    try:
        edu_app.run()
    except Exception as e:
        error_msg = f"CRITICAL ERROR: {e}\n{traceback.format_exc()}"
        log_path = Path(sys.executable).parent / "startup_error.log"
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(error_msg)
        input("Press Enter to exit...")
        sys.exit(1)