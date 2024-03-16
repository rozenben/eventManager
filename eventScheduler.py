import functools
import os
import ssl

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import smtplib

import events_db_manager


class EventScheduler:
    """
    Class to manage event scheduling and reminder emails.
    """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(EventScheduler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.username = os.environ.get("EMAIL_SENDER_USERNAME", "eventManager")
        self.password = os.environ.get("EMAIL_SENDER_PASSWORD", "gzic evwm ibig qiag")
        self.sender = os.environ.get("SENDER", "personaleventmanager@gmail.com")

    def create_scheduler(self):
        """
        Initializes the BackgroundScheduler.
        """
        self.scheduler.start()

    def add_event(self, event):
        """
        Adds a new event and schedules a reminder email.

        Args:
            event object represent event
        """
        self.schedule_reminder(event)

    def update_reminder(self, event_id, updated_event, db):
        """
        Updates an existing event and reschedules the reminder email.

        Args:
            event_id (int): ID of the event to update.
            updated_event
            db
        """
        for i, existing_event in enumerate(db_manager.get_all_events("date", db)):
            if existing_event.id == event_id:
                self.remove_job(event_id)  # Remove existing job
                self.schedule_reminder(updated_event)  # Schedule reminder for updated event
                break

    def schedule_reminder(self, event):
        """
        Schedules a job to send a reminder email 30 minutes before the event.

        Args:
            event
        """
        event_start_time = event.date
        reminder_time = event_start_time - timedelta(minutes=30)

        # Construct a CronTrigger for 30 minutes before the event
        trigger = CronTrigger(hour=reminder_time.hour, minute=reminder_time.minute)

        self.scheduler.add_job(
            functools.partial(self.send_reminder, event), trigger
        )

    def remove_job(self, event_id):
        """
        Removes the scheduled job for a specific event ID.

        Args:
            event_id (int): ID of the event whose job needs removal.
        """
        for job in self.scheduler.get_jobs():
            if job.id.startswith(str(event_id)):
                self.scheduler.remove_job(job.id)
                break

    def send_reminder(self, event):
        """
        Sends a reminder email for the event.

        Args:
            event.
        """
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
                smtp.starttls(context=context)  # Start TLS for encryption
                smtp.login(self.username, self.password)
                message = (f"You are invited to the event {event.title}"
                           f"\n Description: {event.description}"
                           f"\n location {event.location}"
                           f"\n invited: {event.participants}"
                           f"\n on the date {event.date}")
                for participant in event.participants:
                    smtp.sendmail(self.sender, participant, message)

        except smtplib.SMTPAuthenticationError as e:
            print(e)
        except smtplib.SMTPException as e:
            print(e)
