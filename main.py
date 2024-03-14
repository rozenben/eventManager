from fastapi import FastAPI, Body, Path
from datetime import datetime
from typing import Optional
import uuid

from event import Event

app = FastAPI()

events = []  # In-memory list to store events (replace with database later)
id_counter = 0


@app.post("/events")
def create_event(title: str = Body(...), description: str = Body(...), date: datetime = Body(...),
                 location: str = Body(...)):
    """Creates a new event and adds it to the list."""
    event_id = str(uuid.uuid4())  # Generate a UUID string
    new_event = Event(title, description, date, location)
    new_event.id = event_id
    events.append(new_event)
    return {"message": "Event created successfully!", "event": new_event}


@app.get("/events")
def get_all_events():
    """Retrieves a list of all events."""
    return events


@app.get("/events/{event_id}")
def get_event(event_id: str = Path(..., description="ID of the event to retrieve")):
    """Retrieves details of a specific event by its ID."""
    try:
        for event in events:
            if event.id == event_id:
                return event
        return {"message": "Event not found"}
    except AttributeError:  # Handle case where event might not have an "id" attribute
        return {"message": "Invalid event ID format"}


@app.put("/events/{event_id}")
def update_event(event_id: str = Path(..., description="ID of the event to update"),
                 title: Optional[str] = Body(None),
                 description: Optional[str] = Body(None),
                 date: Optional[datetime] = Body(None),
                 location: Optional[str] = Body(None)):
    """Updates an existing event by its ID."""
    try:
        for event in events:
            if event.id == event_id:
                if title is not None:
                    event.title = title
                if description is not None:
                    event.description = description
                if date is not None:
                    event.date = date
                if location is not None:
                    event.location = location
                return {"message": "Event updated successfully!", "event": event}
    except IndexError:
        return {"message": "Event not found"}


@app.delete("/events/{event_id}")
def delete_event(event_id: str = Path(..., description="ID of the event to delete")):
    """Deletes an event by its ID."""
    try:
        for i, event in enumerate(events):
            if event.id == event_id:
                del events[i]
                return {"message": "Event deleted successfully!"}
        return {"message": "Event not found"}
    except AttributeError:  # Handle case where event might not have an "id" attribute
        return {"message": "Invalid event ID format"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
