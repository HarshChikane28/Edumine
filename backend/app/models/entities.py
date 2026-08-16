import enum
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, SmallInteger, String, Text, Time, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass
class UserRole(str, enum.Enum): admin = "admin"; teacher = "teacher"; student = "student"
class ExamStatus(str, enum.Enum): draft = "draft"; scheduled = "scheduled"; completed = "completed"
class ScheduleStatus(str, enum.Enum): scheduled = "scheduled"; completed = "completed"; cancelled = "cancelled"
class SubmissionStatus(str, enum.Enum): pending = "pending"; submitted = "submitted"; graded = "graded"
class ResultStatus(str, enum.Enum): passed = "passed"; failed = "failed"
class DocumentStatus(str, enum.Enum): pending = "pending"; processing = "processing"; completed = "completed"

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))
    full_name: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str] = mapped_column(String(255))

class TeacherPermission(Base):
    __tablename__ = "teacher_permissions"
    __table_args__ = (UniqueConstraint("teacher_id", "permission_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    permission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"))
    granted_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

class ClassRoom(Base):
    __tablename__ = "classes"
    __table_args__ = (UniqueConstraint("grade", "section"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grade: Mapped[str] = mapped_column(String(40))
    section: Mapped[str] = mapped_column(String(20))

class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120))
    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classes.id"))
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classes.id"))
    roll_no: Mapped[str] = mapped_column(String(40))
    student_code: Mapped[str] = mapped_column(String(80), unique=True)
    gpa: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    attendance_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

class Exam(Base):
    __tablename__ = "exams"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120)); term: Mapped[str] = mapped_column(String(80))
    status: Mapped[ExamStatus] = mapped_column(Enum(ExamStatus, name="exam_status"), default=ExamStatus.draft)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

class ExamSchedule(Base):
    __tablename__ = "exam_schedule"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE")); subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id")); class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classes.id"))
    date: Mapped[date] = mapped_column(Date); hall: Mapped[str | None] = mapped_column(String(80), nullable=True); proctor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[ScheduleStatus] = mapped_column(Enum(ScheduleStatus, name="schedule_status"), default=ScheduleStatus.scheduled)

class Result(Base):
    __tablename__ = "results"
    __table_args__ = (UniqueConstraint("exam_id", "student_id", "subject_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE")); student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")); subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"))
    marks: Mapped[Decimal] = mapped_column(Numeric(5, 2)); grade: Mapped[str] = mapped_column(String(10)); status: Mapped[ResultStatus] = mapped_column(Enum(ResultStatus, name="result_status")); entered_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

class TimetableSlot(Base):
    __tablename__ = "timetable_slots"
    __table_args__ = (UniqueConstraint("class_id", "day_of_week", "period_number"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE")); day_of_week: Mapped[int] = mapped_column(SmallInteger); period_number: Mapped[int] = mapped_column(SmallInteger)
    start_time: Mapped[time] = mapped_column(Time); end_time: Mapped[time] = mapped_column(Time); subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id")); teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

class Assignment(Base):
    __tablename__ = "assignments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id")); class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classes.id")); teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")); title: Mapped[str] = mapped_column(String(200)); description: Mapped[str | None] = mapped_column(Text, nullable=True); due_date: Mapped[date] = mapped_column(Date); created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    __table_args__ = (UniqueConstraint("assignment_id", "student_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE")); student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")); submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True); file_path: Mapped[str | None] = mapped_column(String(500), nullable=True); status: Mapped[SubmissionStatus] = mapped_column(Enum(SubmissionStatus, name="submission_status"), default=SubmissionStatus.pending); grade: Mapped[str | None] = mapped_column(String(10), nullable=True); feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

class DocumentRequest(Base):
    __tablename__ = "document_requests"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requested_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")); document_type: Mapped[str] = mapped_column(String(160)); category: Mapped[str] = mapped_column(String(120)); status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus, name="document_status"), default=DocumentStatus.pending); requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()); fulfilled_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True); file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160)); supervisor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")); class_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("classes.id"), nullable=True); max_enrollment: Mapped[int | None] = mapped_column(Integer, nullable=True)

class ActivityEnrollment(Base):
    __tablename__ = "activity_enrollments"
    __table_args__ = (UniqueConstraint("activity_id", "student_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4); activity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE")); student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")); joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ActivityFeed(Base):
    __tablename__ = "activity_feed"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4); activity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE")); text: Mapped[str] = mapped_column(String(500)); created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
