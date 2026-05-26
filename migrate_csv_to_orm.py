import csv
import os

from models import SessionLocal, StudentRecord, SubjectRecord, init_db


def migrate(csv_path="students_data.csv"):
    if not os.path.exists(csv_path):
        return

    init_db()
    with SessionLocal() as session:
        with open(csv_path, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row.get("username")
                if not username:
                    continue

                student = session.query(StudentRecord).filter_by(username=username).one_or_none()
                if not student:
                    student = StudentRecord(
                        name=row["Student_name"],
                        student_id=row["Student_ID"],
                        username=username,
                        password=row["password"],
                    )
                    session.add(student)
                    session.flush()

                for index in range(1, 5):
                    subject_id = row.get(f"Subject_ID{index}")
                    mark = row.get(f"Subject_Mark{index}")
                    if not subject_id or not mark:
                        continue

                    exists = (
                        session.query(SubjectRecord)
                        .filter_by(student_id=student.id, subject_id=subject_id)
                        .one_or_none()
                    )
                    if not exists:
                        session.add(
                            SubjectRecord(
                                student_id=student.id,
                                subject_id=subject_id,
                                mark=int(mark),
                            )
                        )
        session.commit()


if __name__ == "__main__":
    migrate()
