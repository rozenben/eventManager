from fastapi import FastAPI, Body, Path, Query, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime
from typing import Optional, List

# Import SQLAlchemy libraries
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import events_db_manager
import users_db_manager
from eventScheduler import EventScheduler

# Database setup
EVENTS_DATABASE_URL = "sqlite:///events.db"
USERS_DATABASE_URL = "sqlite:///users.db"
# SQLAlchemy engine and session
event_engine = create_engine(EVENTS_DATABASE_URL)
EventSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=event_engine)
users_engine = create_engine(USERS_DATABASE_URL)
UsersSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=users_engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_events_db():
    db = EventSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_users_db():
    db = UsersSessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_users_db)):

    users = users_db_manager.get_all_users(db)
    if users:
        for user in users:
            if credentials.username == user.username and credentials.password == user.password:
                return credentials.username
            else:
                raise HTTPException(status_code=401, detail="Incorrect username or password")
    raise HTTPException(status_code=401, detail="Incorrect username or password")


@app.post("/users")
def create_event(username: str = Body(...),
                 password: str = Body(...),
                 email: str = Body(...),
                 db: Session = Depends(get_users_db)):
    return users_db_manager.create_user(username, password, email, db)


@app.get("/users")
def get_all_users(db: Session = Depends(get_users_db)):
    """Retrieves a list of all events, optionally sorted."""
    return users_db_manager.get_all_users(db)


@app.post("/events", dependencies=[Depends(get_current_username)])
def create_event(title: str = Body(...), description: str = Body(...), date: datetime = Body(...),
                 location: str = Body(...), participants: List[str] = Body(...), db: Session = Depends(get_events_db)):
    return events_db_manager.create_event(title, description, date, location, participants, db)


@app.get("/events", dependencies=[Depends(get_current_username)])
def get_all_events(sort_by: Optional[str] = Query(None), db: Session = Depends(get_events_db)):
    """Retrieves a list of all events, optionally sorted."""
    return events_db_manager.get_all_events(sort_by, db)


@app.get("/events/{event_id}", dependencies=[Depends(get_current_username)])
def get_event(event_id: int = Path(..., description="ID of the event to retrieve"),
              db: Session = Depends(get_events_db)):
    """Retrieves details of a specific event by its ID."""
    return events_db_manager.get_event(event_id, db)


@app.get("/events/{filter_by}/{filter_value}", dependencies=[Depends(get_current_username)])
def get_event_by_filter(filter_by: str = Path(..., description="key to get by"),
                        filter_value: str = Path(..., description="value of key"),
                        db: Session = Depends(get_events_db)):
    """Retrieves details of a specific event by its ID."""
    return events_db_manager.get_event_by(filter_by, filter_value, db)


@app.put("/events/{event_id}", dependencies=[Depends(get_current_username)])
def update_event(event_id: int = Path(..., description="ID of the event to update"),
                 title: Optional[str] = Body(None),
                 description: Optional[str] = Body(None),
                 date: Optional[datetime] = Body(None),
                 location: Optional[str] = Body(None),
                 participants: List[str] = Body(None),
                 db: Session = Depends(get_events_db)):
    return events_db_manager.update_event(event_id, title, description, date, location, participants, db)


@app.delete("/events/{event_id}", dependencies=[Depends(get_current_username)])
def delete_event(event_id: int = Path(..., description="ID of the event to delete"),
                 db: Session = Depends(get_events_db)):
    """Deletes an event by its ID."""
    return events_db_manager.delete_event(event_id, db)


if __name__ == "__main__":
    import uvicorn

    scheduler = EventScheduler()
    scheduler.create_scheduler()

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
