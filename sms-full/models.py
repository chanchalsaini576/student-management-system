from datetime import datetime
from database import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))

    # --- Residential / personal details ---
    address = db.Column(db.String(255))       # street/locality
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    pincode = db.Column(db.String(10))

    guardian_name = db.Column(db.String(120))
    guardian_phone = db.Column(db.String(20))

    # --- Hostel details ---
    is_hostel_resident = db.Column(db.Boolean, default=False)
    room_no = db.Column(db.String(20))
    hostel_block = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendance_records = db.relationship("Attendance", backref="student", cascade="all, delete-orphan")
    marks = db.relationship("ScoreCard", backref="student", cascade="all, delete-orphan")
    fees = db.relationship("Fee", backref="student", cascade="all, delete-orphan")
    hostel_logs = db.relationship("HostelLog", backref="student", cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="student", cascade="all, delete-orphan")

    def attendance_percentage(self):
        total = len(self.attendance_records)
        if total == 0:
            return 100.0
        present = sum(1 for a in self.attendance_records if a.status == "Present")
        return round((present / total) * 100, 2)

    def current_hostel_status(self):
        """Returns 'IN' or 'OUT' based on the latest hostel log entry."""
        if not self.hostel_logs:
            return "IN"  # default assumed in residence
        latest = sorted(self.hostel_logs, key=lambda x: x.timestamp)[-1]
        return latest.direction

    def pending_fees_total(self):
        return sum(f.amount for f in self.fees if not f.paid)


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(10), nullable=False)  # 'Present' or 'Absent'
    subject = db.Column(db.String(80))  # optional, blank = full day


class ScoreCard(db.Model):
    __tablename__ = "scorecard"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)  # Unit Test / Mid Term / Final
    marks_obtained = db.Column(db.Float, nullable=False)
    max_marks = db.Column(db.Float, nullable=False, default=100)
    date = db.Column(db.Date, default=datetime.utcnow)

    def percentage(self):
        if not self.max_marks:
            return 0
        return round((self.marks_obtained / self.max_marks) * 100, 2)

    def grade(self):
        pct = self.percentage()
        if pct >= 90:
            return "A+"
        elif pct >= 80:
            return "A"
        elif pct >= 70:
            return "B"
        elif pct >= 60:
            return "C"
        elif pct >= 50:
            return "D"
        else:
            return "F"


class Fee(db.Model):
    __tablename__ = "fees"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # Tuition / Hostel / Exam / Other
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.Date, nullable=True)
    reminder_sent = db.Column(db.Boolean, default=False)


class HostelLog(db.Model):
    __tablename__ = "hostel_logs"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    direction = db.Column(db.String(5), nullable=False)  # 'IN' or 'OUT'
    remarks = db.Column(db.String(255))


class Task(db.Model):
    """Upcoming work for a student: Test, Assignment, Project, or general Work."""
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    task_type = db.Column(db.String(30), nullable=False)  # Test / Assignment / Project / Work
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    reminder_sent = db.Column(db.Boolean, default=False)
