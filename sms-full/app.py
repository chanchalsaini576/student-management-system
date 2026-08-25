from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from config import Config
from database import db
from models import Student, Attendance, ScoreCard, Fee, HostelLog, Task
from reminders import run_all_reminders
from scheduler import start_scheduler


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)

    # Start the daily automatic reminder scheduler
    start_scheduler(app)

    return app


def register_routes(app):

    # ---------------------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------------------
    @app.route("/")
    def dashboard():
        students = Student.query.all()
        total_students = len(students)
        hostel_residents = sum(1 for s in students if s.is_hostel_resident)
        pending_fee_amount = sum(s.pending_fees_total() for s in students)

        today = date.today()
        upcoming_tasks = (
            Task.query.filter(Task.completed.is_(False), Task.due_date >= today)
            .order_by(Task.due_date.asc())
            .limit(8)
            .all()
        )
        overdue_fees = Fee.query.filter(Fee.paid.is_(False), Fee.due_date < today).count()

        return render_template(
            "dashboard.html",
            total_students=total_students,
            hostel_residents=hostel_residents,
            pending_fee_amount=pending_fee_amount,
            upcoming_tasks=upcoming_tasks,
            overdue_fees=overdue_fees,
            today=today,
        )

    @app.route("/send-reminders", methods=["POST"])
    def send_reminders():
        results = run_all_reminders(app)
        msg = (
            f"Reminders sent — Fees: {results['fees']}, "
            f"Tasks: {results['tasks']}, Attendance warnings: {results['attendance']}"
        )
        if results["errors"]:
            msg += f" | {len(results['errors'])} error(s) occurred (check console)."
        flash(msg, "info")
        return redirect(url_for("dashboard"))

    # ---------------------------------------------------------------
    # STUDENTS (CRUD + full profile)
    # ---------------------------------------------------------------
    @app.route("/students")
    def list_students():
        q = request.args.get("q", "").strip()
        query = Student.query
        if q:
            query = query.filter(
                db.or_(Student.name.ilike(f"%{q}%"), Student.roll_no.ilike(f"%{q}%"))
            )
        students = query.order_by(Student.roll_no).all()
        return render_template("students_list.html", students=students, q=q)

    @app.route("/students/new", methods=["GET", "POST"])
    def new_student():
        if request.method == "POST":
            s = Student(
                roll_no=request.form["roll_no"].strip(),
                name=request.form["name"].strip(),
                course=request.form["course"].strip(),
                year=int(request.form["year"]),
                email=request.form["email"].strip(),
                phone=request.form.get("phone", "").strip(),
                address=request.form.get("address", "").strip(),
                city=request.form.get("city", "").strip(),
                state=request.form.get("state", "").strip(),
                pincode=request.form.get("pincode", "").strip(),
                guardian_name=request.form.get("guardian_name", "").strip(),
                guardian_phone=request.form.get("guardian_phone", "").strip(),
                is_hostel_resident=bool(request.form.get("is_hostel_resident")),
                room_no=request.form.get("room_no", "").strip(),
                hostel_block=request.form.get("hostel_block", "").strip(),
            )
            db.session.add(s)
            try:
                db.session.commit()
                flash(f"Student '{s.name}' added successfully.", "success")
                return redirect(url_for("list_students"))
            except Exception:
                db.session.rollback()
                flash("Roll number already exists.", "danger")
        return render_template("student_form.html", student=None)

    @app.route("/students/<int:student_id>")
    def student_detail(student_id):
        student = Student.query.get_or_404(student_id)
        return render_template("student_detail.html", student=student, today=date.today())

    @app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
    def edit_student(student_id):
        student = Student.query.get_or_404(student_id)
        if request.method == "POST":
            student.name = request.form["name"].strip()
            student.course = request.form["course"].strip()
            student.year = int(request.form["year"])
            student.email = request.form["email"].strip()
            student.phone = request.form.get("phone", "").strip()
            student.address = request.form.get("address", "").strip()
            student.city = request.form.get("city", "").strip()
            student.state = request.form.get("state", "").strip()
            student.pincode = request.form.get("pincode", "").strip()
            student.guardian_name = request.form.get("guardian_name", "").strip()
            student.guardian_phone = request.form.get("guardian_phone", "").strip()
            student.is_hostel_resident = bool(request.form.get("is_hostel_resident"))
            student.room_no = request.form.get("room_no", "").strip()
            student.hostel_block = request.form.get("hostel_block", "").strip()
            db.session.commit()
            flash("Student updated successfully.", "success")
            return redirect(url_for("student_detail", student_id=student.id))
        return render_template("student_form.html", student=student)

    @app.route("/students/<int:student_id>/delete", methods=["POST"])
    def delete_student(student_id):
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        flash("Student deleted.", "info")
        return redirect(url_for("list_students"))

    # ---------------------------------------------------------------
    # ATTENDANCE
    # ---------------------------------------------------------------
    @app.route("/students/<int:student_id>/attendance", methods=["POST"])
    def mark_attendance(student_id):
        student = Student.query.get_or_404(student_id)
        att = Attendance(
            student_id=student.id,
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
            status=request.form["status"],
            subject=request.form.get("subject", "").strip(),
        )
        db.session.add(att)
        db.session.commit()
        flash("Attendance recorded.", "success")
        return redirect(url_for("student_detail", student_id=student.id))

    @app.route("/attendance/<int:record_id>/delete", methods=["POST"])
    def delete_attendance(record_id):
        record = Attendance.query.get_or_404(record_id)
        student_id = record.student_id
        db.session.delete(record)
        db.session.commit()
        return redirect(url_for("student_detail", student_id=student_id))

    # ---------------------------------------------------------------
    # SCORE CARD
    # ---------------------------------------------------------------
    @app.route("/students/<int:student_id>/marks", methods=["POST"])
    def add_marks(student_id):
        student = Student.query.get_or_404(student_id)
        mark = ScoreCard(
            student_id=student.id,
            subject=request.form["subject"].strip(),
            exam_type=request.form["exam_type"],
            marks_obtained=float(request.form["marks_obtained"]),
            max_marks=float(request.form.get("max_marks", 100)),
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date() if request.form.get("date") else date.today(),
        )
        db.session.add(mark)
        db.session.commit()
        flash("Marks added.", "success")
        return redirect(url_for("student_detail", student_id=student.id))

    @app.route("/marks/<int:mark_id>/delete", methods=["POST"])
    def delete_marks(mark_id):
        mark = ScoreCard.query.get_or_404(mark_id)
        student_id = mark.student_id
        db.session.delete(mark)
        db.session.commit()
        return redirect(url_for("student_detail", student_id=student_id))

    # ---------------------------------------------------------------
    # FEES
    # ---------------------------------------------------------------
    @app.route("/students/<int:student_id>/fees", methods=["POST"])
    def add_fee(student_id):
        student = Student.query.get_or_404(student_id)
        fee = Fee(
            student_id=student.id,
            fee_type=request.form["fee_type"],
            amount=float(request.form["amount"]),
            due_date=datetime.strptime(request.form["due_date"], "%Y-%m-%d").date(),
        )
        db.session.add(fee)
        db.session.commit()
        flash("Fee record added.", "success")
        return redirect(url_for("student_detail", student_id=student.id))

    @app.route("/fees/<int:fee_id>/toggle-paid", methods=["POST"])
    def toggle_fee_paid(fee_id):
        fee = Fee.query.get_or_404(fee_id)
        fee.paid = not fee.paid
        fee.paid_date = date.today() if fee.paid else None
        db.session.commit()
        return redirect(url_for("student_detail", student_id=fee.student_id))

    @app.route("/fees/<int:fee_id>/delete", methods=["POST"])
    def delete_fee(fee_id):
        fee = Fee.query.get_or_404(fee_id)
        student_id = fee.student_id
        db.session.delete(fee)
        db.session.commit()
        return redirect(url_for("student_detail", student_id=student_id))

    # ---------------------------------------------------------------
    # HOSTEL IN/OUT
    # ---------------------------------------------------------------
    @app.route("/students/<int:student_id>/hostel-toggle", methods=["POST"])
    def hostel_toggle(student_id):
        student = Student.query.get_or_404(student_id)
        new_direction = "OUT" if student.current_hostel_status() == "IN" else "IN"
        log = HostelLog(
            student_id=student.id,
            direction=new_direction,
            remarks=request.form.get("remarks", "").strip(),
        )
        db.session.add(log)
        db.session.commit()
        flash(f"{student.name} marked {new_direction}.", "success")
        return redirect(url_for("student_detail", student_id=student.id))

    @app.route("/hostel")
    def hostel_overview():
        students = Student.query.filter_by(is_hostel_resident=True).all()
        return render_template("hostel_overview.html", students=students)

    # ---------------------------------------------------------------
    # TASKS / UPCOMING WORK / TESTS
    # ---------------------------------------------------------------
    @app.route("/students/<int:student_id>/tasks", methods=["POST"])
    def add_task(student_id):
        student = Student.query.get_or_404(student_id)
        task = Task(
            student_id=student.id,
            title=request.form["title"].strip(),
            description=request.form.get("description", "").strip(),
            task_type=request.form["task_type"],
            due_date=datetime.strptime(request.form["due_date"], "%Y-%m-%d").date(),
        )
        db.session.add(task)
        db.session.commit()
        flash("Task added.", "success")
        return redirect(url_for("student_detail", student_id=student.id))

    @app.route("/tasks/<int:task_id>/toggle-done", methods=["POST"])
    def toggle_task_done(task_id):
        task = Task.query.get_or_404(task_id)
        task.completed = not task.completed
        db.session.commit()
        return redirect(url_for("student_detail", student_id=task.student_id))

    @app.route("/tasks/<int:task_id>/delete", methods=["POST"])
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        student_id = task.student_id
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for("student_detail", student_id=student_id))

    @app.route("/tasks")
    def all_tasks():
        today = date.today()
        tasks = Task.query.filter(Task.completed.is_(False)).order_by(Task.due_date.asc()).all()
        return render_template("tasks_overview.html", tasks=tasks, today=today)


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
