# Split the Bill API

A secure RESTful API built with **Python**, **FastAPI**, and **SQLModel** to manage shared expenses and calculate bill totals.

## Features
*   **JWT Authentication:** Secure user login using JSON Web Tokens.
*   **Password Hashing:** Passwords are securely hashed using Bcrypt before being stored in the database.
*   **Relational Database:** Users, Bills, and Expenses are linked using SQLModel and SQLite.
*   **Expense Summary:** Automatically calculates the total amount for a specific bill.

