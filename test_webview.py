#!/usr/bin/env python3
"""
Simple webview test to check if webview is working
"""
import webview
import threading
import time
from flask import Flask

# Simple Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>Test Page</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 50px;
            }
            h1 { font-size: 3em; margin-bottom: 20px; }
            p { font-size: 1.2em; }
        </style>
    </head>
    <body>
        <h1>🎉 WEBVIEW IS WORKING! 🎉</h1>
        <p>If you can see this page, webview is functioning correctly.</p>
        <p>The issue is likely with the Flask app configuration or template loading.</p>
    </body>
    </html>
    '''

def start_flask():
    """Start Flask server"""
    try:
        app.run(host='127.0.0.1', port=8081, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Flask error: {e}")

if __name__ == '__main__':
    # Start Flask in background
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask to start
    time.sleep(2)
    
    # Create webview window
    webview.create_window(
        title='Webview Test',
        url='http://127.0.0.1:8081',
        width=800,
        height=600
    )
    
    # Start webview
    webview.start(debug=True)