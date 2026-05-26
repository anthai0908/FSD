import statistics

from Subject import Subject
from models import SessionLocal, StudentRecord, SubjectRecord, init_db


class Database:
    def __init__(self, filename="students_data.csv"):
        self.filename = filename
        init_db()

    def check_and_create_student_file(self):
        init_db()

    def clear_database(self):
        with SessionLocal() as session:
            session.query(SubjectRecord).delete()
            session.query(StudentRecord).delete()
            session.commit()

    def get_student_username_dict(self):
        with SessionLocal() as session:
            students = session.query(StudentRecord).all()
            return {student.username: student.password for student in students}

    def username_exists(self, username):
        with SessionLocal() as session:
            return session.query(StudentRecord.id).filter_by(username=username).first() is not None

    def authenticate_student(self, username, password):
        with SessionLocal() as session:
            student = (
                session.query(StudentRecord.password)
                .filter_by(username=username)
                .one_or_none()
            )
            return bool(student and student.password == password)

    def get_student_ID_list(self):
        with SessionLocal() as session:
            return [student.student_id for student in session.query(StudentRecord).all()]

    def register_write(self, Student_name, Student_ID, username, password):
        with SessionLocal() as session:
            existing = session.query(StudentRecord).filter_by(username=username).one_or_none()
            if existing:
                return

            session.add(
                StudentRecord(
                    name=Student_name,
                    student_id=Student_ID,
                    username=username,
                    password=password,
                )
            )
            session.commit()

    def update_password(self, username, new_password):
        with SessionLocal() as session:
            student = session.query(StudentRecord).filter_by(username=username).one_or_none()
            if student:
                student.password = new_password
                session.commit()

    def write_subject(self, username, subject):
        with SessionLocal() as session:
            student = session.query(StudentRecord).filter_by(username=username).one_or_none()
            if not student:
                return
            if len(student.subjects) >= 4:
                return
            exists = (
                session.query(SubjectRecord)
                .filter_by(student_id=student.id, subject_id=subject.ID)
                .one_or_none()
            )
            if exists:
                return

            session.add(
                SubjectRecord(
                    student_id=student.id,
                    subject_id=subject.ID,
                    mark=int(subject.mark),
                )
            )
            session.commit()

    def remove_subject(self, username, subject_ID):
        with SessionLocal() as session:
            student = session.query(StudentRecord).filter_by(username=username).one_or_none()
            if not student:
                return
            subject = (
                session.query(SubjectRecord)
                .filter_by(student_id=student.id, subject_id=subject_ID)
                .one_or_none()
            )
            if subject:
                session.delete(subject)
                session.commit()

    def get_student_ID(self, username):
        with SessionLocal() as session:
            student = session.query(StudentRecord).filter_by(username=username).one_or_none()
            return student.student_id if student else None

    def get_student_name(self, username):
        with SessionLocal() as session:
            student = session.query(StudentRecord).filter_by(username=username).one_or_none()
            return student.name if student else None

    def get_subjects(self, username):
        with SessionLocal() as session:
            student = session.query(StudentRecord).filter_by(username=username).one_or_none()
            if not student:
                return []
            return [Subject(subject.subject_id, subject.mark) for subject in student.subjects]

    def grade_and_mean_mark_calculate(self):
        # Mean and grade are computed dynamically in get_students/group_students.
        return

    def determine_grade(self, mark):
        mark = float(mark)
        if mark >= 85:
            return "HD"
        elif 85 > mark >= 75:
            return "D"
        elif 75 > mark >= 65:
            return "C"
        elif 65 > mark >= 50:
            return "P"
        else:
            return "F"

    def group_students(self):
        groups = {"F": [], "P": [], "C": [], "D": [], "HD": []}
        for student in self.get_students():
            grade = student["Grade"]
            if grade in groups:
                groups[grade].append(student)
        return groups["F"], groups["P"], groups["C"], groups["D"], groups["HD"]

    def remove_student(self, student_ID):
        with SessionLocal() as session:
            student = session.query(StudentRecord).filter_by(student_id=student_ID).one_or_none()
            if student:
                session.delete(student)
                session.commit()

    def get_students(self):
        with SessionLocal() as session:
            students = session.query(StudentRecord).all()
            return [self._student_to_row(student) for student in students]

    def _student_to_row(self, student):
        row = {
            "Student_name": student.name,
            "Student_ID": student.student_id,
            "username": student.username,
            "password": student.password,
            "Mean_mark": "",
            "Grade": "",
        }

        marks = []
        for index in range(1, 5):
            row[f"Subject_ID{index}"] = ""
            row[f"Subject_Mark{index}"] = ""

        for index, subject in enumerate(student.subjects[:4], start=1):
            row[f"Subject_ID{index}"] = subject.subject_id
            row[f"Subject_Mark{index}"] = str(subject.mark)
            marks.append(subject.mark)

        if marks:
            mean_mark = statistics.mean(marks)
            row["Mean_mark"] = mean_mark
            row["Grade"] = self.determine_grade(mean_mark)

        return row
