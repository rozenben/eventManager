from datetime import datetime
from typing import List, Optional
import re

from fastapi import Body, Depends, Query, Path
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from eventScheduler import EventScheduler as eventScheduler

# Base class for SQLAlchemy models
Base = declarative_base()

DATABASE_URL = "sqlite:///events.db"
# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    participants = Column(String, nullable=False)


def create_event(title: str = Body(...), description: str = Body(...), date: datetime = Body(...),
                 location: str = Body(...), participants: List[str] = Body(...), db: Session=None):
    # db = Depends(get_db)
    # db: Session = Depends(get_db)
    for participant in participants:
        if not is_valid_email(participant):
            return {f"participant {participant} should be a valid email"}

    """Creates a new event and saves it to the database."""
    new_event = Event(title=title, description=description, date=date, location=location,
                      participants=",".join(participants))
    db.add(new_event)
    db.commit()  # Commit changes to the database
    db.refresh(new_event)  # Refresh to retrieve generated ID

    es = eventScheduler()
    es.send_reminder(new_event)
    es.add_event(new_event)
    return {"message": "Event created successfully!", "event": new_event}


def get_all_events(sort_by: Optional[str] = Query(None), db: Session = None):
    events = db.query(Event)
    if sort_by == "date":
        events = events.order_by(Event.date)
    # TODO Add more sorting options based on your needs (e.g., location)
    return events.all()


def get_event(event_id: int = Path(..., description="ID of the event to retrieve"), db: Session = None):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        return {"message": "Event not found"}
    return event


def update_event(event_id: int = Path(..., description="ID of the event to update"),
                 title: Optional[str] = Body(None),
                 description: Optional[str] = Body(None),
                 date: Optional[datetime] = Body(None),
                 location: Optional[str] = Body(None),
                 participants: List[str] = Body(None),
                 db: Session = None):
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

    es = eventScheduler()
    es.send_reminder(event)
    es.update_reminder(event.id, event, db)
    return {"message": "Event updated successfully!", "event": event}


def delete_event(event_id: int = Path(..., description="ID of the event to delete"), db: Session = None):
    """Deletes an event by its ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        return {"message": "Event not found"}
    db.delete(event)
    db.commit()
    return {"message": f"Event id {event_id} deleted successfully"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_valid_email(email):
    """
    This function uses a regular expression to validate a basic email format.
    """
    regex = r"^[^@]+@[^@]+\.[^@]+$"
    return bool(re.match(regex, email))
