# Importing necessary modules and packages
from fastapi import FastAPI, Body, Path, Query, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime
from typing import Optional, List

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Importing local modules
import events_db_manager
import users_db_manager
from eventScheduler import EventScheduler

# Database setup
EVENTS_DATABASE_URL = "sqlite:///events.db"
USERS_DATABASE_URL = "sqlite:///users.db"

# SQLAlchemy engine and session creation
event_engine = create_engine(EVENTS_DATABASE_URL)
EventSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=event_engine)
users_engine = create_engine(USERS_DATABASE_URL)
UsersSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=users_engine)

# Base class for SQLAlchemy models
Base = declarative_base()


# Function to get events database session
def get_events_db():
    db = EventSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to get users database session
def get_users_db():
    db = UsersSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Creating FastAPI app instance
app = FastAPI()
# Initializing HTTPBasic security instance
security = HTTPBasic()


# Function to get current username based on HTTPBasic credentials
def get_current_username(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_users_db)):
    # Retrieving all users from database
    users = users_db_manager.get_all_users(db)
    if users:
        for user in users:
            # Checking if credentials match any user
            if credentials.username == user.username and credentials.password == user.password:
                return credentials.username
            else:
                # Raising HTTPException if credentials are incorrect
                raise HTTPException(status_code=401, detail="Incorrect username or password")
    # Raising HTTPException if no users found or no matching credentials
    raise HTTPException(status_code=401, detail="Incorrect username or password")


# Endpoint to create a new user
@app.post("/users")
def create_event(username: str = Body(...),
                 password: str = Body(...),
                 email: str = Body(...),
                 db: Session = Depends(get_users_db)):
    return users_db_manager.create_user(username, password, email, db)


# Endpoint to retrieve all users
@app.get("/users")
def get_all_users(db: Session = Depends(get_users_db)):
    """Retrieves a list of all users."""
    return users_db_manager.get_all_users(db)


# Endpoint to create a new event
@app.post("/events", dependencies=[Depends(get_current_username)])
def create_event(title: str = Body(...), description: str = Body(...), date: datetime = Body(...),
                 location: str = Body(...), participants: List[str] = Body(...), db: Session = Depends(get_events_db)):
    return events_db_manager.create_event(title, description, date, location, participants, db)


# Endpoint to retrieve all events
@app.get("/events", dependencies=[Depends(get_current_username)])
def get_all_events(sort_by: Optional[str] = Query(None), db: Session = Depends(get_events_db)):
    """Retrieves a list of all events, optionally sorted."""
    return events_db_manager.get_all_events(sort_by, db)


# Endpoint to retrieve a specific event by ID
@app.get("/events/{event_id}", dependencies=[Depends(get_current_username)])
def get_event(event_id: int = Path(..., description="ID of the event to retrieve"),
              db: Session = Depends(get_events_db)):
    """Retrieves details of a specific event by its ID."""
    return events_db_manager.get_event(event_id, db)


# Endpoint to retrieve events by filtering
@app.get("/events/{filter_by}/{filter_value}", dependencies=[Depends(get_current_username)])
def get_event_by_filter(filter_by: str = Path(..., description="key to filter by"),
                        filter_value: str = Path(..., description="value of key"),
                        db: Session = Depends(get_events_db)):
    """Retrieves details of events based on a specific filter."""
    return events_db_manager.get_event_by(filter_by, filter_value, db)


# Endpoint to update a specific event by ID
@app.put("/events/{event_id}", dependencies=[Depends(get_current_username)])
def update_event(event_id: int = Path(..., description="ID of the event to update"),
                 title: Optional[str] = Body(None),
                 description: Optional[str] = Body(None),
                 date: Optional[datetime] = Body(None),
                 location: Optional[str] = Body(None),
                 participants: List[str] = Body(None),
                 db: Session = Depends(get_events_db)):
    return events_db_manager.update_event(event_id, title, description, date, location, participants, db)


# Endpoint to delete a specific event by ID
@app.delete("/events/{event_id}", dependencies=[Depends(get_current_username)])
def delete_event(event_id: int = Path(..., description="ID of the event to delete"),
                 db: Session = Depends(get_events_db)):
    """Deletes an event by its ID."""
    return events_db_manager.delete_event(event_id, db)


# Running the FastAPI server
if __name__ == "__main__":
    import uvicorn

    # Creating an instance of EventScheduler
    scheduler = EventScheduler()
    # Creating a scheduler for periodic tasks
    scheduler.create_scheduler()

    # Running the FastAPI server
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
