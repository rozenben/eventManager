from fastapi import FastAPI, Body, Path, Query, Depends
from datetime import datetime
from typing import Optional

# Import SQLAlchemy libraries
from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

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
    participants = Column(Integer, default=0)  # Add participants column if needed


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
                 location: str = Body(...), db: Session = Depends(get_db)):
    """Creates a new event and saves it to the database."""
    new_event = Event(title=title, description=description, date=date, location=location)
    db.add(new_event)
    db.commit()  # Commit changes to the database
    db.refresh(new_event)  # Refresh to retrieve generated ID
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
                 location: Optional[str] = Body(None), db: Session = Depends(get_db)):
    """Updates an existing event by its ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        return {"message": "Event not found"}
    if title is not None:
        event.title = title
    if description is not None:
        event.description = description
    if date is not None:
        event.date = date
    if location is not None:
        event.location = location
    db.commit()  # Commit changes to the database
    return {"message": "Event updated successfully!", "event": event}


@app.delete("/events/{event_id}")
def delete_event(event_id: int = Path(..., description="ID of the event to delete"), db: Session = Depends(get_db)):
    """Deletes an event by its ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        return {"message": "Event not found"}
    db.delete(event)
    db.commit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)