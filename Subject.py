 # 導入隨機數模塊，用於生成隨機數。# Import the random number module to generate random numbers.

class Subject:
    def __init__(self, ID, mark):                        # 這是類的初始化方法，每當創建一個 Subject 的實例時，它會自動調用這個方法。
        self.ID= ID   # 調用 generate_unique_id 方法來賦予對象一個唯一的ID。
        self.mark = int(mark)    # 生成一個介於25到100之間的隨機分數。
        self.grade = self.determine_grade()  # A set to store used IDs to ensure uniqueness

     # 這是一個類方法，用於生成一個格式為三位數的唯一ID。
     # 它在1到999之間隨機選擇一個數字，然後檢查這個數字是否已經在 used_ids 集合中。如果不在，就將其添加到集合中並返回這個ID。
     
    # 調用 determine_grade 方法來根據分數確定對象的等級。
    
    def determine_grade(self):       # 這是一個實例方法，用於根據 self.mark 的值決定對象的等級。
        if self.mark >= 85:
            return 'HD'
        elif 85 >self.mark >= 75:
            return 'D'
        elif 75 > self.mark >= 65:
            return 'C'
        elif 65 > self.mark >= 50:
            return 'P'
        else:
            return 'F'
    