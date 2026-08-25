# 🎓 Student Management System (Full Stack)

A complete full-stack **Student Management System** built with **Flask (Python)** on the
backend and **Bootstrap 5 + Jinja2** on the frontend, backed by **SQLite**.

## ✨ Features

| Module | What it does |
|---|---|
| 👤 Student Profiles | Full details: name, roll no, course, year, contact, **residential address (where they live)**, guardian info |
| ✅ Attendance | Mark Present/Absent per date/subject, auto attendance % calculation |
| 📊 Score Card | Subject-wise marks, exam type (Unit Test/Mid/Final), auto percentage + grade |
| 💰 Fees | Track fee dues (Tuition/Hostel/Exam), paid/unpaid status, overdue detection |
| 🏠 Hostel In/Out | Mark student IN/OUT of hostel, full timestamped log, room & block info |
| 📝 Upcoming Work/Tests | Add tests, assignments, projects, or general work with due dates |
| 📧 Email Reminders | Automatic emails for **fees due**, **upcoming tests/work**, and **low attendance** — sent daily by a background scheduler, or on-demand via a "Send Reminders Now" button |

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, APScheduler (for daily reminder job)
- **Frontend:** HTML, Jinja2 templates, Bootstrap 5, Bootstrap Icons
- **Database:** SQLite (zero setup, file-based — `sms.db`)
- **Email:** Python's built-in `smtplib` (works with Gmail, Outlook, or any SMTP provider)

## 📂 Project Structure

```
sms-full/
├── app.py                # Main Flask app + all routes
├── config.py              # App configuration (reads .env)
├── database.py            # SQLAlchemy db instance
├── models.py               # Student, Attendance, ScoreCard, Fee, HostelLog, Task
├── email_utils.py          # SMTP email sending helper
├── reminders.py            # Fee / task / attendance reminder logic
├── scheduler.py             # Daily background job (APScheduler)
├── requirements.txt
├── .env.example             # Copy to .env and fill in your email credentials
├── .gitignore
├── templates/                # All Jinja2/Bootstrap HTML pages
│   ├── base.html
│   ├── dashboard.html
│   ├── students_list.html
│   ├── student_form.html
│   ├── student_detail.html   # attendance + scorecard + fees + hostel + tasks tabs
│   ├── hostel_overview.html
│   └── tasks_overview.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## 🚀 How to Run Locally

### 1. Clone and set up
```bash
git clone https://github.com/YOUR-USERNAME/student-management-system.git
cd student-management-system
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure email (optional but recommended)
```bash
cp .env.example .env
```
Then open `.env` and fill in:
- `MAIL_USERNAME` — your Gmail address
- `MAIL_PASSWORD` — a Gmail **App Password** (not your normal password — see instructions inside `.env.example`)

> ⚠️ **If you skip this step**, the app still works fully — it will just print
> `[EMAIL SKIPPED]` to the console instead of actually sending mail, so you can
> still test/demo everything without a real email account.

### 5. Run the app
```bash
python app.py
```
Open your browser at: **http://127.0.0.1:5000**

The database (`sms.db`) is created automatically on first run — no manual setup needed.

## 📧 How Reminders Work

- A background job (via **APScheduler**) runs **automatically once a day** at the time
  set in `.env` (`REMINDER_HOUR` / `REMINDER_MINUTE`) — this requires the app to be
  running continuously (e.g., on a server).
- You can also click **"Send Reminders Now"** on the Dashboard to trigger it instantly —
  useful for testing/demo.
- It checks and emails:
  - Students with **fees due soon or overdue**
  - Students with **tests/assignments/work due soon**
  - Students with **attendance below 75%** (configurable)

## 💻 How to Open in VS Code

1. Open VS Code → **File → Open Folder** → select the `student-management-system` folder.
2. Install the **Python extension** (VS Code will usually prompt you).
3. Open the integrated terminal (`` Ctrl + ` ``) and run:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
4. Ctrl+Click the `http://127.0.0.1:5000` link in the terminal to open it in your browser.

## 📤 How to Push to GitHub

1. **Create a new repository** on [github.com](https://github.com) — name it e.g.
   `student-management-system`. Don't initialize it with a README (you already have one).

2. In VS Code's terminal (inside your project folder), run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: full-stack Student Management System"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/student-management-system.git
   git push -u origin main
   ```
3. Refresh your GitHub repo page — all your files should now be there.

> 🔒 Your `.env` file (with real email credentials) is already excluded via `.gitignore`,
> so your password will **never** be pushed to GitHub. Only `.env.example` (with no real
> secrets) is included, so anyone cloning the repo knows what to configure.

## 🔮 Future Improvements

- Admin login/authentication
- Export attendance/marks to PDF or Excel
- SMS reminders in addition to email
- React or Vue frontend (currently server-rendered Jinja2 + Bootstrap for simplicity)

## 📄 License

Free to use for learning and academic project purposes.
