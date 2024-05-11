import re
import random
from Subject import Subject

class Student:
    def __init__(self, username, database):
        self.username = username
        self.database = database
        self.ID = self.database.get_student_ID(username)
        self.name = self.database.get_student_name(username)
        self.username_pattern = r'^[a-z]+\.[a-z0-9]+@university\.com)$'
        self.password_pattern = r'^[A-Z]{1}[a-zA-Z]{5,}\d{3,}$'

    def change_password(self):
        try:
            while True:
                new_password = input('        Please input your new password (Enter x to exit password update): ')
                if new_password == 'x':
                    break
                if re.match(self.password_pattern, new_password):
                    print('        \033[93mNew password is in correct format\033[0m')
                    while True:
                        confirmed_password = input('        Please confirm your new password: ')
                        if new_password == confirmed_password:
                            self.database.update_password(self.username, new_password)
                            print('        \033[93mNew password has been updated\033[0m')
                            break
                        else: 
                            print('        \033[91mConfirmed password and new password are not identical\033[0m')
                    break
                else: 
                    raise ValueError("New password is not in correct format")
        except ValueError as ve:
            print(f'        \033[91m{ve}\033[0m')
            print('        \033[91mpassword should be in format:\033[0m')
            print('        \033[91m- Start with uppercase\n        \- Minimum 6 letters\n        \- Following by minimum 3-digits\033[0m')



    def subject_enrol(self):
        subject_list = self.database.get_subjects(self.username)
        if len(subject_list) < 4:
            subject_ID_list = [enrolled_subject.ID for enrolled_subject in subject_list]
            while True:
                ID = f"{random.randint(1, 999):03}"
                mark = random.randint(25,100)
                if ID not in subject_ID_list:
                    subject = Subject(ID, mark)
                    self.database.write_subject(self.username, subject)
                    subject_list.append(subject)
                    print(f'        \033[93mEnrolling in Subject-{subject.ID}\n        You are now enrolled in {len(subject_list)} out of 4 subjects\033[0m')
                    break
        else: 
            print("        \033[91mStudents are allowed to enrol in 4 subjects only\033[0m")
        

    def subject_remove(self):
        subject_list = self.database.get_subjects(self.username)
        if len(subject_list) == 0:
            print(f'        \033[91mThere is no enrolled subject\033[0m')
        else:
            enrolled_subject_ID_list = [enrolled_subject.ID for enrolled_subject in subject_list]
            while True:
                print('        Enrolled subjects list: ', enrolled_subject_ID_list)
                subject_ID = input('        Please select the subject you want to remove: ')
                if subject_ID in ["x", "X"]:
                    break
                else:
                    subject_ID = f'{subject_ID:0>3}'
                    if subject_ID not in enrolled_subject_ID_list:
                        print('        \033[91mThe subject you want to remove is not in your enrolled subjects list\033[0m')
                    else:
                        subject_ID_position = enrolled_subject_ID_list.index(subject_ID)
                        subject_list.pop(subject_ID_position)
                        self.database.remove_subject(self.username, subject_ID)
                        print(f'        \033[93mSubject {subject_ID} has been removed\033[0m')
                        print(f'        \033[93mYou are now enrolled in {len(subject_list)} out of 4 subjects\033[0m')
                        break
    def subject_show(self):
        subject_list = self.database.get_subjects(self.username)
        if len(subject_list) == 0:
            print(f'        \033[91mThere is no enrolled subject\033[0m')
        else:
            print(f'        \033[93mShowing {len(subject_list)} subjects\033[0m')
            for subject in subject_list:
                print(f'        Subject::{subject.ID} -- mark = {subject.mark} -- grade = {subject.grade}')

    
                


             
            

