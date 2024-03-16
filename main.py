from fastapi import FastAPI, Body, Path, Query, Depends
from datetime import datetime
from typing import Optional, List

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


@app.get("/events/{event_id}")
def get_event(event_id: int = Path(..., description="ID of the event to retrieve"), db: Session = Depends(get_db)):
    """Retrieves details of a specific event by its ID."""
    return db_manager.get_event(event_id, db)


@app.get("/events/{filter_by}/{filter_value}")
def get_event_by_filter(filter_by: str = Path(..., description="key to get by"),
                        filter_value: str = Path(..., description="value of key"),
                        db: Session = Depends(get_db)):
    """Retrieves details of a specific event by its ID."""
    return db_manager.get_event_by(filter_by, filter_value, db)


@app.put("/events/{event_id}")
def update_event(event_id: int = Path(..., description="ID of the event to update"),
                 title: Optional[str] = Body(None),
                 description: Optional[str] = Body(None),
                 date: Optional[datetime] = Body(None),
                 location: Optional[str] = Body(None),
                 participants: List[str] = Body(None),
                 db: Session = Depends(get_db)):
    return db_manager.update_event(event_id, title, description, date, location, participants, db)


@app.delete("/events/{event_id}")
def delete_event(event_id: int = Path(..., description="ID of the event to delete"), db: Session = Depends(get_db)):
    """Deletes an event by its ID."""
    return db_manager.delete_event(event_id, db)


if __name__ == "__main__":
    import uvicorn

    scheduler = EventScheduler()
    scheduler.create_scheduler()

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
