import random

from models import SessionLocal, StudentRecord, init_db


STUDENTS = [
    ("alice.chen@university.com", "Alice Chen", "Student001"),
    ("brandon.wong@university.com", "Brandon Wong", "Student002"),
    ("carla.nguyen@university.com", "Carla Nguyen", "Student003"),
    ("dylan.patel@university.com", "Dylan Patel", "Student004"),
    ("elena.ross@university.com", "Elena Ross", "Student005"),
    ("farah.ali@university.com", "Farah Ali", "Student006"),
    ("george.ho@university.com", "George Ho", "Student007"),
    ("hannah.li@university.com", "Hannah Li", "Student008"),
    ("ian.tan@university.com", "Ian Tan", "Student009"),
    ("julia.kim@university.com", "Julia Kim", "Student010"),
    ("kevin.loo@university.com", "Kevin Loo", "Student011"),
    ("linda.ong@university.com", "Linda Ong", "Student012"),
    ("mason.yap@university.com", "Mason Yap", "Student013"),
    ("nina.singh@university.com", "Nina Singh", "Student014"),
    ("owen.lim@university.com", "Owen Lim", "Student015"),
    ("priya.shah@university.com", "Priya Shah", "Student016"),
    ("quentin.foong@university.com", "Quentin Foong", "Student017"),
    ("rachel.chan@university.com", "Rachel Chan", "Student018"),
    ("samuel.ng@university.com", "Samuel Ng", "Student019"),
    ("tina.yeo@university.com", "Tina Yeo", "Student020"),
    ("ulysses.teo@university.com", "Ulysses Teo", "Student021"),
    ("victoria.woo@university.com", "Victoria Woo", "Student022"),
    ("wendy.lim@university.com", "Wendy Lim", "Student023"),
    ("xavier.lee@university.com", "Xavier Lee", "Student024"),
    ("yasmin.ahmad@university.com", "Yasmin Ahmad", "Student025"),
    ("zachary.owens@university.com", "Zachary Owens", "Student026"),
    ("amber.foo@university.com", "Amber Foo", "Student027"),
    ("brian.goh@university.com", "Brian Goh", "Student028"),
    ("claire.park@university.com", "Claire Park", "Student029"),
    ("daniel.tan@university.com", "Daniel Tan", "Student030"),
]


def generate_unique_student_id(existing_ids):
    while True:
        student_id = f"{random.randint(100000, 999999)}"
        if student_id not in existing_ids:
            return student_id


def main():
    init_db()

    created = 0
    skipped = 0

    with SessionLocal() as session:
        existing_usernames = {row.username for row in session.query(StudentRecord.username).all()}
        existing_ids = {row.student_id for row in session.query(StudentRecord.student_id).all()}

        for username, name, password in STUDENTS:
            if username in existing_usernames:
                skipped += 1
                continue

            student_id = generate_unique_student_id(existing_ids)
            existing_ids.add(student_id)
            session.add(
                StudentRecord(
                    student_id=student_id,
                    name=name,
                    username=username,
                    password=password,
                )
            )
            created += 1

        session.commit()

    print(f"Created {created} students, skipped {skipped} existing accounts.")


if __name__ == "__main__":
    main()
