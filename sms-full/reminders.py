"""
Checks all students for:
  1. Fees due soon (or overdue) and unpaid -> email reminder
  2. Upcoming tests / assignments / work -> email reminder
  3. Low attendance (below threshold) -> warning email
Called manually via the "Send Reminders Now" button, or automatically every day
by the APScheduler job set up in scheduler.py.
"""

from datetime import date, timedelta
from database import db
from models import Student, Fee, Task
from email_utils import send_email


def run_all_reminders(app):
    results = {"fees": 0, "tasks": 0, "attendance": 0, "errors": []}

    with app.app_context():
        today = date.today()

        # ---------- 1. FEE REMINDERS ----------
        fee_cutoff = today + timedelta(days=app.config["FEE_REMINDER_DAYS_BEFORE"])
        due_fees = Fee.query.filter(
            Fee.paid.is_(False),
            Fee.due_date <= fee_cutoff,
            Fee.reminder_sent.is_(False),
        ).all()

        for fee in due_fees:
            student = fee.student
            days_left = (fee.due_date - today).days
            status_line = "is OVERDUE" if days_left < 0 else f"is due in {days_left} day(s)"

            subject = f"Fee Payment Reminder - {fee.fee_type}"
            body = f"""
            <p>Dear {student.name},</p>
            <p>This is a reminder that your <b>{fee.fee_type}</b> fee of
            <b>₹{fee.amount:,.2f}</b> {status_line} (Due date: {fee.due_date.strftime('%d-%b-%Y')}).</p>
            <p>Please make the payment at the earliest to avoid any inconvenience.</p>
            <p>Regards,<br>Student Management Office</p>
            """
            ok, err = send_email(app, student.email, subject, body)
            if ok:
                fee.reminder_sent = True
                results["fees"] += 1
            elif err:
                results["errors"].append(f"Fee reminder to {student.email}: {err}")

        # ---------- 2. UPCOMING TEST / WORK REMINDERS ----------
        task_cutoff = today + timedelta(days=app.config["TASK_REMINDER_DAYS_BEFORE"])
        upcoming_tasks = Task.query.filter(
            Task.completed.is_(False),
            Task.due_date <= task_cutoff,
            Task.due_date >= today,
            Task.reminder_sent.is_(False),
        ).all()

        for task in upcoming_tasks:
            student = task.student
            days_left = (task.due_date - today).days
            when_text = "today" if days_left == 0 else f"in {days_left} day(s)"

            subject = f"Upcoming {task.task_type}: {task.title}"
            body = f"""
            <p>Dear {student.name},</p>
            <p>You have an upcoming <b>{task.task_type}</b>: <b>{task.title}</b>,
            due {when_text} (Date: {task.due_date.strftime('%d-%b-%Y')}).</p>
            <p>{task.description or ''}</p>
            <p>Please prepare/complete it on time.</p>
            <p>Regards,<br>Student Management Office</p>
            """
            ok, err = send_email(app, student.email, subject, body)
            if ok:
                task.reminder_sent = True
                results["tasks"] += 1
            elif err:
                results["errors"].append(f"Task reminder to {student.email}: {err}")

        # ---------- 3. LOW ATTENDANCE WARNINGS ----------
        threshold = app.config["LOW_ATTENDANCE_THRESHOLD"]
        for student in Student.query.all():
            if student.attendance_records and student.attendance_percentage() < threshold:
                subject = "Low Attendance Warning"
                body = f"""
                <p>Dear {student.name},</p>
                <p>Your current attendance is <b>{student.attendance_percentage()}%</b>,
                which is below the required minimum of {threshold}%.</p>
                <p>Please ensure regular attendance to avoid academic issues.</p>
                <p>Regards,<br>Student Management Office</p>
                """
                ok, err = send_email(app, student.email, subject, body)
                if ok:
                    results["attendance"] += 1
                elif err:
                    results["errors"].append(f"Attendance warning to {student.email}: {err}")

        db.session.commit()

    return results
