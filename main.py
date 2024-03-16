import ssl

from fastapi import FastAPI, Body, Path, Query, Depends
from datetime import datetime
from typing import Optional, List
import re

# Import SQLAlchemy libraries
from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# email libs
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# sender_email = "personaleventmanager@gmail.com"
# password = "Em123456"


# Database setup (replace with your path)
DATABASE_URL = "sqlite:///events.db"

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


# Event model (mapped to the "events" table)
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    participants = Column(String, nullable=False)


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.post("/events")
def create_event(title: str = Body(...), description: str = Body(...), date: datetime = Body(...),
                 location: str = Body(...), participants: List[str] = Body(...), db: Session = Depends(get_db)):
    for participant in participants:
        if not is_valid_email(participant):
            return {f"participant {participant} should be a valid email"}

    """Creates a new event and saves it to the database."""
    new_event = Event(title=title, description=description, date=date, location=location,
                      participants=",".join(participants))
    db.add(new_event)
    db.commit()  # Commit changes to the database
    db.refresh(new_event)  # Refresh to retrieve generated ID
    for participant in participants:
        send_email("sender@gmail.com", participant, new_event, "username", "password")
    return {"message": "Event created successfully!", "event": new_event}


@app.get("/events")
def get_all_events(sort_by: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Retrieves a list of all events, optionally sorted."""
    events = db.query(Event)
    if sort_by == "date":
        events = events.order_by(Event.date)
    # Add more sorting options based on your needs (e.g., location)
    return events.all()


@app.get("/events/{event_id}")
def get_event(event_id: int = Path(..., description="ID of the event to retrieve"), db: Session = Depends(get_db)):
    """Retrieves details of a specific event by its ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        return {"message": "Event not found"}
    return event


@app.put("/events/{event_id}")
def update_event(event_id: int = Path(..., description="ID of the event to update"),
                 title: Optional[str] = Body(None),
                 description: Optional[str] = Body(None),
                 date: Optional[datetime] = Body(None),
                 location: Optional[str] = Body(None),
                 participants: List[str] = Body(None),
                 db: Session = Depends(get_db)):
    """Updates an existing event by its ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        return {"message": "Event not found"}
    event_participants = event.participants.replace(" ", "")
    participants_list = event_participants.split(",")

    if title is not None:
        event.title = title
    if description is not None:
        event.description = description
    if date is not None:
        event.date = date
    if location is not None:
        event.location = location
    if participants is not None:
        for participant in participants:
            if not is_valid_email(participant):
                return {f"participant {participant} should be a valid email"}
            if participant not in participants_list:
                event.participants += "," + participant
    db.commit()  # Commit changes to the database

    for participant in participants_list:
        send_email("sender@gmail.com", participant, event, "username", "password")
    return {"message": "Event updated successfully!", "event": event}


@app.delete("/events/{event_id}")
def delete_event(event_id: int = Path(..., description="ID of the event to delete"), db: Session = Depends(get_db)):
    """Deletes an event by its ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        return {"message": "Event not found"}
    db.delete(event)
    db.commit()


def is_valid_email(email):
    """
    This function uses a regular expression to validate a basic email format.
    """
    regex = r"^[^@]+@[^@]+\.[^@]+$"
    return bool(re.match(regex, email))


def send_email(sender, recipient, event, username, password):
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
            smtp.starttls(context=context)  # Start TLS for encryption
            smtp.login(username, password)
            message = (f"You are invited to the event {event.title}"
                       f"\n Description: {event.description}"
                       f"\n location {event.location}"
                       f"\n invited: {event.participants}"
                       f"\n on the date {event.date}")
            smtp.sendmail(sender, recipient, message)

    except smtplib.SMTPAuthenticationError as e:
        print(e)
    except smtplib.SMTPException as e:
        print(e)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
