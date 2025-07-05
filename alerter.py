import smtplib
from email.mime.text import MIMEText

def send_alert_email(subject, body, config):
    """Sends an email alert using SMTP."""
    if not config.SMTP_ENABLED:
        print("\nEmail alerting is disabled. Skipping.")
        return

    print("\nSending email alert...")
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = config.SMTP_FROM
        msg["To"] = ", ".join(config.SMTP_TO)

        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            if config.SMTP_USE_TLS:
                server.starttls()
            if config.SMTP_USER:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_FROM, config.SMTP_TO, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
