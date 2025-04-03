# NewEdu API

This API serves as the backend for the NewEdu platform, an educational platform for Uzbek youth that provides high-tier education and productivity boosting through AI-tailored study plans and gamification.

## Features

- User authentication (register/login) for three types of users:
  - Students
  - Teachers
  - Administration
- JWT-based authentication
- Database integration with MySQL 8.0
- Built with FastAPI for high performance

## Project Structure

The API follows a modular architecture for better maintainability and scalability:

```
/app
  /api
    /endpoints       # API route handlers organized by function
      auth.py        # Authentication endpoints (login, check-phone)
      register.py    # Registration endpoints for different user types
      users.py       # User-related endpoints
    api.py           # API router that combines all endpoints
  /core
    config.py        # Application settings and configuration
    database.py      # Database setup and session management
    security.py      # Security utilities (password hashing, JWT)
  /models            # SQLAlchemy database models
    user.py          # User, Student, Teacher, Admin models
  /schemas           # Pydantic schemas for request/response validation
    user.py          # Schemas for users and authentication
  /utils             # Utility functions
main.py              # Application entry point
```

## Tech Stack

- Python 3.8+
- FastAPI
- SQLAlchemy ORM
- MySQL 8.0
- JWT Authentication

## API Endpoints

### Phone Number Check
- `POST /api/v1/auth/check-phone` - Check if a phone number exists for a specific user type

### Authentication
- `POST /api/v1/auth/login` - Login and receive JWT token

### Registration
- `POST /api/v1/register/student` - Register a new student
- `POST /api/v1/register/teacher` - Register a new teacher
- `POST /api/v1/register/admin` - Register a new administrator

### User
- `GET /api/v1/users/me` - Get current authenticated user information

## Setup & Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with the following variables:
   ```
   DATABASE_URL=mysql+pymysql://username:password@localhost/newedu
   JWT_SECRET_KEY=your-secret-key-change-this-in-production
   ```
5. Start the API server:
   ```
   python main.py
   ```
   The API will be available at http://localhost:8000

## API Documentation

FastAPI automatically generates interactive documentation:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Security Measures

- Password hashing with bcrypt
- JWT tokens for authentication
- CORS protection
- Input validation with Pydantic models

## Development

To run the server in development mode with auto-reload:
```
uvicorn main:app --reload
```

## Contact

Developer: Saidburkhon
Contact: +998972707007
Company: New Edu - Yangi Ta'lim
