# Faculty Tool Box (FTB) - Educational Desktop Application

A modern Flask-based desktop application for educational institutions, providing access to Line Balancing modules, simulation tools, and learning resources.

## 🚀 Quick Start

### Download & Run
1. Download `EDU_Toolbox_Final.exe` from the `dist` folder
2. Double-click to run the application
3. Use demo credentials:
   - **Student**: Any email/password + any activation key
   - **Teacher**: Any email/password + any activation key

### Demo Mode
The application runs in demo mode - all login credentials are accepted for testing purposes.

## 📁 File Structure & Purpose

### Core Application Files
```
├── app.py                          # Main Flask application (CRITICAL)
├── requirements.txt                # Python dependencies
├── EDU_Toolbox_Final.spec         # PyInstaller build configuration
└── dist/
    └── EDU_Toolbox_Final.exe      # Final working executable
```

### User Interface Files
```
├── ui/
    ├── Login.html                  # Modern login page with gradient design
    ├── NividLogo.png              # Application logo
    ├── Student Panel/
    │   ├── Student_Dashboard.html  # Student main dashboard
    │   ├── Model_Library.html      # Student model library
    │   ├── My_Notes_Student.html   # Student notes interface
    │   └── Assignments_Student.html # Student assignments
    └── Teacher Panel/
        ├── Teacher_Dashboard.html  # Teacher main dashboard
        ├── Model_Library.html      # Teacher model library
        └── Students_Data.html      # Student progress tracking
```

### Runtime Data (Auto-created)
```
├── data/
│   └── user_data.db               # SQLite database (auto-created)
├── modules/
│   └── modules.json               # Module configuration (auto-created)
├── config/                        # Configuration files (auto-created)
└── assets/                        # Educational assets (auto-created)
```

## 🔧 Key Features

### Technical Architecture
- **Flask Backend**: Web server on port 8080 (avoids Windows restrictions)
- **Webview Frontend**: Native desktop wrapper for web interface
- **SQLite Database**: Local data storage for users, notes, progress
- **Session Management**: Secure login and user state management
- **Demo File Generation**: Creates Excel/PowerPoint/HTML demo files

### User Features
- **Modern UI**: Professional gradient design with responsive layout
- **Dual Login**: Separate interfaces for students and teachers
- **File Access**: Opens educational files (Excel, PowerPoint, Witness models)
- **Progress Tracking**: Student learning progress and module access
- **Notes System**: Student note-taking functionality
- **Exercise Management**: Teacher assignment creation and tracking

## 🛠️ Development Setup

### Prerequisites
```bash
pip install flask webview sqlite3 pathlib threading subprocess
```

### Run from Source
```bash
python app.py
```

### Build Executable
```bash
python -m PyInstaller --onefile --windowed --add-data "ui;ui" --name "EDU_Toolbox_Final" app.py
```

## 📋 File Descriptions

| File | Purpose | Critical |
|------|---------|----------|
| `app.py` | Main Flask application with all backend logic | ✅ YES |
| `ui/Login.html` | Modern login interface with styling | ✅ YES |
| `ui/Student Panel/*.html` | Student dashboard and interfaces | ✅ YES |
| `ui/Teacher Panel/*.html` | Teacher dashboard and interfaces | ✅ YES |
| `EDU_Toolbox_Final.exe` | Final working executable | ✅ YES |
| `requirements.txt` | Python dependencies list | ⚠️ Development |
| `EDU_Toolbox_Final.spec` | PyInstaller build configuration | ⚠️ Development |
| `data/user_data.db` | SQLite database (runtime) | 🔄 Auto-created |
| `modules/modules.json` | Module configuration (runtime) | 🔄 Auto-created |

## 🎯 Usage Instructions

### For End Users
1. **Download**: Get `EDU_Toolbox_Final.exe`
2. **Run**: Double-click the executable
3. **Login**: Use any credentials (demo mode)
4. **Navigate**: Access dashboards, libraries, and tools
5. **File Access**: Click on educational files to open demos

### For Developers
1. **Modify**: Edit `app.py` for backend changes
2. **UI Updates**: Modify HTML files in `ui/` folder
3. **Rebuild**: Use PyInstaller command to create new executable
4. **Test**: Run from source with `python app.py`

## 🔐 Security Features

- **Path Traversal Protection**: Prevents unauthorized file access
- **Role-Based Access**: Different permissions for students/teachers
- **File Type Validation**: Only allows approved educational file types
- **Session Security**: Secure cookie configuration
- **Input Validation**: Sanitized form inputs and API requests

## 🐛 Troubleshooting

### Common Issues
- **Black Screen**: Ensure port 8080 is available
- **File Access Denied**: Application creates demo files automatically
- **Login Issues**: Demo mode accepts any credentials
- **UI Not Loading**: Check `ui/` folder is present with executable

### Technical Notes
- Uses port 8080 instead of 5000 (Windows compatibility)
- Creates demo files for educational content
- Webview provides native desktop experience
- SQLite database for local data storage

## 📞 Support

For technical support or questions about the Faculty Tool Box application, please refer to the documentation or contact the development team.

---

**Version**: Final Release  
**Platform**: Windows Desktop  
**Technology**: Python Flask + Webview  
**License**: Educational Use