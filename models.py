from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


DATABASE_URL = "sqlite:///students.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Base = declarative_base()


class StudentRecord(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    student_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)

    subjects = relationship(
        "SubjectRecord",
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="SubjectRecord.subject_id",
    )


class SubjectRecord(Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),)

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    subject_id = Column(String, nullable=False)
    mark = Column(Integer, nullable=False)

    student = relationship("StudentRecord", back_populates="subjects")


def init_db():
    Base.metadata.create_all(bind=engine)
