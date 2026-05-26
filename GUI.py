import tkinter as tk
from tkinter import messagebox
from System import System
from EnrollmentWindow import EnrollmentWindow
from Student import Student

class GUIApp(System):
    def __init__(self, master):
        super().__init__()
        self.master = master
        master.title("University Enrollment")

        self.create_widgets()

    def create_widgets(self):
        window_width = 520
        window_height = 560
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.master.resizable(False, False)

        self.username_value = "zhuhang.li@university.com"
        self.password_value = "Zhuhangli123"

        self.page = tk.Frame(self.master, bg="white")
        self.page.pack(fill=tk.BOTH, expand=True, padx=28, pady=28)

        # This screen intentionally uses Buttons for all visible text because
        # the system Tk build on this machine is not rendering Label/Entry/Canvas.
        self.title_button = tk.Button(
            self.page,
            text="UTS STUDENT ENROLLMENT",
            font=("Helvetica", 20, "bold"),
            relief=tk.GROOVE,
            bd=2,
            command=lambda: None,
            padx=18,
            pady=16,
        )
        self.title_button.pack(fill=tk.X, pady=(0, 14))

        self.pattern_button = tk.Button(
            self.page,
            text="●  ●  ●     ━━━━━━━━━━━━━     ●  ●  ●",
            font=("Helvetica", 14, "bold"),
            relief=tk.FLAT,
            command=lambda: None,
            pady=8,
        )
        self.pattern_button.pack(fill=tk.X, pady=(0, 16))

        self.info_button = tk.Button(
            self.page,
            text="Manage subjects, marks, and AI study advice",
            font=("Helvetica", 13, "bold"),
            relief=tk.RIDGE,
            bd=2,
            command=lambda: None,
            pady=12,
        )
        self.info_button.pack(fill=tk.X, pady=(0, 20))

        self.card = tk.Frame(self.page, bg="white")
        self.card.pack(fill=tk.X)

        self.username_display = tk.Button(
            self.card,
            text=f"USERNAME\n{self.username_value}",
            font=("Helvetica", 14, "bold"),
            relief=tk.RAISED,
            bd=4,
            command=lambda: None,
            padx=16,
            pady=18,
        )
        self.username_display.pack(fill=tk.X, pady=(0, 16))

        self.password_display = tk.Button(
            self.card,
            text="PASSWORD\n***********",
            font=("Helvetica", 14, "bold"),
            relief=tk.RAISED,
            bd=4,
            command=lambda: None,
            padx=16,
            pady=18,
        )
        self.password_display.pack(fill=tk.X, pady=(0, 22))

        self.login_button = tk.Button(
            self.card,
            text="LOGIN WITH DEMO ACCOUNT",
            command=self.student_login,
            font=("Helvetica", 16, "bold"),
            relief=tk.RAISED,
            bd=5,
            padx=18,
            pady=18,
        )
        self.login_button.pack(fill=tk.X, pady=(0, 18))

        self.footer_button = tk.Button(
            self.page,
            text="After login, open AI Study Advice to test DeepSeek",
            font=("Helvetica", 12, "bold"),
            relief=tk.FLAT,
            command=lambda: None,
            pady=10,
        )
        self.footer_button.pack(fill=tk.X, pady=(6, 0))

    def student_login(self):
        username = self.username_value.strip()
        password = self.password_value

        try:
        
            if not username:
                raise ValueError("Empty username field")
            if not password:
                raise ValueError("Empty password field")
            if self.student_authenticate(username, password):
                self.student = Student(username, self.database)
                messagebox.showinfo("Success", f"Login successful!\nWelcome {self.student.name}")
                self.master.withdraw()  # Hide the login window
                self.open_enrollment_window()    
            else:
                raise ValueError("Invalid username or password")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))


    def open_enrollment_window(self):
        enrollment_window = EnrollmentWindow(self.master, self.student, self.database)





if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()

#test for git restriction
