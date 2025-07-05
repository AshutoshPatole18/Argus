import logging
import smtplib
from email.mime.text import MIMEText

def send_alert_email(subject, body, config):
    """Sends an email alert using SMTP settings from the config."""
    if not config.getboolean('Email', 'enabled'):
        logging.info("Email alerting is disabled in config.ini. Skipping.")
        return
    logging.info("Sending email alert...")
    try:
        smtp_server = config.get('Email', 'server')
        smtp_port = config.getint('Email', 'port')
        smtp_user = config.get('Email', 'user')
        smtp_password = config.get('Email', 'password')
        smtp_from = config.get('Email', 'from_address')
        smtp_to = [addr.strip() for addr in config.get('Email', 'to_addresses').split(',')]

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = smtp_from
        msg["To"] = ", ".join(smtp_to)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if config.getboolean('Email', 'use_tls'):
                server.starttls()
            if smtp_user:
                server.login(smtp_user, smtp_password)
            server.sendmail(smtp_from, smtp_to, msg.as_string())
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
