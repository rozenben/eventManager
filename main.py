import functools
import ssl

from fastapi import FastAPI, Body, Path, Query, Depends
from datetime import datetime
from typing import Optional, List
import re

# Import SQLAlchemy libraries
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import db_manager
from eventScheduler import EventScheduler

# Database setup
DATABASE_URL = "sqlite:///events.db"

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


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
    return db_manager.create_event(title, description, date, location, participants, db)


@app.get("/events")
def get_all_events(sort_by: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Retrieves a list of all events, optionally sorted."""
    return db_manager.get_all_events(sort_by, db)
    # # TODO Add more sorting options based on your needs (e.g., location)


@app.get("/events/{event_id}")
def get_event(event_id: int = Path(..., description="ID of the event to retrieve"), db: Session = Depends(get_db)):
    """Retrieves details of a specific event by its ID."""
    return db_manager.get_event(event_id, db)


@app.put("/events/{event_id}")
def update_event(event_id: int = Path(..., description="ID of the event to update"),
                 title: Optional[str] = Body(None),
                 description: Optional[str] = Body(None),
                 date: Optional[datetime] = Body(None),
                 location: Optional[str] = Body(None),
                 participants: List[str] = Body(None),
                 db: Session = Depends(get_db)):
    return db_manager.update_event(event_id, title, description, date, location, participants, db)
    # """Updates an existing event by its ID."""
    # event = db.query(Event).filter(Event.id == event_id).first()
    # if event is None:
    #     return {"message": "Event not found"}
    # event_participants = event.participants.replace(" ", "")
    # participants_list = event_participants.split(",")
    #
    # if title is not None:
    #     event.title = title
    # if description is not None:
    #     event.description = description
    # if date is not None:
    #     event.date = date
    # if location is not None:
    #     event.location = location
    # if participants is not None:
    #     for participant in participants:
    #         if not is_valid_email(participant):
    #             return {f"participant {participant} should be a valid email"}
    #         if participant not in participants_list:
    #             event.participants += "," + participant
    # db.commit()  # Commit changes to the database
    #
    # scheduler.send_reminder(event)
    # scheduler.update_event(event.id, event)
    # return {"message": "Event updated successfully!", "event": event}


@app.delete("/events/{event_id}")
def delete_event(event_id: int = Path(..., description="ID of the event to delete"), db: Session = Depends(get_db)):
    """Deletes an event by its ID."""
    return db_manager.delete_event(event_id, db)


if __name__ == "__main__":
    import uvicorn

    scheduler = EventScheduler()
    scheduler.create_scheduler()

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
