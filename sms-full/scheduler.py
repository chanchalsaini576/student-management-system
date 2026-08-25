"""
Sets up a background job (APScheduler) that runs the reminder check
automatically once a day at the configured time (see REMINDER_HOUR /
REMINDER_MINUTE in .env). This means fee, test/work, and attendance
reminder emails go out on their own -- no manual action needed once
the server is running continuously.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from reminders import run_all_reminders


def start_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: run_all_reminders(app),
        trigger="cron",
        hour=app.config["REMINDER_HOUR"],
        minute=app.config["REMINDER_MINUTE"],
        id="daily_reminder_job",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler
