# School Study Room Reservation System

## Description

This project is a school study room reservation system developed to make it easier to check room availability and manage reservations.

## Features

- User registration and login.
- Check room availability by date and time.
- View room capacity and available seats.
- Reserve rooms according to their capacity.
- Limit of one reservation per user per day.
- Edit user account details.
- Store data in a database.

## Technologies Used

- **Python** — programming language.
- **Flask** — web application framework.
- **HTML** — page structure.
- **CSS and Bootstrap** — page styling and layout.
- **DB Browser for SQLite** — tool used to view and manage the database.

## Installation and Execution

### 1. Install the dependencies

```bash
pip install flask flask-sqlalchemy werkzeug
```

### 2. Run the application

In the project folder, run:

```bash
python main.py
```

### 3. Access the website

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

## Database

The application stores user information, login records, and room reservations in an SQLite database, which can be viewed and managed using DB Browser for SQLite.
