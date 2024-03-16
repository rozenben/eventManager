from datetime import datetime
from typing import List, Optional
import re

from fastapi import Body, Depends, Query, Path
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
    """
    SQLAlchemy model representing an Event entity.
    """
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    participants = Column(String, nullable=False)


def create_event(title: str = Body(...), description: str = Body(...), date: datetime = Body(...),
                 location: str = Body(...), participants: List[str] = Body(...), db: Session = None):
    """
    Creates a new event and saves it to the database.

    Args:
        title (str): Title of the event.
        description (str): Description of the event.
        date (datetime): Date and time of the event.
        location (str): Location of the event.
        participants (List[str]): List of participants' email addresses.
        db (Session): Database session.

    Returns:
        dict: Message indicating success or failure of event creation along with event details.
    """
    for participant in participants:
        if not is_valid_email(participant):
            return {f"participant {participant} should be a valid email"}

    new_event = Event(title=title, description=description, date=date, location=location,
                      participants=",".join(participants))
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    es = eventScheduler()
    es.send_reminder(new_event)
    es.add_event(new_event)
    return {"message": "Event created successfully!", "event": new_event}


def get_all_events(sort_by: Optional[str] = Query(None), db: Session = None):
    """
    Retrieves a list of all events optionally sorted.

    Args:
        sort_by (Optional[str]): Field to sort by (e.g., "location", "date").
        db (Session): Database session.

    Returns:
        list: List of all events.
    """
    events = db.query(Event)
    if sort_by == "location":
        events = events.order_by(Event.location)
    else:
        events = events.order_by(Event.date)
    return events.all()


def get_event(event_id: int = Path(..., description="ID of the event to retrieve"), db: Session = None):
    """
    Retrieves details of a specific event by its ID.

    Args:
        event_id (int): ID of the event to retrieve.
        db (Session): Database session.

    Returns:
        dict: Details of the event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        return {"message": "Event not found"}
    return event


def get_event_by(filter_by: str, filter_value: str, db):
    """
    Retrieves events based on a specific filter.

    Args:
        filter_by (str): Field to filter by.
        filter_value (str): Value of the filter.
        db (Session): Database session.

    Returns:
        list: List of events matching the filter criteria.
    """
    query = db.query(Event)
    if filter_by and filter_value:
        filter_condition = getattr(Event, filter_by).startswith(filter_value)
        query = query.filter(filter_condition)
        events = query.all()
        if not events:
            return {"message": "No events found matching the filter criteria."}
        return events


def update_event(event_id: int = Path(..., description="ID of the event to update"),
                 title: Optional[str] = Body(None),
                 description: Optional[str] = Body(None),
                 date: Optional[datetime] = Body(None),
                 location: Optional[str] = Body(None),
                 participants: List[str] = Body(None),
                 db: Session = None):
    """
    Updates an existing event by its ID.

    Args:
        event_id (int): ID of the event to update.
        title (Optional[str]): New title of the event.
        description (Optional[str]): New description of the event.
        date (Optional[datetime]): New date and time of the event.
        location (Optional[str]): New location of the event.
        participants (List[str]): List of new participants' email addresses.
        db (Session): Database session.

    Returns:
        dict: Message indicating success or failure of event update along with updated event details.
    """
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
    db.commit()

    es = eventScheduler()
    es.send_reminder(event)
    es.update_reminder(event.id, event, db)
    return {"message": "Event updated successfully!", "event": event}


def delete_event(event_id: int = Path(..., description="ID of the event to delete"), db: Session = None):
    """
    Deletes an event by its ID.

    Args:
        event_id (int): ID of the event to delete.
        db (Session): Database session.

    Returns:
        dict: Message indicating success or failure of event deletion.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        return {"message": "Event not found"}
    db.delete(event)
    db.commit()
    return {"message": f"Event id {event_id} deleted successfully"}


def get_db():
    """
    Dependency function to provide a database session.

    Returns:
        Session: Database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_valid_email(email):
    """
    Validates a basic email format using regular expressions.

    Args:
        email (str): Email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    regex = r"^[^@]+@[^@]+\.[^@]+$"
    return bool(re.match(regex, email))
