import random

from Database import Database
from Subject import Subject
from models import SessionLocal, StudentRecord


def load_student_usernames():
    with SessionLocal() as session:
        rows = (
            session.query(StudentRecord.username)
            .filter(StudentRecord.username != "admin")
            .order_by(StudentRecord.username)
            .all()
        )
    return [username for (username,) in rows]


def pick_subject_id(used_ids):
    while True:
        subject_id = f"{random.randint(1, 999):03}"
        if subject_id not in used_ids:
            return subject_id


def pick_mark():
    return random.randint(25, 100)


def main():
    database = Database()
    usernames = load_student_usernames()

    updated = 0
    already_full = 0

    for username in usernames:
        subjects = database.get_subjects(username)
        used_ids = {subject.ID for subject in subjects}

        if len(subjects) >= 4:
            already_full += 1
            continue

        while len(subjects) < 4:
            subject = Subject(pick_subject_id(used_ids), pick_mark())
            database.write_subject(username, subject)
            used_ids.add(subject.ID)
            subjects.append(subject)

        updated += 1
        print(f"{username}: now enrolled in 4 subjects")

    print(
        f"summary updated={updated} already_full={already_full} "
        f"total={len(usernames)}"
    )


if __name__ == "__main__":
    main()
