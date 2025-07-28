import configparser
from celery import Celery
import asyncio
from email.message import EmailMessage
import aiosmtplib

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

smtp_host = config.get('email', 'smtp_host')
smtp_port = config.getint('email', 'smtp_port')
smtp_user = config.get('email', 'smtp_user')
smtp_password = config.get('email', 'smtp_password')
sender = config.get('email', 'sender')
recipients = [r.strip() for r in config.get('email', 'recipients').split(',')]
use_tls = config.getboolean('email', 'use_tls', fallback=True)

# Celery app
app = Celery('alerts', broker='redis://localhost:6379/0')

@app.task
def send_alert_email(subject, body):
    import logging
    try:
        logging.info(f"Attempting to send alert email: {subject}")
        async def _send():
            message = EmailMessage()
            message["From"] = sender
            message["To"] = ', '.join(recipients)
            message["Subject"] = subject
            message.set_content(body)

            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                use_tls=use_tls
            )

        # Use a fresh event loop if none exists, else run in current loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            # Schedule coroutine in running loop
            task = loop.create_task(_send())
        else:
            asyncio.run(_send())
        logging.info("Alert email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send alert email: {e}", exc_info=True)