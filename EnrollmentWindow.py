import tkinter as tk
from tkinter import messagebox

class EnrollmentWindow(tk.Toplevel):
    def __init__(self, master, student, database):
        super().__init__(master)
        self.title("Enrollment")
        self.student = student
        self.database = database
        
        # Center the enrollment window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 400) // 2
        self.geometry(f"600x400+{x}+{y}")

        # Add widgets for enrollment functionality here
        enrollment_label = tk.Label(self, text="Enrollment Window")
        enrollment_label.pack()

        # Create a Listbox widget to display subject list
        self.subject_listbox = tk.Listbox(self, height=15, width=45)  # Larger listbox
        self.subject_listbox.pack()

        # Populate the Listbox with subjects
        self.populate_subject_list()

        # Add Enroll, Remove, Deselect, and Return buttons
        buttons_frame = tk.Frame(self, width=45, height= 20)  # Set background color to white
        buttons_frame.pack(side=tk.BOTTOM, pady=5)

        # Enroll Button
        self.enroll_button = tk.Button(buttons_frame, text="Enroll in Subject", command=self.enrol_in_subject)
        self.enroll_button.pack(side=tk.LEFT, padx=5)

        # Remove Button
        self.remove_button = tk.Button(buttons_frame, text="Remove Subject", command=self.remove_subject)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        # Deselect Button
        self.deselect_button = tk.Button(buttons_frame, text="Deselect", command=self.deselect_subject)
        self.deselect_button.pack(side=tk.LEFT, padx=5)

        # Return Button
        self.return_button = tk.Button(buttons_frame, text="Return to Login", command=self.return_to_login)
        self.return_button.pack(side=tk.LEFT, padx=5)

    def populate_subject_list(self):
        self.subject_listbox.delete(0, tk.END)
        # Get the enrolled subjects for the given username from the database
        enrolled_subjects = self.database.get_subjects(self.student.username)
        if enrolled_subjects:
            # Insert each enrolled subject into the Listbox
            for subject in enrolled_subjects:
                self.subject_listbox.insert(tk.END, f"Subject::{subject.ID} -- mark = {subject.mark} --grade = {subject.grade}")
        else:
            # If no subjects are enrolled, display a message indicating that
            self.subject_listbox.insert(tk.END, "No enrolled subject")

    def enrol_in_subject(self):
        enrolled_subjects = self.database.get_subjects(self.student.username)   
        if len(enrolled_subjects) >= 4:
            messagebox.showinfo("Enrollment Limit Reached", "One student can only enroll in a maximum of 4 subjects.")
        else:
            self.student.subject_enrol() 
            messagebox.showinfo("Enrollment Successful", "You have successfully enrolled in a subject.")
            self.populate_subject_list()

    def remove_subject(self):
        try:
            # Get the index of the selected subject
            selected_index = self.subject_listbox.curselection()
            if selected_index:
                # Extract the first selected index from the tuple
                selected_index = selected_index[0]
                enrolled_subjects = self.database.get_subjects(self.student.username)
                removed_subject_ID = enrolled_subjects[selected_index].ID 
                # Get the subject information from the selected index
                self.database.remove_subject(self.student.username, removed_subject_ID)
                messagebox.showinfo("Subject Removed", f"Subject {removed_subject_ID} has been removed.")
                self.populate_subject_list()
            else:
                raise Exception("No Subject Selected")
        except Exception as e:
            messagebox.showinfo("Error", str(e))
    
    def return_to_login(self):
        # Withdraw the enrollment window
        self.withdraw()
        # Deiconify (show) the master window
        self.master.deiconify()
        # Close the enrollment window
        self.destroy()

    def deselect_subject(self):
        self.subject_listbox.selection_clear(0, tk.END)

