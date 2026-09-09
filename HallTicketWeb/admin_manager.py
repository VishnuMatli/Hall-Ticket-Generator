import tkinter as tk
from tkinter import messagebox
import mysql.connector
import bcrypt

# ===================== CONFIGURATION =====================
COLORS = {
    "bg": "#212529",
    "fg": "#f8f9fa",
    "input_bg": "#495057",
    "accent": "#0d6efd",
    "success": "#198754"
}

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="0407",
        database="hall_ticket_db_university",
    )

class AdminManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin User Manager")
        self.geometry("400x450")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)

        # Header
        tk.Label(self, text="CREATE NEW ADMIN", font=("Segoe UI", 18, "bold"), 
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=30)

        # Username
        tk.Label(self, text="Username", bg=COLORS["bg"], fg=COLORS["fg"]).pack(anchor="w", padx=40)
        self.ent_user = tk.Entry(self, font=("Segoe UI", 12), bg=COLORS["input_bg"], fg="white", bd=0)
        self.ent_user.pack(fill="x", padx=40, pady=(5, 15), ipady=5)

        # Password
        tk.Label(self, text="Password", bg=COLORS["bg"], fg=COLORS["fg"]).pack(anchor="w", padx=40)
        self.ent_pass = tk.Entry(self, show="●", font=("Segoe UI", 12), bg=COLORS["input_bg"], fg="white", bd=0)
        self.ent_pass.pack(fill="x", padx=40, pady=(5, 15), ipady=5)

        # Confirm Password
        tk.Label(self, text="Confirm Password", bg=COLORS["bg"], fg=COLORS["fg"]).pack(anchor="w", padx=40)
        self.ent_confirm = tk.Entry(self, show="●", font=("Segoe UI", 12), bg=COLORS["input_bg"], fg="white", bd=0)
        self.ent_confirm.pack(fill="x", padx=40, pady=(5, 30), ipady=5)

        # Button
        btn = tk.Button(self, text="ADD USER", command=self.add_user, 
                        bg=COLORS["success"], fg="white", font=("Segoe UI", 10, "bold"), 
                        bd=0, padx=20, pady=10, cursor="hand2")
        btn.pack(fill="x", padx=40)

    def add_user(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        confirm = self.ent_confirm.get().strip()

        if not user or not pwd:
            messagebox.showwarning("Error", "All fields are required")
            return

        if pwd != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if exists
            cur.execute("SELECT id FROM admin_users WHERE username = %s", (user,))
            if cur.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return

            # Hash Password
            hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
            
            # Insert
            cur.execute("INSERT INTO admin_users (username, password_hash) VALUES (%s, %s)", 
                        (user, hashed.decode('utf-8')))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Admin user '{user}' created successfully!")
            self.ent_user.delete(0, tk.END)
            self.ent_pass.delete(0, tk.END)
            self.ent_confirm.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

if __name__ == "__main__":
    app = AdminManager()
    app.mainloop()