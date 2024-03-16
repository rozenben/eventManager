import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import modules to be tested
import main
import eventScheduler
import users_db_manager
import events_db_manager


class TestMain(unittest.TestCase):
    def test_create_event(self):
        # Mock the database session
        mock_db_session = MagicMock()
        mock_db_add = MagicMock()
        mock_db_session.add = mock_db_add

        # Mock the current username
        mock_current_username = "test_user"

        # Call the function with mocked dependencies
        with patch("main.get_current_username", return_value=mock_current_username), \
                patch("main.get_events_db", return_value=mock_db_session):
            response = main.create_event(title="Test Event",
                                         description="This is a test event",
                                         date=datetime.now(),
                                         location="Tel Aviv, test street",
                                         participants=["a@a.a"],
                                         db=mock_db_session)

        # Assert that the database session add method was called
        mock_db_add.assert_called_once()

        # Assert response
        self.assertEqual(response["message"], "Event created successfully!")


class TestEventScheduler(unittest.TestCase):
    def test_schedule_reminder(self):
        # Mock event object
        mock_event = MagicMock()
        mock_event.date = datetime.now()

        # Create an instance of EventScheduler
        scheduler = eventScheduler.EventScheduler()

        # Call the function with mocked dependencies
        scheduler.scheduler = MagicMock()
        scheduler.send_reminder = MagicMock()
        scheduler.schedule_reminder(mock_event)

        # Assert that the scheduler was called with the correct arguments
        scheduler.scheduler.add_job.assert_called_once()


class TestUsersDBManager(unittest.TestCase):
    def test_create_user(self):
        # Mock the database session
        mock_db_session = MagicMock()

        # Call the function with mocked dependencies
        with patch("main.get_users_db", return_value=mock_db_session):
            response = users_db_manager.create_user(username="test user",
                                                    password="test password",
                                                    email="test@gmail.com",
                                                    db=mock_db_session)

        # Assert response
        self.assertEqual(response["message"], "Username created successfully!")


if __name__ == "__main__":
    unittest.main()
