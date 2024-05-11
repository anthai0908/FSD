import tkinter as tk
from tkinter import messagebox
from System import System
from EnrollmentWindow import EnrollmentWindow
from Student import Student

class GUIApp(System):
    def __init__(self, master):
        super().__init__()
        self.master = master
        master.title("University System")

        self.create_widgets()

    def create_widgets(self):
        # Center the login window on the screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - 300) // 2  # Width of the window is 300
        y = (screen_height - 200) // 2  # Height of the window is 200
        self.master.geometry(f"300x200+{x}+{y}")

        self.label = tk.Label(self.master, text="University System", font=("Arial", 16))
        self.label.pack()

        self.username_label = tk.Label(self.master, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.master, bg="lightgray", fg = 'black')
        self.username_entry.pack()

        self.password_label = tk.Label(self.master, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.master, show="*", bg="lightgray", fg = 'black')
        self.password_entry.pack()

        self.login_button = tk.Button(self.master, text="Login", command=self.student_login)
        self.login_button.pack()

    def student_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.student = Student(username, self.database)

        try:
        
            if not username:
                raise ValueError("Empty username field")
            if not password:
                raise ValueError("Empty password field")
            if self.student_authenticate(username, password):
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
