from Admin import Admin
import random
from Student import Student
from Database import Database
import re

class System:
    def __init__(self):
        self.admin = None
        self.student = None
        self.admin_dict = {'an.thai@university.com': 'Anthai1234', 'gavin.li@university.com': '654321', 'thomas.hsieh@university.com': '111111', 'bobby.yuan@university.com': '222222'}
        self.database = Database()
        self.username_pattern = r"^[a-z]+\.[a-z0-9]+@university\.com$"
        self.password_pattern = r"^[A-Z]{1}[a-zA-Z]{5,}\d{3,}$"
    def main(self):
        self.menu() 

    def menu(self):
        while True:
            print("\033[96mUniversity System (\033[0m\033[96m(A)\033[0m\033[96mAdmin, (\033[0m\033[96mS\033[0m\033[96m)Student, or (\033[0m\033[96mX\033[0m\033[96m)Exit\033[0m\033[96m):\033[0m ", end="")
            c = input().strip().upper()

            if c == 'X':
                    print('\033[93mThank you\033[0m')
                    break
            elif c == 'A':
                    self.admin_system()
            elif c == 'S':
                    self.student_system()
            else: 
                    print("        \033[91mInvalid input, please input correctly\033[0m")


    def admin_system(self):        
        while True:
            c = input('        \033[96mAdmin System (\033[0m\033[96mx\033[0m\033[96m(Exit)/\033[0m\033[96ml\033[0m\033[96m(Login)\033[0m\033[96m:\033[0m ')
            if c == 'l':
                self.admin_login()
            elif c == 'x':
                break
            else:
               print('        \033[91mInvalid input, please input correctly\033[0m')


    def student_system(self):
        while True:
            try:
                c = input('        \033[96mStudent system (\033[0m\033[96mx\033[0m\033[96m(Exit)/\033[0m\033[96ml\033[0m\033[96m(Login)/\033[0m\033[96mr\033[0m\033[96m(Register)\033[0m\033[96m:\033[0m ')
                if c == 'x':
                    break
                elif c == 'l':
                    self.student_login() 
                elif c == 'r':
                    self.student_register()
                else:
                    raise ValueError('Invalid input, please input correctly')
            except ValueError as ve:
                print(f'        \033[91m{ve}\033[0m')


    def student_register(self):
        while True:
            print('        \033[96mStudent register\033[0m')
            try:
                username = input('        Please input your student username (Enter x to return to Student system): ')
                if username == 'x':
                    break
                
                password = input('        Please input your student password: ')

                if self.username_format_validation(username) and self.password_format_validation(password):
                    print('        \033[93mUsername and password format valid\033[0m')
                    if self.check_username(username):
                        name = self.getname(username)
                        ID = self.ID_generate()
                        self.database.register_write(name, ID, username, password)       
                        print(f"        \033[93m{name} account has been successfully registered\033[0m")
                        break
                    else: 
                        print("        \033[91mThis username has already been used, please choose another username, maybe adding a number after lastname element\033[0m")
                else:
                    raise ValueError("Username and password are not in correct format")

            except ValueError as ve:
                print(f"        \033[91m{ve}\033[0m")
                print('        \033[91mUsername should be in format: firstname.surname@university.com\033[0m')
                print('        \033[91mPassword should be in format:\033[0m')
                print('        \033[91m- Start with uppercase\n        - Minimum 6 letters\n        - Following by minimum 3-digits\033[0m')
            
                      
    def username_format_validation(self, username):
            return bool(re.match(self.username_pattern, username))
    
    def password_format_validation(self, password):
            return bool(re.match(self.password_pattern, password))
    
    def getname(self, username):
        # Extract the name components
        fullname = username.split('@')[0]
        firstname = fullname.split('.')[0].capitalize()
        lastname =re.search(r'[a-zA-Z]+', fullname.split('.')[1]).group().lower().capitalize()
        return (firstname +' '+ lastname)
        
    def check_username(self, username):
        username_dict = self.database.get_student_username_dict()
        if username not in username_dict.keys():
            return True
        else:
            return False
               
    def ID_generate(self):
        ID_list = self.database.get_student_ID_list()
        match = True
        while match:
            ID = f"{random.randint(1, 999999):06}"
            if ID not in ID_list:
                match = False 
        return ID
    
    def student_authenticate(self, username, password):
        username_dict = self.database.get_student_username_dict()
        if username  in username_dict.keys() and password == username_dict[username]:
            return True
        else: 
            return False
        
    def admin_authenticate(self, username, password):
        if username in self.admin_dict.keys() and password == self.admin_dict[username]:
            return True
        else: 
            return False
               
    def student_login(self):
        while True:
            print('        \033[92mStudent login\033[0m')
            try:
                username = input('        Please input your student username (Enter x to return to Student system): ')
                if username == 'x':
                    break
                
                password = input('        Please input your student password: ')
                
                if not self.username_format_validation(username):
                    raise ValueError("Username is not in correct format")
                
                if not self.password_format_validation(password):
                    raise ValueError("Password is not in correct format")
                
                if not self.student_authenticate(username, password):
                    raise ValueError("Username and password combination is incorrect")
                
                self.student = Student(username, self.database)
                print(f'        \033[93mWelcome {self.student.name}\033[0m')
                self.student_course_menu()
            
            except ValueError as ve:
                print(f'        \033[91m{ve}\033[0m')

            
    def admin_login(self):
        while True:
            print('        \033[92mAdmin login\033[0m')
            try:
                username = input('        Please input your admin username (Enter x to return to Admin system): ')
                if username == 'x':
                    break
                password = input('        Please input your admin password: ')
                if self.admin_authenticate(username, password):
                    self.admin = Admin(username, self.database)
                    print(f"        \033[93mWelcome {self.admin.name}\033[0m")
                    self.admin_menu()
                else: 
                    print('        \033[91mYour admin username does not exist or wrong username/password\033[0m')
            except ValueError as ve:
                print(f'        \033[91m{ve}\033[0m')

    def student_course_menu(self):
        while True:
            try:
                c = input("        Student course menu (c(Change)/e(Enrol)/r(Remove)/s(Show)/x(Exit)): ")
                if c == 'x':
                    break
                elif c == 'c':
                    self.student.change_password()
                elif c == 'e':
                    self.student.subject_enrol()
                elif c == 'r':
                    self.student.subject_remove()
                elif c == 's':
                    self.student.subject_show()
                else:
                    raise ValueError("Invalid input, please input correctly")
            except ValueError as ve:
                print(f'        \033[91m{ve}\033[0m')

    def admin_menu(self):
        while True:
            try:
                c = input("        \033[92mAdmin menu (c(Clear database file)/g(Group students)/p(Partition students)/r(Remove students)/s(Show)/x(Exit)):\033[0m ")
                if c == 'x':
                    break
                elif c == 'c':
                    self.admin.clear_database()
                elif c == 'g':
                    self.admin.group_students()
                elif c == 'p':
                    self.admin.partition_students()
                elif c == 'r':
                    self.admin.remove_students()
                elif c == 's':
                    self.admin.show()
                else:
                    raise ValueError('Invalid input, please input correctly')
            except ValueError as ve:
                print(f'        \033[91m{ve}\033[0m')

if __name__ == '__main__':
    System().main()

