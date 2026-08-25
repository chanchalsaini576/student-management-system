import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "sms.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Email (SMTP) settings ---
    # For Gmail: enable 2FA, then create an "App Password" and use that below
    # (do NOT use your normal Gmail password).
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_FROM = os.environ.get("MAIL_FROM", MAIL_USERNAME)

    # Reminder thresholds
    FEE_REMINDER_DAYS_BEFORE = int(os.environ.get("FEE_REMINDER_DAYS_BEFORE", 3))
    TASK_REMINDER_DAYS_BEFORE = int(os.environ.get("TASK_REMINDER_DAYS_BEFORE", 2))
    LOW_ATTENDANCE_THRESHOLD = float(os.environ.get("LOW_ATTENDANCE_THRESHOLD", 75.0))

    # Scheduler: run automatic daily reminder check at this hour (24h, server time)
    REMINDER_HOUR = int(os.environ.get("REMINDER_HOUR", 8))
    REMINDER_MINUTE = int(os.environ.get("REMINDER_MINUTE", 0))
