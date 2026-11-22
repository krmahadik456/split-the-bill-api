# Split the Bill API

A RESTful backend application built using Python and FastAPI to manage shared bills, record expenses, and calculate total spending.

## Problem Statement

When friends, roommates, or groups travel together, they frequently share expenses. Keeping track of who created a bill, recording individual expenses, and calculating total spending manually can become confusing.

This application addresses that problem by providing a centralized API for managing bills and recording associated expenses.

## Solution

Split the Bill API allows authenticated users to:

- Register and log in securely.
- Create bills.
- View their own bills.
- Add expenses to bills.
- View expenses associated with a bill.
- Retrieve a summary containing the total amount and number of expenses.

The application uses JWT-based authentication to protect user-specific resources.

## Tech Stack

- **Language:** Python
- **Backend Framework:** FastAPI
- **Database:** SQLite
- **ORM:** SQLModel
- **Authentication:** JWT
- **Password Security:** Bcrypt
- **API Documentation:** Swagger UI / OpenAPI

## Features

### 1. User Authentication
- User registration.
- Password hashing.
- Login using username and password.
- JWT access token generation.
- Protected API endpoints.

### 2. Bill Management
- Create a new bill.
- Associate bills with their owners.
- Retrieve bills belonging to the authenticated user.

### 3. Expense Management
- Add expenses to existing bills.
- Associate expenses with the bill and user who paid.
- Retrieve expenses belonging to a bill.

### 4. Expense Summary
- Calculate the total recorded expenses.
- Display the number of expenses.
- Retrieve the bill name and spending summary.

## Database Design

The application uses three database entities:

- **User:** Stores usernames and hashed passwords.
- **Bill:** Stores bill information and its owner's ID.
- **Expense:** Stores expense descriptions, amounts, bill IDs, and payer IDs.

Relationships:

- One user can create multiple bills.
- One bill can contain multiple expenses.
- Each expense is associated with a bill and a user.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register a user |
| POST | `/login` | Authenticate a user |
| GET | `/me` | Get authenticated user |
| POST | `/bills` | Create a bill |
| GET | `/bills` | Retrieve user's bills |
| POST | `/bills/{bill_id}/expenses` | Add an expense |
| GET | `/bills/{bill_id}/expenses` | Retrieve bill expenses |
| GET | `/bills/{bill_id}/summary` | Retrieve expense summary |

Protected endpoints require a valid bearer token.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/krmahadik456/split-the-bill-api.git
cd split-the-bill-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

Windows:
```bash
venv\Scripts\activate
```

Linux / macOS:
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi "uvicorn[standard]" sqlmodel passlib[bcrypt] bcrypt PyJWT python-multipart
```

### 4. Run the application

```bash
uvicorn main:app --reload
```

### 5. Open API documentation

Visit:

http://127.0.0.1:8000/docs

## Future Improvements

- PostgreSQL integration.
- Group members and shared bill participation.
- Automatic expense splitting.
- Individual balances and settlement calculations.
- Improved validation and error handling.
- Automated API testing using Pytest.
- Docker containerization.

## Project Status

Beginner-level backend project demonstrating REST API development, database relationships, authentication, and expense management.

## Author

Kaustubh Mahadik

GitHub: https://github.com/krmahadik456
