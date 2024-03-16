from fastapi import Body
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String)
    email = Column(String)


def create_user(username: str = Body(...),
                password: str = Body(...),
                email: str = Body(...),
                db: Session = None):
    new_user = User(username=username, password=password, email=email)
    db.add(new_user)
    db.commit()  # Commit changes to the database
    db.refresh(new_user)  # Refresh to retrieve generated ID
    return {"message": "Username created successfully!", "user": new_user}


def get_all_users(db: Session = None):
    users = db.query(User)
    users = users.order_by(User.username)
    return users.all()
