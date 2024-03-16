from fastapi import Body
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class User(Base):
    """
    SQLAlchemy model representing a User entity.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String)
    email = Column(String)


def create_user(username: str = Body(...),
                password: str = Body(...),
                email: str = Body(...),
                db: Session = None):
    """
    Creates a new user and saves it to the database.

    Args:
        username (str): Username of the user.
        password (str): Password of the user.
        email (str): Email of the user.
        db (Session): Database session.

    Returns:
        dict: Message indicating success or failure of user creation along with user details.
    """
    new_user = User(username=username, password=password, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Username created successfully!", "user": new_user}


def get_all_users(db: Session = None):
    """
    Retrieves a list of all users sorted by username.

    Args:
        db (Session): Database session.

    Returns:
        list: List of all users.
    """
    users = db.query(User)
    users = users.order_by(User.username)
    return users.all()
