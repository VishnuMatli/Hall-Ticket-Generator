import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk 
import mysql.connector
import pandas as pd
import bcrypt
import os
import math

# Try importing matplotlib for graphics
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ===================== CONFIGURATION & MITS THEME =====================
COLORS = {
    "bg_main": "#121212",         # Matte Black
    "bg_sidebar": "#1e1e1e",      # Dark Sidebar
    "bg_card": "#252526",         # Card Background (VS Code style)
    "fg_text": "#e0e0e0",         # Off-white text
    "fg_muted": "#858585",        # Muted Text
    "accent_primary": "#007acc",  # MITS Blue (Professional)
    "accent_secondary": "#0098ff",# Lighter Blue
    "danger": "#f44336",          # Material Red
    "success": "#4caf50",         # Material Green
    "warning": "#ff9800",         # Material Orange
    "entry_bg": "#3c3c3c",        # Input Background
    "entry_fg": "#ffffff",        # Input Text
    "border": "#333333",          # Subtle Border
    "hover": "#2a2d2e"            # Hover State
}

FONTS = {
    "header": ("Segoe UI", 24, "bold"),
    "subheader": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 10),
    "bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 10)
}

# ===================== DATABASE HELPER =====================
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "0407",           
    "database": "hall_ticket_db_university"
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("DB Connection Error", f"Could not connect to database: {err}")
        return None

def execute_query(query, params=(), fetch=False):
    conn = get_db_connection()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        if fetch:
            result = cur.fetchall()
            return result
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return None
    finally:
        if conn: conn.close()

# ===================== CUSTOM GRAPHIC WIDGETS =====================
class FlatButton(tk.Canvas):
    """A clean, professional flat button with hover effects"""
    def __init__(self, master, text, command, width=120, height=35, color=COLORS["accent_primary"], **kwargs):
        bg_color = kwargs.pop('bg', master['bg']) 
        super().__init__(master, width=width, height=height, bg=bg_color, highlightthickness=0, cursor="hand2", **kwargs)
        self.command = command
        self.text = text
        self.color = color
        self.width = width
        self.height = height
        self.base_bg = bg_color
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw(state="normal")

    def draw(self, state="normal"):
        self.delete("all")
        
        fill_color = self.color
        text_color = "white"
        
        if state == "hover":
            # Simple hover effect: draw a border line at bottom
            pass 

        # Draw Rounded Rectangle
        r = 4 # radius
        self.create_polygon(
            r, 0, self.width-r, 0,
            self.width, r, self.width, self.height-r,
            self.width-r, self.height, r, self.height,
            0, self.height-r, 0, r,
            fill=fill_color, outline="", tags="shape"
        )
        
        if state == "hover":
             self.create_line(r, self.height, self.width-r, self.height, fill="white", width=2)

        self.create_text(self.width/2, self.height/2, text=self.text, fill=text_color, font=FONTS["bold"], tags="text")

    def on_enter(self, e):
        self.draw(state="hover")

    def on_leave(self, e):
        self.draw(state="normal")

    def on_click(self, e):
        if self.command:
            self.command()

# ===================== AUTH SYSTEM =====================
def setup_auth_db():
    conn = get_db_connection()
    if not conn: return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
    """)
    cur.execute("SELECT * FROM admin_users WHERE username = 'admin'")
    if not cur.fetchone():
        hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        cur.execute("INSERT INTO admin_users (username, password_hash) VALUES (%s, %s)", 
                    ("admin", hashed.decode('utf-8')))
        conn.commit()
    conn.close()

def authenticate_user(username, password):
    rows = execute_query("SELECT password_hash FROM admin_users WHERE username=%s", (username,), fetch=True)
    if rows:
        stored_hash = rows[0][0].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True
    return False

# ===================== PASSWORD CHANGE DIALOG =====================
class ChangePasswordDialog(tk.Toplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.title("Change Password")
        self.geometry("400x450")
        self.configure(bg=COLORS["bg_card"])
        self.resizable(False, False)
        self.transient(parent)
        
        # FIX: Ensure window is visible before grabbing focus
        self.wait_visibility() 
        self.grab_set()
        
        self.current_user = current_user

        # Center
        x = parent.winfo_x() + 50
        y = parent.winfo_y() + 50
        self.geometry(f"+{x}+{y}")

        tk.Label(self, text="Change Password", font=("Segoe UI", 18, "bold"), 
                 bg=COLORS["bg_card"], fg="white").pack(pady=30)

        # Create input fields and store references
        self.ent_old = self.create_input("Current Password")
        self.ent_new = self.create_input("New Password")
        self.ent_confirm = self.create_input("Confirm New")

        FlatButton(self, "Update", self.save_password, width=200, height=40, color=COLORS["success"], bg=COLORS["bg_card"]).pack(pady=30)

    def create_input(self, label_text):
        frame = tk.Frame(self, bg=COLORS["bg_card"])
        frame.pack(fill="x", padx=40, pady=5)
        
        tk.Label(frame, text=label_text, font=FONTS["bold"], bg=COLORS["bg_card"], fg=COLORS["fg_muted"]).pack(anchor="w")
        
        # Explicit height via ipady and standard relief to ensure visibility
        ent = tk.Entry(frame, font=("Segoe UI", 11), bg=COLORS["entry_bg"], fg="white", 
                       insertbackground="white", relief="solid", bd=1, show="●")
        ent.pack(fill="x", pady=(5, 0), ipady=4)
        return ent

    def save_password(self):
        old = self.ent_old.get().strip()
        new = self.ent_new.get().strip()
        confirm = self.ent_confirm.get().strip()

        if not old or not new or not confirm:
            messagebox.showwarning("Error", "All fields are required.")
            return

        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match.")
            return

        if authenticate_user(self.current_user, old):
            new_hashed = bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            if execute_query("UPDATE admin_users SET password_hash=%s WHERE username=%s", (new_hashed, self.current_user)):
                messagebox.showinfo("Success", "Password updated successfully!")
                self.destroy()
        else:
            messagebox.showerror("Error", "Incorrect current password.")

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MITS Admin Login")
        self.geometry("900x600")
        self.configure(bg=COLORS["bg_main"])
        self.resizable(False, False)
        self._center_window()

        self.canvas = tk.Canvas(self, bg=COLORS["bg_main"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.create_rectangle(0, 0, 900, 300, fill=COLORS["bg_sidebar"], outline="")

        self.frame = tk.Frame(self.canvas, bg=COLORS["bg_card"], padx=60, pady=60)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(self.frame, text="MITS University", font=("Segoe UI", 36, "bold"), 
                 bg=COLORS["bg_card"], fg=COLORS["accent_primary"]).pack(pady=(0, 5))
        tk.Label(self.frame, text="MADANAPALLE INSTITUTE OF TECHNOLOGY & SCIENCE", font=("Segoe UI", 8, "bold"), 
                 bg=COLORS["bg_card"], fg=COLORS["fg_muted"]).pack(pady=(0, 40))

        self._create_label(self.frame, "USERNAME")
        self.ent_user = self._create_entry(self.frame)
        self.ent_user.pack(pady=(5, 20))
        self.ent_user.focus()

        self._create_label(self.frame, "PASSWORD")
        self.ent_pass = self._create_entry(self.frame, show="●")
        self.ent_pass.pack(pady=(5, 30))

        FlatButton(self.frame, "LOGIN", self.login, width=280, height=45, bg=COLORS["bg_card"]).pack(pady=10)
        self.bind('<Return>', lambda e: self.login())

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_label(self, parent, text):
        tk.Label(parent, text=text, font=FONTS["bold"], bg=COLORS["bg_card"], fg=COLORS["fg_muted"]).pack(anchor="w")

    def _create_entry(self, parent, **kwargs):
        ent = tk.Entry(parent, font=("Segoe UI", 11), bg=COLORS["entry_bg"], fg="white", 
                        relief="flat", width=30, insertbackground="white", **kwargs)
        return ent

    def login(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        
        if authenticate_user(user, pwd):
            self.destroy()
            DashboardApp(user).mainloop()
        else:
            messagebox.showerror("Access Denied", "Invalid Credentials")

# ===================== MAIN DASHBOARD =====================
class DashboardApp(tk.Tk):
    def __init__(self, current_user):
        super().__init__()
        self.title(f"MITS Admin Console | User: {current_user}")
        self.geometry("1400x900")
        self.configure(bg=COLORS["bg_main"])
        self.current_user = current_user
        
        self._setup_styles()
        self._setup_sidebar()
        self._setup_main_area()
        self.show_view("Home")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", 
                        background=COLORS["bg_main"], 
                        foreground="white", 
                        fieldbackground=COLORS["bg_main"], 
                        borderwidth=0, 
                        rowheight=40, 
                        font=FONTS["body"])
        
        style.configure("Treeview.Heading", 
                        background=COLORS["bg_card"], 
                        foreground=COLORS["fg_text"], 
                        font=FONTS["bold"], 
                        relief="flat")
        
        style.map("Treeview", 
                  background=[("selected", COLORS["accent_primary"])],
                  foreground=[("selected", "white")])
        
        style.configure("TCombobox", 
                        fieldbackground=COLORS["entry_bg"], 
                        background=COLORS["bg_card"], 
                        foreground="white",
                        arrowcolor="white",
                        borderwidth=0)
        
        style.map('TCombobox', fieldbackground=[('readonly', COLORS["entry_bg"])],
                  selectbackground=[('readonly', COLORS["entry_bg"])],
                  selectforeground=[('readonly', "white")])

    def _setup_sidebar(self):
        sb = tk.Frame(self, bg=COLORS["bg_sidebar"], width=280, bd=0)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        
        tk.Frame(sb, bg=COLORS["border"], width=1).pack(side="right", fill="y")

        logo_frame = tk.Frame(sb, bg=COLORS["bg_sidebar"], pady=30)
        logo_frame.pack(fill="x")
        
        try:
            if os.path.exists("MITS-Logo.png"):
                load = Image.open("MITS-Logo.png")
                load = load.resize((80, 80), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(load)
                tk.Label(logo_frame, image=self.logo_img, bg=COLORS["bg_sidebar"]).pack()
        except Exception as e:
            print(f"Logo load error: {e}")

        tk.Label(logo_frame, text="MITS", font=("Segoe UI", 24, "bold"), 
                 bg=COLORS["bg_sidebar"], fg="white").pack(pady=(10, 0))
        tk.Label(logo_frame, text="ADMIN CONSOLE", font=("Segoe UI", 10), 
                 bg=COLORS["bg_sidebar"], fg=COLORS["accent_primary"]).pack()

        nav_container = tk.Frame(sb, bg=COLORS["bg_sidebar"])
        nav_container.pack(fill="x", pady=20)

        nav_items = [
            ("Dashboard", "Home"),
            ("Departments", "Department"),
            ("Students", "Student"),
            ("Subjects", "Subject"),
            ("Promotions", "Promotion")
        ]

        for text, view in nav_items:
            self._add_nav_btn(nav_container, text, lambda v=view: self.show_view(v))

        footer = tk.Frame(sb, bg=COLORS["bg_sidebar"], pady=20)
        footer.pack(side="bottom", fill="x")
        tk.Label(footer, text=f"User: {self.current_user}", bg=COLORS["bg_sidebar"], 
                 fg=COLORS["fg_muted"], font=FONTS["small"]).pack()
        
        FlatButton(footer, "Change Password", self.open_change_password, width=200, height=35, color=COLORS["warning"], bg=COLORS["bg_sidebar"]).pack(pady=5)
        FlatButton(footer, "Logout", self.logout, width=200, height=35, color=COLORS["danger"], bg=COLORS["bg_sidebar"]).pack(pady=5)

    def _add_nav_btn(self, parent, text, command):
        btn = FlatButton(parent, text, command, width=240, height=45, color=COLORS["bg_card"], bg=COLORS["bg_sidebar"])
        btn.pack(pady=5)

    def _setup_main_area(self):
        self.container = tk.Frame(self, bg=COLORS["bg_main"])
        self.container.pack(side="right", fill="both", expand=True)
        self.views = {}
        for F in (HomeView, DepartmentView, StudentView, SubjectView, PromotionView):
            name = F.__name__.replace("View", "")
            view = F(self.container, self)
            self.views[name] = view
            view.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def show_view(self, name):
        if name in self.views:
            view = self.views[name]
            view.tkraise()
            if hasattr(view, "refresh"): view.refresh()

    def open_change_password(self):
        ChangePasswordDialog(self, self.current_user)

    def logout(self):
        self.destroy()
        LoginWindow().mainloop()

# ===================== VIEWS =====================

class BaseView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.controller = controller
        
    def add_header(self, title, subtitle=""):
        f = tk.Frame(self, bg=COLORS["bg_main"], pady=20, padx=40)
        f.pack(fill="x")
        
        tk.Label(f, text=title, font=FONTS["header"], bg=COLORS["bg_main"], fg="white").pack(anchor="w")
        if subtitle:
            tk.Label(f, text=subtitle, font=FONTS["body"], bg=COLORS["bg_main"], fg=COLORS["fg_muted"]).pack(anchor="w")
        
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=40)

    def create_input(self, parent, width=None):
        e = tk.Entry(parent, bg=COLORS["entry_bg"], fg="white", 
                     insertbackground="white", relief="flat", font=FONTS["body"])
        if width: e.config(width=width)
        return e

    def create_tree(self, parent, columns):
        container = tk.Frame(parent, bg=COLORS["bg_main"], bd=1, relief="solid") 
        container.pack(fill="both", expand=True)

        tree = ttk.Treeview(container, columns=columns, show="headings", selectmode="extended")
        
        ysb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        xsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        
        ysb.pack(side="right", fill="y")
        xsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").upper())
            tree.column(col, width=120, anchor="w")
        return tree

class HomeView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_header("Dashboard", "Overview of College Metrics")
        
        stats_frame = tk.Frame(self, bg=COLORS["bg_main"], padx=40, pady=20)
        stats_frame.pack(fill="x")
        
        self.cards = {}
        self._create_stat_card(stats_frame, "Departments", COLORS["accent_primary"], 0)
        self._create_stat_card(stats_frame, "Students", COLORS["success"], 1)
        self._create_stat_card(stats_frame, "Subjects", COLORS["warning"], 2)

        self.chart_area = tk.Frame(self, bg=COLORS["bg_main"], padx=40, pady=20)
        self.chart_area.pack(fill="both", expand=True)

    def _create_stat_card(self, parent, title, color, col):
        card = tk.Frame(parent, bg=COLORS["bg_card"], height=120, width=300)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        card.pack_propagate(False)
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Frame(card, bg=color, width=5).pack(side="left", fill="y")
        
        content = tk.Frame(card, bg=COLORS["bg_card"], padx=20)
        content.pack(side="left", fill="both", expand=True)
        
        tk.Label(content, text=title.upper(), font=FONTS["bold"], bg=COLORS["bg_card"], fg=COLORS["fg_muted"]).pack(anchor="w", pady=(20, 5))
        lbl_val = tk.Label(content, text="0", font=("Segoe UI", 36, "bold"), bg=COLORS["bg_card"], fg="white")
        lbl_val.pack(anchor="w")
        
        self.cards[title] = lbl_val

    def refresh(self):
        counts = {
            "Departments": "SELECT COUNT(*) FROM departments",
            "Students": "SELECT COUNT(*) FROM students",
            "Subjects": "SELECT COUNT(*) FROM subjects"
        }
        for key, query in counts.items():
            res = execute_query(query, fetch=True)
            if res: self.cards[key].config(text=str(res[0][0]))

        if not MATPLOTLIB_AVAILABLE: return
        for w in self.chart_area.winfo_children(): w.destroy()

        data = execute_query("SELECT department, COUNT(*) FROM students GROUP BY department", fetch=True)
        if not data: return

        depts = [d[0] for d in data]
        vals = [d[1] for d in data]

        fig = Figure(figsize=(10, 4), dpi=100, facecolor=COLORS["bg_main"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["bg_card"])
        ax.bar(depts, vals, color=COLORS["accent_primary"])
        
        ax.set_title("Student Distribution by Department", color="white", pad=20)
        ax.tick_params(colors="white")
        ax.spines['bottom'].set_color(COLORS["border"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLORS["border"])

        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

class DepartmentView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_header("Departments", "Manage Academic Departments")
        
        toolbar = tk.Frame(self, bg=COLORS["bg_main"], padx=40, pady=10)
        toolbar.pack(fill="x")
        
        self.ent_name = self.create_input(toolbar, width=30)
        self.ent_name.pack(side="left", padx=(0, 10))
        
        FlatButton(toolbar, "Add Department", self.add, width=140, height=30, color=COLORS["success"], bg=COLORS["bg_main"]).pack(side="left")
        FlatButton(toolbar, "Delete Selected", self.delete, width=140, height=30, color=COLORS["danger"], bg=COLORS["bg_main"]).pack(side="right")
        
        tree_frame = tk.Frame(self, bg=COLORS["bg_main"], padx=40, pady=10)
        tree_frame.pack(fill="both", expand=True)
        self.tree = self.create_tree(tree_frame, ["ID", "Name"])

    def refresh(self):
        rows = execute_query("SELECT id, name FROM departments ORDER BY id", fetch=True)
        self.tree.delete(*self.tree.get_children())
        if rows:
            for r in rows: self.tree.insert("", "end", values=r)

    def add(self):
        val = self.ent_name.get().strip()
        if val:
            if execute_query("INSERT INTO departments (name) VALUES (%s)", (val,)):
                self.ent_name.delete(0, 'end')
                self.refresh()

    def delete(self):
        sel = self.tree.selection()
        if sel:
            if messagebox.askyesno("Confirm", "Delete selected department?"):
                did = self.tree.item(sel[0])['values'][0]
                execute_query("DELETE FROM departments WHERE id=%s", (did,))
                self.refresh()

class StudentView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_header("Students", "Manage Student Records")
        
        toolbar = tk.Frame(self, bg=COLORS["bg_main"], padx=40, pady=10)
        toolbar.pack(fill="x")
        
        tk.Label(toolbar, text="Dept:", bg=COLORS["bg_main"], fg=COLORS["fg_muted"]).pack(side="left")
        self.cb_dept = ttk.Combobox(toolbar, width=15, state="readonly"); self.cb_dept.pack(side="left", padx=5)
        
        tk.Label(toolbar, text="Sem:", bg=COLORS["bg_main"], fg=COLORS["fg_muted"]).pack(side="left")
        self.cb_sem = ttk.Combobox(toolbar, width=10, state="readonly"); self.cb_sem.pack(side="left", padx=5)
        
        FlatButton(toolbar, "Filter", self.refresh, width=80, height=30, bg=COLORS["bg_main"]).pack(side="left", padx=5)
        
        FlatButton(toolbar, "Delete Selected", self.delete, width=120, height=30, color=COLORS["danger"], bg=COLORS["bg_main"]).pack(side="right", padx=5)
        FlatButton(toolbar, "Edit Selected", self.edit_selected, width=120, height=30, color=COLORS["warning"], bg=COLORS["bg_main"]).pack(side="right", padx=5)
        FlatButton(toolbar, "Export Excel", self.export_excel, width=120, height=30, color=COLORS["accent_secondary"], bg=COLORS["bg_main"]).pack(side="right", padx=5)
        FlatButton(toolbar, "Add Student", self.show_add_overlay, width=120, height=30, color=COLORS["success"], bg=COLORS["bg_main"]).pack(side="right", padx=5)

        content = tk.Frame(self, bg=COLORS["bg_main"], padx=40, pady=10)
        content.pack(fill="both", expand=True)
        self.tree = self.create_tree(content, ["Roll_No", "Name", "Dept", "Sem", "Year", "Regulation", "Mobile"])

        self.overlay = tk.Frame(self, bg=COLORS["bg_card"], bd=1, relief="solid")
        self.setup_form()

    def setup_form(self):
        tk.Label(self.overlay, text="Student Record Form", font=FONTS["subheader"], bg=COLORS["bg_card"], fg="white").pack(pady=20)
        
        form_frame = tk.Frame(self.overlay, bg=COLORS["bg_card"])
        form_frame.pack(fill="both", expand=True, padx=50)
        
        self.entries = {}
        fields = ["Roll Number", "Name", "Father Name", "DOB (YYYY-MM-DD)", "Gender", "Mobile", "Department", "Regulation", "Year", "Semester", "Section"]
        
        for i, f in enumerate(fields):
            row = i // 2
            col = i % 2
            
            cont = tk.Frame(form_frame, bg=COLORS["bg_card"])
            cont.grid(row=row, column=col, sticky="ew", padx=10, pady=10)
            form_frame.grid_columnconfigure(col, weight=1)
            
            tk.Label(cont, text=f, font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["fg_muted"]).pack(anchor="w")
            
            if f in ["Department", "Semester", "Gender", "Regulation"]:
                e = ttk.Combobox(cont, state="readonly")
            else:
                e = self.create_input(cont)
            e.pack(fill="x", pady=(5,0))
            self.entries[f] = e

        action_frame = tk.Frame(self.overlay, bg=COLORS["bg_card"], pady=20)
        action_frame.pack(fill="x", padx=50)
        
        FlatButton(action_frame, "Save", self.save_student, width=150, height=40, color=COLORS["success"], bg=COLORS["bg_card"]).pack(side="right")
        FlatButton(action_frame, "Cancel", self.hide_overlay, width=100, height=40, color=COLORS["danger"], bg=COLORS["bg_card"]).pack(side="right", padx=10)

    def show_add_overlay(self):
        depts = [d[0] for d in execute_query("SELECT name FROM departments", fetch=True) or []]
        sems = [s[0] for s in execute_query("SELECT name FROM semesters", fetch=True) or []]
        self.entries["Department"]['values'] = depts
        self.entries["Semester"]['values'] = sems
        self.entries["Gender"]['values'] = ["Male", "Female"]
        self.entries["Regulation"]['values'] = ["R23", "R20", "R19"]
        
        self.overlay.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        self.overlay.lift()

    def hide_overlay(self):
        self.overlay.place_forget()
        for e in self.entries.values():
            if isinstance(e, ttk.Combobox): e.set('')
            else: e.delete(0, 'end')

    def save_student(self):
        data = [self.entries[f].get() for f in ["Roll Number", "Name", "Father Name", "DOB (YYYY-MM-DD)", "Gender", "Mobile", "Department", "Regulation", "Year", "Semester", "Section"]]
        if not data[0] or not data[1]: return messagebox.showerror("Error", "Roll No & Name required")
        
        sql = """INSERT INTO students (roll_number, name, father_name, dob, gender, mobile, department, regulation, year, semester, section)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                 ON DUPLICATE KEY UPDATE name=VALUES(name), father_name=VALUES(father_name), dob=VALUES(dob), gender=VALUES(gender), mobile=VALUES(mobile), department=VALUES(department), regulation=VALUES(regulation), year=VALUES(year), semester=VALUES(semester), section=VALUES(section)"""
        
        if execute_query(sql, tuple(data)):
            messagebox.showinfo("Success", "Student Saved")
            self.hide_overlay()
            self.refresh()

    def refresh(self):
        depts = execute_query("SELECT name FROM departments", fetch=True)
        self.cb_dept['values'] = [d[0] for d in depts] if depts else []
        sems = execute_query("SELECT name FROM semesters", fetch=True)
        self.cb_sem['values'] = [s[0] for s in sems] if sems else []
        
        sql = "SELECT roll_number, name, department, semester, year, regulation, mobile FROM students WHERE 1=1"
        params = []
        if self.cb_dept.get(): sql += " AND department=%s"; params.append(self.cb_dept.get())
        if self.cb_sem.get(): sql += " AND semester=%s"; params.append(self.cb_sem.get())
        
        rows = execute_query(sql, tuple(params), fetch=True)
        self.tree.delete(*self.tree.get_children())
        if rows:
            for r in rows: self.tree.insert("", "end", values=r)

    def delete(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", f"Delete {len(sel)} students?"):
            for item in sel:
                roll = self.tree.item(item)['values'][0]
                execute_query("DELETE FROM students WHERE roll_number=%s", (str(roll),))
            self.refresh()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel: return
        if len(sel) > 1: return messagebox.showwarning("Warning", "Select only one student to edit")
        
        roll = self.tree.item(sel[0])['values'][0]
        # CAUTION: Fetch explicit columns to avoid mismatch
        query = "SELECT roll_number, name, father_name, dob, gender, mobile, department, regulation, year, semester, section FROM students WHERE roll_number=%s"
        row = execute_query(query, (str(roll),), fetch=True)
        if not row: return
        
        self.show_add_overlay()
        r = row[0] 
        # r indices: 0:roll, 1:name, 2:father, 3:dob, 4:gender, 5:mobile, 6:dept, 7:reg, 8:year, 9:sem, 10:sec
        try:
            self.entries["Roll Number"].delete(0, 'end'); self.entries["Roll Number"].insert(0, r[0])
            self.entries["Name"].delete(0, 'end'); self.entries["Name"].insert(0, r[1])
            self.entries["Father Name"].delete(0, 'end'); self.entries["Father Name"].insert(0, r[2])
            self.entries["DOB (YYYY-MM-DD)"].delete(0, 'end'); self.entries["DOB (YYYY-MM-DD)"].insert(0, str(r[3])) # Convert date to string
            self.entries["Gender"].set(r[4])
            self.entries["Mobile"].delete(0, 'end'); self.entries["Mobile"].insert(0, r[5])
            self.entries["Department"].set(r[6])
            self.entries["Regulation"].set(r[7])
            self.entries["Year"].delete(0, 'end'); self.entries["Year"].insert(0, r[8])
            self.entries["Semester"].set(r[9])
            self.entries["Section"].delete(0, 'end'); self.entries["Section"].insert(0, r[10])
        except Exception as e:
            print(f"Fill error: {e}")

    def export_excel(self):
        pass 

class SubjectView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_header("Subjects", "Curriculum Management")
        
        toolbar = tk.Frame(self, bg=COLORS["bg_main"], padx=40, pady=10)
        toolbar.pack(fill="x")
        
        tk.Label(toolbar, text="Dept:", bg=COLORS["bg_main"], fg=COLORS["fg_muted"]).pack(side="left")
        self.cb_dept = ttk.Combobox(toolbar, width=15); self.cb_dept.pack(side="left", padx=5)
        
        tk.Label(toolbar, text="Sem:", bg=COLORS["bg_main"], fg=COLORS["fg_muted"]).pack(side="left")
        self.cb_sem = ttk.Combobox(toolbar, width=10); self.cb_sem.pack(side="left", padx=5)
        
        FlatButton(toolbar, "Load", self.refresh, width=80, height=30, bg=COLORS["bg_main"]).pack(side="left", padx=5)
        FlatButton(toolbar, "Delete Selected", self.delete_single, width=120, height=30, color=COLORS["danger"], bg=COLORS["bg_main"]).pack(side="right", padx=5)
        FlatButton(toolbar, "Edit Selected", self.edit_single, width=120, height=30, color=COLORS["warning"], bg=COLORS["bg_main"]).pack(side="right", padx=5)
        FlatButton(toolbar, "Delete Batch", self.delete_batch, width=120, height=30, color=COLORS["danger"], bg=COLORS["bg_main"]).pack(side="right", padx=5)

        content = tk.Frame(self, bg=COLORS["bg_main"], padx=40, pady=10)
        content.pack(fill="both", expand=True)
        self.tree = self.create_tree(content, ["ID", "Code", "Name", "Dept", "Sem", "Reg"])

        self.overlay = tk.Frame(self, bg=COLORS["bg_card"], bd=1, relief="solid")
        self.setup_edit_form()

    def setup_edit_form(self):
        tk.Label(self.overlay, text="Edit Subject", font=FONTS["subheader"], bg=COLORS["bg_card"], fg="white").pack(pady=20)
        self.edit_entries = {}
        for f in ["Subject Code", "Subject Name"]:
            tk.Label(self.overlay, text=f, bg=COLORS["bg_card"], fg="white").pack()
            e = self.create_input(self.overlay, width=40)
            e.pack(pady=5)
            self.edit_entries[f] = e
        
        self.current_edit_id = None
        FlatButton(self.overlay, "Save Changes", self.save_edit, width=150, height=35, color=COLORS["success"], bg=COLORS["bg_card"]).pack(pady=20)
        FlatButton(self.overlay, "Cancel", lambda: self.overlay.place_forget(), width=100, height=35, color=COLORS["danger"], bg=COLORS["bg_card"]).pack()

    def refresh(self):
        depts = execute_query("SELECT name FROM departments", fetch=True)
        self.cb_dept['values'] = [d[0] for d in depts] if depts else []
        sems = execute_query("SELECT name FROM semesters", fetch=True)
        self.cb_sem['values'] = [s[0] for s in sems] if sems else []
        
        sql = "SELECT id, subject_code, subject_name, department, semester, regulation FROM subjects WHERE 1=1"
        params = []
        if self.cb_dept.get(): sql += " AND department=%s"; params.append(self.cb_dept.get())
        if self.cb_sem.get(): sql += " AND semester=%s"; params.append(self.cb_sem.get())
        
        rows = execute_query(sql, tuple(params), fetch=True)
        self.tree.delete(*self.tree.get_children())
        if rows:
            for r in rows: self.tree.insert("", "end", values=r)

    def delete_single(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", "Delete selected subject?"):
            sid = self.tree.item(sel[0])['values'][0]
            execute_query("DELETE FROM subjects WHERE id=%s", (sid,))
            self.refresh()

    def delete_batch(self):
        pass

    def edit_single(self):
        sel = self.tree.selection()
        if not sel: return
        if len(sel) > 1: return
        
        vals = self.tree.item(sel[0])['values']
        self.current_edit_id = vals[0]
        self.edit_entries["Subject Code"].delete(0, 'end'); self.edit_entries["Subject Code"].insert(0, vals[1])
        self.edit_entries["Subject Name"].delete(0, 'end'); self.edit_entries["Subject Name"].insert(0, vals[2])
        
        self.overlay.place(relx=0.3, rely=0.3, relwidth=0.4, relheight=0.4)
        self.overlay.lift()

    def save_edit(self):
        code = self.edit_entries["Subject Code"].get()
        name = self.edit_entries["Subject Name"].get()
        if execute_query("UPDATE subjects SET subject_code=%s, subject_name=%s WHERE id=%s", (code, name, self.current_edit_id)):
            self.overlay.place_forget()
            self.refresh()

class PromotionView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_header("Promotions", "Batch Year Advancement")
        
        container = tk.Frame(self, bg=COLORS["bg_card"], padx=60, pady=60)
        container.pack(expand=True)
        
        tk.Label(container, text="Target Department", bg=COLORS["bg_card"], fg=COLORS["fg_muted"]).pack(anchor="w")
        self.cb_dept = ttk.Combobox(container, width=40); self.cb_dept.pack(pady=10)
        
        tk.Label(container, text="Current Semester", bg=COLORS["bg_card"], fg=COLORS["fg_muted"]).pack(anchor="w")
        self.cb_sem = ttk.Combobox(container, width=40); self.cb_sem.pack(pady=10)
        self.cb_sem.bind("<<ComboboxSelected>>", self.update_label)
        
        self.lbl_info = tk.Label(container, text="Select semester...", bg=COLORS["bg_card"], fg=COLORS["accent_primary"], font=FONTS["bold"])
        self.lbl_info.pack(pady=20)
        
        FlatButton(container, "Promote Batch", self.promote, width=300, height=45, color=COLORS["success"], bg=COLORS["bg_card"]).pack(pady=5)
        FlatButton(container, "Demote Batch", self.demote, width=300, height=45, color=COLORS["danger"], bg=COLORS["bg_card"]).pack(pady=5)
        
        self.refresh()

    def refresh(self):
        depts = execute_query("SELECT name FROM departments", fetch=True)
        self.cb_dept['values'] = ["ALL"] + [d[0] for d in depts] if depts else []
        sems = execute_query("SELECT name FROM semesters", fetch=True)
        self.cb_sem['values'] = [s[0] for s in sems] if sems else []

    def get_sem_order(self):
        return ['I-I', 'I-II', 'II-I', 'II-II', 'III-I', 'III-II', 'IV-I', 'IV-II']

    def update_label(self, e):
        cur = self.cb_sem.get()
        order = self.get_sem_order()
        try:
            idx = order.index(cur)
            if idx + 1 < len(order):
                nxt = order[idx+1]
                nxt_yr = (order.index(nxt) // 2) + 1
                self.lbl_info.config(text=f"Promoting to: {nxt} (Year {nxt_yr})")
            else:
                self.lbl_info.config(text="Cannot promote (Course Completed)")
        except ValueError:
            self.lbl_info.config(text="Invalid Semester")

    def execute_move(self, is_promote):
        cur = self.cb_sem.get()
        dept = self.cb_dept.get()
        order = self.get_sem_order()
        
        if cur not in order:
            messagebox.showwarning("Warning", "Select a valid semester first.")
            return
        
        idx = order.index(cur)
        target = None
        target_yr = 0
        
        if is_promote:
            if idx + 1 < len(order):
                target = order[idx+1]
                target_yr = (order.index(target) // 2) + 1
            else:
                messagebox.showinfo("Info", "Batch has completed the course.")
                return
        else:
            if idx - 1 >= 0:
                target = order[idx-1]
                target_yr = (order.index(target) // 2) + 1
            else:
                messagebox.showerror("Error", "Cannot demote from first semester.")
                return
                
        action = "PROMOTE" if is_promote else "DEMOTE"
        if messagebox.askyesno("Confirm", f"{action} students from {cur} to {target} (Year {target_yr})?"):
            sql = "UPDATE students SET semester=%s, year=%s WHERE semester=%s"
            params = [target, target_yr, cur]
            
            if dept != "ALL":
                sql += " AND department=%s"
                params.append(dept)
                
            execute_query(sql, tuple(params))
            messagebox.showinfo("Success", "Batch updated successfully.")

    def promote(self): self.execute_move(True)
    def demote(self): self.execute_move(False)

if __name__ == "__main__":
    setup_auth_db()
    LoginWindow().mainloop()