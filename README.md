Event Management System
This repository contains a set of Python files that collectively form an Event Management System. The system allows users to create events, manage event details, and send reminders to participants.

Files Overview
1. main.py
This file serves as the main application entry point. It defines various FastAPI endpoints for event and user management, interacts with databases using SQLAlchemy, and manages authentication using HTTP Basic Authentication.

Key features:

Define FastAPI endpoints for user and event management
Implement HTTP Basic Authentication for user authentication
Utilize SQLAlchemy for database interaction
2. eventScheduler.py
The EventScheduler class in this file manages event scheduling and reminder emails. It utilizes the APScheduler library to schedule reminder emails before events occur. This class ensures that participants receive reminders at specified intervals before their scheduled events.

Key features:

Schedule reminder emails for events
Send reminder emails using SMTP
Implement Singleton pattern for managing event scheduling
3. users_db_manager.py
This file contains functions for user management within the database. It defines SQLAlchemy models and CRUD operations for creating and retrieving users.

Key features:

Define SQLAlchemy model for the User entity
Implement functions for creating and retrieving users from the database
4. events_db_manager.py
Similar to users_db_manager.py, this file handles event management within the database. It defines SQLAlchemy models and functions for creating, retrieving, updating, and deleting events.

Key features:

Define SQLAlchemy model for the Event entity
Implement CRUD operations for managing events in the database
Dependencies
FastAPI: For building web APIs
SQLAlchemy: For database interaction and ORM
APScheduler: For scheduling reminder emails
Python libraries for handling email sending (e.g., smtplib)
Usage
To run the Event Management System, ensure you have the necessary dependencies installed. Then, execute main.py using Python. Access the provided FastAPI endpoints to interact with the system.

Configuration
Ensure to configure environment variables for email sender credentials (EMAIL_SENDER_USERNAME and EMAIL_SENDER_PASSWORD) and sender email address (SENDER) for proper functioning of the reminder email feature.
