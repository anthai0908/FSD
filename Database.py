import csv
import os
import statistics
from Subject import Subject

class Database():
    def __init__(self, filename='students_data.csv'):
        self.filename = filename # filename='students_data.csv'
        self.check_and_create_student_file()

    def check_and_create_student_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Student_name', 'Student_ID', 'username', 'password', 'Subject_ID1','Subject_Mark1', 'Subject_ID2','Subject_Mark2',
                                 'Subject_ID3','Subject_Mark3','Subject_ID4','Subject_Mark4', 'Mean_mark', 'Grade']) 
    def clear_database(self):
        with open(self.filename, 'r', newline='') as file:
            header = file.readline()
        # Open the CSV file in write mode, which truncates it and effectively clears its contents
        with open(self.filename, 'w', newline='') as file:
        # Write the header back to the file
            file.write(header)
    def get_student_username_dict(self):
 # 這一行檢查 Database 類的實例是否已經有 student_username 這個屬性（即字典）。如果不存在，則執行下一行。
            student_username_dict = {}  # 創造 student_username 字典
            
            with open(self.filename, 'r') as file: # 使用 with 語句來打開文件，這樣可以確保文件在讀取後會被正確關閉。
                reader = csv.DictReader(file)
                for row in reader:
                    username = row['username']  # Access by column header 'username'
                    password = row['password']  # Access by column header 'password'
                    # 這兩行根據列標題（如 'username' 和 'password'）從每行中提取用戶名和密碼。
                    student_username_dict[username] = password
                    # 這行代碼將每個用戶名作為鍵，相應的密碼作為值，添加到 student_username 字典中。
    
            return student_username_dict

    def get_student_ID_list(self):
        with open(self.filename, mode='r') as file:
            reader = csv.DictReader(file)
            return [row['Student_ID'] for row in reader] # 將'Student_ID'的所有物件返回並製作成一列表。

    def register_write(self, Student_name, Student_ID, username, password):
        with open(self.filename, mode = 'r', newline='') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
        with open(self.filename, mode='a', newline='') as file: # 'a' means append.
            writer = csv.DictWriter(file, fieldnames = fieldnames)  # 这行代码创建了一个 csv.writer 对象，它能够将列表（或任何可迭代对象）的内容按照 CSV 格式写入到文件中。
            writer.writerow({'Student_name':Student_name, 'Student_ID': Student_ID, 'username': username, 'password': password}) 
                            # 將 Student_name, Student_ID, username, password 依序寫入新的row中。

    def update_password(self, username, new_password):
                            # 创建一个内存中的数据容器，用于存储更新后的数据
        updated_data = []  # Create a List for the updated data imported from System
    
        # 读取原始文件，更新密码
        with open(self.filename, mode='r') as file:  # 使用 open 函数以只读模式打开 CSV 文件，self.filename 是包含文件名的类属性。
            reader = csv.DictReader(file) # 读取 CSV 文件时，它将自动使用文件的第一行作为字典的键（即列标题）。然后，每一行的数据都会被读取为一个字典，其中键是列标题，值是相应的数据。
            for row in reader:
                if row['username'] == username:
                    row['password'] = new_password
            updated_data.append(row)
            # 遍历文件中的每一行，对于每一行数据，如果 username 字段匹配传入的 username 参数，则更新该行的 password 字段为 new_password。
            # 不管该行数据是否被修改，都将其添加到 updated_data 列表中。
    
        # 写回更新后的数据到原始文件
        with open(self.filename, mode='w', newline='') as file:
            # reader.fieldnames 包含從原始文件讀取時使用的所有列標題。這保證了在寫回文件時，列的順序和原文件一致。
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(updated_data)
            
            
    def write_subject(self, username, subject):
        data = []
    # 首先讀取現有數據
        with open(self.filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    # 填入新的科目ID和成績到空白欄位
                    for i in range(1, 5):
                        if not row[f'Subject_ID{i}']: # 檢查當前索引的科目ID欄位是否為空。
                            row[f'Subject_ID{i}'] = subject.ID
                            row[f'Subject_Mark{i}'] = subject.mark
                            break
                data.append(row) # 不論是否更新了該行，都將其保存到 data 列表中。
        
        with open(self.filename, mode='w', newline='') as file: # 使用寫入模式 ('w') 意味著如果文件已存在，其原有內容將被清空；如果文件不存在，則創建新文件。
            # reader.fieldnames 包含從原始文件讀取時使用的所有列標題。這保證了在寫回文件時，列的順序和原文件一致。
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames) # 創建一個 DictWriter 對象，用於將字典寫入到CSV文件中。
            # DictWriter 需要知道每行字典將要使用的鍵（即列標題），這些鍵由 fieldnames 參數提供。
            writer.writeheader() # 這行代碼寫入列標題（或稱為表頭）到CSV文件。這確保了文件中的數據列清晰標示，有助於數據的解析和閱讀。
            writer.writerows(data) # 這行代碼將 data 列表中的所有行（每行是一個字典）寫入到CSV文件。
            # 由於 data 列表在之前的讀取過程中已經被更新或修改，這裡寫入的將是最新的數據。
        self.grade_and_mean_mark_calculate()

    def remove_subject(self, username, subject_ID):
        data = []
        with open(self.filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    # 檢查和清除匹配的科目ID和成績
                    for i in range(1, 5):
                        if row[f'Subject_ID{i}'] == subject_ID:
                            row[f'Subject_ID{i}'] = ''  # 清除科目ID
                            row[f'Subject_Mark{i}'] = ''  # 清除相應的成績
                data.append(row)
                
        with open(self.filename, mode='w', newline='') as file:
            # reader.fieldnames 包含從原始文件讀取時使用的所有列標題。這保證了在寫回文件時，列的順序和原文件一致。
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(data)
        self.grade_and_mean_mark_calculate()

    def get_student_ID(self, username):
        with open(self.filename, mode='r') as file:  # 'r' 是 read 的意思。
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    return row['Student_ID']

    def get_student_name(self, username):
        with open(self.filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    return row['Student_name']

    def get_subjects(self, username):
        subject_list = []
        # 首先讀取現有數據
        with open(self.filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                     # 收集所有科目ID和成績
                    for i in range(1, 5):  # 假設每個學生最多有四門科目
                        subject_ID_get = f'Subject_ID{i}'
                        mark_get = f'Subject_Mark{i}'
                        if row[subject_ID_get]:
                            subject = Subject(row[subject_ID_get], row[mark_get])  # 確保科目ID和成績欄位有東西存在
                            subject_list.append(subject)
                      # 找到匹配的行後退出循環

        return subject_list
    def grade_and_mean_mark_calculate(self):
        with open(self.filename, mode = 'r', newline= '') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            rows = []
            for row in reader:
                mark_list = []
                for i in range(1,5):
                    if row[f'Subject_ID{i}']:
                        mark_list.append(int(row[f'Subject_Mark{i}']))
                if len(mark_list) >0: 
                    row['Mean_mark'] = statistics.mean(mark_list)
                    row['Grade'] = self.determine_grade(row['Mean_mark'])
                rows.append(row)
        with open(self.filename, mode = 'w', newline= '') as file:
            writer = csv.DictWriter(file, fieldnames= fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    def determine_grade(self, mark):
        if mark >= 85:
            return 'HD'
        elif 85 >mark >= 75:
            return 'D'
        elif 75 > mark >= 65:
            return 'C'
        elif 65 > mark >= 50:
            return 'P'
        else:
            return 'F'
    def group_students(self):
        F, P, C, D, HD = [], [], [], [], []
        with open(self.filename, mode= 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Grade'] == 'F':
                    F.append(row)
                elif row['Grade'] == 'P':
                    P.append(row)
                elif row['Grade'] == 'C':
                    C.append(row)
                elif row['Grade'] == 'D':
                    D.append(row)
                elif row['Grade'] == 'HD':
                    HD.append(row)
                else: 
                    continue
        return F, P, C, D, HD
    def remove_student(self, student_ID):
        data = []
        with open(self.filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['Student_ID'] == student_ID:
                    continue
                else:
                    data.append(row)
        with open(self.filename, mode = 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()
            writer.writerows(data)
    def get_students(self):
        subject_list = []
        with open(self.filename, mode ='r', newline= '') as file:
            reader = csv.DictReader(file)
            for row in reader:
                subject_list.append(row)
        return subject_list
            

        

