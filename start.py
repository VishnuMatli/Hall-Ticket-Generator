import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import os
import sys
import threading
import platform
import queue
import shutil
import time

class ModernControlDeck(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("MITS | Server Operations Center")
        self.geometry("1000x1000")
        self.configure(bg="#1e1e2e")  # Modern Dark Slate
        
        # --- ASSETS & CONFIG ---
        self.is_windows = platform.system() == "Windows"
        self.root_dir = os.getcwd()
        self.hall_ticket_web_dir = os.path.join(self.root_dir, "HallTicketWeb")
        
        # Paths
        if os.path.exists(os.path.join(self.root_dir, "views")):
            self.views_dir = os.path.join(self.root_dir, "views")
        else:
            self.views_dir = self.root_dir
            
        self.design_options = ["index.ejs", "index2.ejs", "index3.ejs", "index4.ejs", "index_old.ejs"]
        self.target_file = "index.ejs"
        self.backup_file = "_index_master_backup.ejs"
        
        # Venv Detection
        if self.is_windows:
            self.venv_python = os.path.join(self.root_dir, "hallenv", "Scripts", "python.exe")
        else:
            self.venv_python = os.path.join(self.root_dir, "hallenv", "bin", "python")

        if not os.path.exists(self.venv_python):
            self.venv_python = sys.executable

        # --- STATE ---
        self.processes = {}
        self.status_indicators = {} # Map process key to canvas widget
        self.log_queue = queue.Queue()
        self.protocol("WM_DELETE_WINDOW", self.shutdown_system)

        # --- STYLES ---
        self.setup_styles()
        
        # --- UI CONSTRUCTION ---
        self.create_header()
        self.create_dashboard()
        self.create_terminal()

        # --- LOOPS ---
        self.after(100, self.process_logs)
        self.after(1000, self.update_status_monitor) # Status heartbeat

    def setup_styles(self):
        """Define a clean, professional dark theme."""
        self.colors = {
            "bg_main": "#1e1e2e",       # Deep Slate
            "bg_card": "#2b2b3b",       # Lighter Slate
            "bg_term": "#11111b",       # Almost Black
            "primary": "#89b4fa",       # Soft Blue
            "success": "#a6e3a1",       # Soft Green
            "danger": "#f38ba8",        # Soft Red
            "warning": "#f9e2af",       # Soft Yellow
            "text": "#cdd6f4",          # White-ish
            "text_dim": "#a6adc8",      # Gray-ish
            "border": "#45475a"         # Border color
        }
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame Styles
        style.configure("Card.TFrame", background=self.colors["bg_card"], relief="flat")
        style.configure("Main.TFrame", background=self.colors["bg_main"])
        
        # Label Styles
        style.configure("Header.TLabel", background=self.colors["bg_main"], foreground=self.colors["text"], font=("Segoe UI", 16, "bold"))
        style.configure("SubHeader.TLabel", background=self.colors["bg_card"], foreground=self.colors["text_dim"], font=("Segoe UI", 10, "bold"))
        style.configure("Status.TLabel", background=self.colors["bg_card"], foreground=self.colors["text"], font=("Segoe UI", 11, "bold"))
        
        # Button Styles (TButton often has limitations, we use tk.Button for flat look usually, but let's try ttk)
        style.configure("Action.TButton", font=("Segoe UI", 9), padding=6)

    def create_header(self):
        header = tk.Frame(self, bg=self.colors["bg_main"], height=60, pady=15, padx=30)
        header.pack(fill="x")
        
        # Title
        tk.Label(header, text="SERVER OPERATIONS CENTER", bg=self.colors["bg_main"], fg=self.colors["text"], font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(header, text=" // MITS EXAM BRANCH", bg=self.colors["bg_main"], fg=self.colors["text_dim"], font=("Segoe UI", 14)).pack(side="left")
        
        # Shutdown
        btn_exit = tk.Button(
            header, text="⏻ SHUTDOWN", command=self.shutdown_system,
            bg=self.colors["danger"], fg="#111", relief="flat",
            font=("Segoe UI", 9, "bold"), padx=15, pady=5, cursor="hand2"
        )
        btn_exit.pack(side="right")

    def create_dashboard(self):
        main_frame = tk.Frame(self, bg=self.colors["bg_main"])
        main_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # --- SECTION 1: CONFIGURATION ---
        config_card = tk.Frame(main_frame, bg=self.colors["bg_card"], padx=20, pady=20)
        config_card.pack(fill="x", pady=(0, 20))
        
        # Rounded corners visual trick (optional, keeping it simple rectangular for reliability)
        
        tk.Label(config_card, text="INTERFACE CONFIGURATION", bg=self.colors["bg_card"], fg=self.colors["primary"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        
        config_row = tk.Frame(config_card, bg=self.colors["bg_card"])
        config_row.pack(fill="x", pady=(10, 0))
        
        tk.Label(config_row, text="Active UI Template:", bg=self.colors["bg_card"], fg=self.colors["text"]).pack(side="left", padx=(0, 10))
        
        self.design_var = tk.StringVar(value=self.design_options[0])
        self.design_combo = ttk.Combobox(config_row, textvariable=self.design_var, values=self.design_options, state="readonly", width=25)
        self.design_combo.pack(side="left")
        
        tk.Label(config_row, text="Selects the visual theme for the generated Hall Tickets.", bg=self.colors["bg_card"], fg=self.colors["text_dim"], font=("Segoe UI", 9, "italic")).pack(side="left", padx=15)

        # --- SECTION 2: PROCESS GRID ---
        grid_frame = tk.Frame(main_frame, bg=self.colors["bg_main"])
        grid_frame.pack(fill="x")
        
        # Define Services
        services = [
            ("HALL TICKET SERVER", "server.js", "Student protal for Hall Ticket generation", self.start_node_server, "NodeServer"),
            ("WEB INTERFACE", "app.py", "Web Portal for Database management", self.start_web_ui, "WebUI"),
            ("DATA MANAGER", "manager.py", "Database entry and modification tool", self.start_manage_ui, "ManageUI"),
            ("ADMIN CONSOLE", "admin_manager.py", "Admin accounts manager", self.start_admin_manager, "AdminManager"),
        ]

        # Create 2x2 Grid
        for i, (title, script, desc, cmd, key) in enumerate(services):
            row = i // 2
            col = i % 2
            self.create_service_card(grid_frame, title, script, desc, cmd, key, row, col)
            
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

    def create_service_card(self, parent, title, script, desc, start_cmd, process_key, row, col):
        card = tk.Frame(parent, bg=self.colors["bg_card"], padx=20, pady=20)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Header Row
        head = tk.Frame(card, bg=self.colors["bg_card"])
        head.pack(fill="x", pady=(0, 5))  # Fixed: mb=5 -> pady=(0, 5)
        
        tk.Label(head, text=title, bg=self.colors["bg_card"], fg=self.colors["text"], font=("Segoe UI", 12, "bold")).pack(side="left")
        
        # Status Dot
        status_frame = tk.Frame(head, bg=self.colors["bg_card"])
        status_frame.pack(side="right")
        
        dot = tk.Canvas(status_frame, width=12, height=12, bg=self.colors["bg_card"], highlightthickness=0)
        dot.create_oval(1, 1, 11, 11, fill="#444", outline="", tags="dot")
        dot.pack(side="right", padx=5)
        
        lbl_status = tk.Label(status_frame, text="OFFLINE", bg=self.colors["bg_card"], fg="#666", font=("Segoe UI", 8, "bold"))
        lbl_status.pack(side="right")
        
        # Store references for updates
        self.status_indicators[process_key] = {"canvas": dot, "label": lbl_status}
        
        # Script Name & Desc
        tk.Label(card, text=f"[{script}]", bg=self.colors["bg_card"], fg=self.colors["primary"], font=("Consolas", 9)).pack(anchor="w")
        tk.Label(card, text=desc, bg=self.colors["bg_card"], fg=self.colors["text_dim"], font=("Segoe UI", 9), wraplength=350, justify="left").pack(anchor="w", pady=(5, 15))
        
        # Controls
        btn_frame = tk.Frame(card, bg=self.colors["bg_card"])
        btn_frame.pack(fill="x", pady=(15, 0)) # Fixed: mt="auto" -> pady=(15, 0)
        
        tk.Button(
            btn_frame, text="▶ START SERVICE", command=start_cmd,
            bg=self.colors["border"], fg=self.colors["text"],
            activebackground=self.colors["success"], activeforeground="#111",
            relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"), height=2
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(
            btn_frame, text="⏹ STOP", command=lambda: self.stop_process(process_key),
            bg=self.colors["bg_main"], fg=self.colors["danger"],
            activebackground=self.colors["danger"], activeforeground="#fff",
            relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"), width=10, height=2
        ).pack(side="right", padx=(5, 0))

    def create_terminal(self):
        term_frame = tk.Frame(self, bg=self.colors["bg_main"])
        term_frame.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        
        tk.Label(term_frame, text="SYSTEM LOGS", bg=self.colors["bg_main"], fg=self.colors["text_dim"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5)) # Fixed: mb=5 -> pady=(0, 5)
        
        self.console = scrolledtext.ScrolledText(
            term_frame, bg=self.colors["bg_term"], fg=self.colors["text"],
            font=("Consolas", 9), relief="flat", bd=0, padx=10, pady=10
        )
        self.console.pack(fill="both", expand=True)
        
        # Log Tags
        self.console.tag_config("stderr", foreground=self.colors["danger"])
        self.console.tag_config("stdout", foreground=self.colors["text"])
        self.console.tag_config("system", foreground=self.colors["primary"])
        self.console.tag_config("success", foreground=self.colors["success"])
        self.console.tag_config("alert", foreground=self.colors["warning"])
        
        self.log_system(f"Control Deck Initialized on {platform.system()}.", "system")

    # --- LOGIC ---

    def apply_design_template(self):
        """Swaps the index.ejs file based on selection."""
        selected_design = self.design_var.get()
        target_path = os.path.join(self.views_dir, self.target_file)
        backup_path = os.path.join(self.views_dir, self.backup_file)
        
        if not os.path.exists(backup_path):
            if os.path.exists(target_path):
                try:
                    shutil.copy2(target_path, backup_path)
                    self.log_system(f"Backup created: {self.backup_file}", "system")
                except Exception as e:
                    self.log_system(f"Backup failed: {e}", "stderr")
                    return False
        
        if selected_design == "index.ejs":
            source_path = backup_path
            source_name = "Master Backup"
        else:
            source_path = os.path.join(self.views_dir, selected_design)
            source_name = selected_design

        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, target_path)
                self.log_system(f"Design Template Applied: {source_name}", "success")
                return True
            except Exception as e:
                self.log_system(f"Template Application Failed: {e}", "stderr")
                return False
        else:
            self.log_system(f"Template source not found: {selected_design}", "stderr")
            return False

    def run_process(self, name, command, cwd=None):
        if name in self.processes and self.processes[name].poll() is None:
            self.log_system(f"{name} is already running.", "alert")
            return

        def target():
            try:
                startupinfo = None
                if self.is_windows:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=cwd,
                    bufsize=1,
                    universal_newlines=True,
                    startupinfo=startupinfo
                )
                self.processes[name] = process
                self.log_system(f"Started service: {name} (PID: {process.pid})", "success")

                # Stream Output
                threading.Thread(target=self.stream_reader, args=(process.stdout, "stdout", name), daemon=True).start()
                threading.Thread(target=self.stream_reader, args=(process.stderr, "stderr", name), daemon=True).start()
                
                process.wait()
                
                # Cleanup after exit
                self.log_system(f"Service stopped: {name} (Code: {process.returncode})", "alert")
                if name in self.processes:
                    del self.processes[name]

            except Exception as e:
                self.log_system(f"Execution Error ({name}): {str(e)}", "stderr")

        threading.Thread(target=target, daemon=True).start()

    def stop_process(self, name):
        if name in self.processes:
            proc = self.processes[name]
            if proc.poll() is None:
                self.log_system(f"Stopping {name}...", "system")
                proc.terminate() 
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.log_system(f"Force killing {name}...", "stderr")
                    proc.kill()
            else:
                if name in self.processes: del self.processes[name]
        else:
            self.log_system(f"{name} is not active.", "alert")

    def shutdown_system(self):
        if messagebox.askokcancel("System Shutdown", "Terminate all services and exit?"):
            self.log_system("Initiating Shutdown...", "stderr")
            for name, proc in list(self.processes.items()):
                if proc.poll() is None:
                    proc.kill()
            self.destroy()
            sys.exit()

    def stream_reader(self, pipe, tag, name):
        try:
            for line in iter(pipe.readline, ''):
                if line: self.log_queue.put((tag, f"[{name}] {line}"))
                else: break
        finally:
            pipe.close()

    def process_logs(self):
        while not self.log_queue.empty():
            tag, msg = self.log_queue.get_nowait()
            self.console.insert(tk.END, msg, tag)
            self.console.see(tk.END)
        self.after(50, self.process_logs)

    def log_system(self, msg, tag="system"):
        self.log_queue.put((tag, f">> {msg}\n"))

    def update_status_monitor(self):
        """Updates the colored dots based on process status."""
        for key, widgets in self.status_indicators.items():
            is_running = key in self.processes and self.processes[key].poll() is None
            
            color = self.colors["success"] if is_running else "#444"
            text = "ONLINE" if is_running else "OFFLINE"
            text_color = self.colors["success"] if is_running else "#666"
            
            widgets["canvas"].itemconfigure("dot", fill=color)
            widgets["label"].config(text=text, fg=text_color)
            
        self.after(1000, self.update_status_monitor)

    # --- ACTIONS ---
    def start_node_server(self):
        self.apply_design_template()
        cmd = ["node", "server.js"]
        if self.is_windows: cmd = ["cmd", "/c", "node", "server.js"]
        self.run_process("NodeServer", cmd, cwd=self.root_dir)

    def start_web_ui(self):
        self.run_process("WebUI", [self.venv_python, "app.py"], cwd=self.hall_ticket_web_dir)

    def start_manage_ui(self):
        cwd = self.root_dir
        if not os.path.exists(os.path.join(self.root_dir, "manager.py")):
            if os.path.exists(os.path.join(self.hall_ticket_web_dir, "manager.py")):
                cwd = self.hall_ticket_web_dir
        self.run_process("ManageUI", [self.venv_python, "manager.py"], cwd=cwd)

    def start_admin_manager(self):
        self.run_process("AdminManager", [self.venv_python, "admin_manager.py"], cwd=self.hall_ticket_web_dir)

if __name__ == "__main__":
    app = ModernControlDeck()
    app.mainloop()