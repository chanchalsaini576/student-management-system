"""
Simple email-sending helper using Python's built-in smtplib.
Reads SMTP config from the Flask app's config (see config.py / .env).
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(app, to_email, subject, body_html):
    """
    Sends an HTML email. Returns (True, None) on success or (False, error_message) on failure.
    If MAIL_USERNAME / MAIL_PASSWORD are not configured, it safely skips sending
    and logs to console instead (useful for local testing without real email setup).
    """
    username = app.config.get("MAIL_USERNAME")
    password = app.config.get("MAIL_PASSWORD")

    if not username or not password:
        print(f"[EMAIL SKIPPED - no SMTP configured] To: {to_email} | Subject: {subject}")
        return False, "SMTP not configured (set MAIL_USERNAME / MAIL_PASSWORD in .env)"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = app.config.get("MAIL_FROM", username)
        msg["To"] = to_email
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(msg["From"], [to_email], msg.as_string())

        print(f"[EMAIL SENT] To: {to_email} | Subject: {subject}")
        return True, None
    except Exception as e:
        print(f"[EMAIL FAILED] To: {to_email} | Error: {e}")
        return False, str(e)
