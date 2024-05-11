#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 15:33:38 2024

@author: gavinli
"""

import re
class Admin():
    def __init__(self, username, database):
        self.database = database
        self.username = username
        self.name = self.getname(username)
        
    def clear_database(self):
            while True:
                print("        \033[93mClearing students database\n\033[0m", end="")
                a = input("        \033[91mAre you sure you want to clear the database (Y)ES/(N)O:\033[0m ").strip().capitalize()
                if a == "Y":
                    self.database.clear_database()
                    print('        \033[93mStudent data cleared\033[0m')
                    break
                elif a == "N":
                    break
                else: 
                    print('        \033[91mInvalid input\033[0m')



    def getname(self, username):
        fullname = username.split("@")[0]
        firstname = fullname.split(".")[0].capitalize()
        lastname = re.search(r"[a-zA-Z]+", fullname.split(".")[1]).group().lower().capitalize()
        return (firstname +" "+ lastname)

    def group_students(self):
        F,P,C,D,HD = self.database.group_students()
        groups = {'F': F, 'P': P, 'C': C, 'D': D, 'HD': HD}
        if len(F) == len(P) == len(C) == len(D) == len(HD) == 0:
            print('                \033[91m< Nothing to display >\n\033[0m', end="")
        else:
            for group_name, group in groups.items():
                if len(group) > 0:
                    print(f"        Group {group_name:}")
                    for student in group:
                        print(f"        {student['Student_name']} :: {student['Student_ID']} --> GRADE: {student['Grade']} - MARK: {student['Mean_mark']}")
                if len(group) == 0:
                    print(f"        \033[91mThere is no student in group {group_name}\n\033[0m", end="")

    def partition_students(self):
        F,P,C,D,HD = self.database.group_students()
        if len(F) == len(P) == len(C) == len(D) == len(HD) == 0:
            print('                \033[91m< Nothing to display >\n\033[0m', end="")
        else: 
            print('        \033[93mFail \033[0m')
            if len(F) == 0:
                print('        \033[93m<There is no failed student>\033[0m')
            if len(F) >0:
                for student in F:
                    print(f'        {student["Student_name"]} :: {student["Student_ID"]} --> GRADE: {student["Grade"]} - MARK: {student["Mean_mark"]}')
            print('        \033[93mPass \033[0m')
            if len(P) == len(C) == len(D) == len(HD) == 0:
                print('        \033[93m<There is no passed student>\033[0m')
            else:
                for group in [P,C,D,HD]:
                        for student in group:
                            print(f"        {student['Student_name']} :: {student['Student_ID']} --> GRADE: {student['Grade']} - MARK: {student['Mean_mark']}")

    def remove_students(self):
        try:
            while True:
                student_ID_list = self.database.get_student_ID_list()
                if len(student_ID_list) == 0:
                    print(f"        \033[93mThere is no student in the list\033[0m")
                    break
                else:
                    print(f"        \033[93mList of students: {student_ID_list}\033[0m")
                    a = input("        Please select student ID you want to remove(Enter X to return to Admin menu): ")
                    if a not in student_ID_list and a.upper() != "X":
                        a = a.zfill(3)
                        raise ValueError(f"Student ID {a} does not exist or is invalid format")
                    if a.upper() == "X":
                        break
                    if a in student_ID_list:
                        self.database.remove_student(a)   
                        print(f"        \033[93mStudent with ID {a} removed successfully.\033[0m")
                        break
        except ValueError as ve:
            print(f"        \033[91m{ve}\033[0m")


    def show(self):
        print("        \033[93mList of all students: \n\033[0m", end="")
        student_list = self.database.get_students()
        if len(student_list) ==0:
            print("                 \033[91m<Nothing to display>\033[0m")
        else:
            for student in student_list:
                print(f"        {student['Student_name']} :: {student['Student_ID']} --> Email: {student['username']}")
    
    
    
    
        

            
        