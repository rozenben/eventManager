from datetime import datetime


class Event:
    def __init__(self, title: str, description: str, date: datetime, location: str, participants: list[str] = []):
        self.id = None
        self.title = title
        self.description = description
        self.date = date
        self.location = location
        self.participants = participants

    def add_participant(self, participant: str):
        self.participants.append(participant)

    def remove_participant(self, participant: str):
        self.participants.remove(participant)

    def __str__(self):
        return f"Title: {self.title}\nDescription: {self.description}\nDate: {self.date.strftime('%Y-%m-%d %H:%M')}\nLocation: {self.location}\nParticipants: {', '.join(self.participants)}, {self.id=}"
