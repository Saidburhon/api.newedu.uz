# NewEdu API Project Documentation

## Overview

The NewEdu API is the backend infrastructure for the NewEdu platform, an educational system designed for Uzbek youth to access high-quality education and boost productivity through AI-tailored study plans and gamification. The API serves as the foundation for both web and mobile applications, with a particular focus on supporting the Android app.

## Project Purpose

NewEdu aims to transform education in Uzbekistan by:

1. **Providing personalized learning experiences** through AI-generated study plans
2. **Strengthening student discipline** with app blocking features during school hours
3. **Gamifying the educational process** to increase engagement and motivation
4. **Creating a unified platform** for students, teachers, and administrators

The API is built to support a user base that could potentially scale to a million users, making robustness, security, and performance critical considerations in its design.

## Technical Architecture

### Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (recently migrated from MySQL)
- **Authentication**: JWT (JSON Web Tokens)
- **Password Security**: Bcrypt hashing
- **API Documentation**: OpenAPI/Swagger (auto-generated)

### Project Structure

The API follows a modular architecture for better maintainability and scalability:

```
/app
  /api
    /endpoints       # API route handlers organized by function
      auth.py        # Authentication endpoints (login, check-phone)
      register.py    # Registration endpoints for different user types
      users.py       # User-related endpoints
      student_profile.py # Student-specific endpoints
      blocking.py    # App blocking functionality endpoints
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

### Database Schema

The database is structured around a multi-type user system with the following key tables:

1. **users**: Base table for all user types with common fields
   - id, phone_number, full_name, password_hash, user_type, created_at, updated_at

2. **students**: Student-specific information
   - user_id (foreign key to users), school, grade (1-11), class_id, created_at, updated_at

3. **teachers**: Teacher-specific information
   - user_id (foreign key to users), school, subjects, created_at, updated_at

4. **admins**: Administrator-specific information
   - user_id (foreign key to users), role, created_at, updated_at

## Key Features

### 1. Multi-User Type Authentication System

The API supports three distinct user types (students, teachers, administrators) with:

- **Phone number verification**: Checks if a phone number exists for a specific user type
- **Secure registration**: Separate endpoints for each user type with appropriate validation
- **JWT authentication**: Tokens with 14-day expiration for persistent authentication
- **Role-based access control**: Different endpoints and permissions based on user type

### 2. App Blocking System

A core feature of the platform is the ability to block distracting applications on students' phones during school hours:

- **GPS-based detection**: Determines when a student is inside school grounds
- **Schedule-aware blocking**: Considers school calendar (holidays, special events)
- **Emergency exceptions**: Allows for unblocking specific apps in emergency situations
- **Administrative controls**: School admins can manage blocking rules

This system is designed to work with intermittent internet connectivity, using a REST API approach with local caching rather than WebSockets.

### 3. Student Profile Management

Endpoints for managing student information including:

- **Educational details**: School, grade, and class information
- **Profile updates**: Ability to modify profile information
- **Academic progress tracking**: (Planned for future implementation)

## API Endpoints

### Authentication

- `POST /api/v1/auth/check-phone` - Check if a phone number exists for a specific user type
- `POST /api/v1/auth/login` - Login and receive JWT token

### Registration

- `POST /api/v1/register/student` - Register a new student
- `POST /api/v1/register/teacher` - Register a new teacher
- `POST /api/v1/register/admin` - Register a new administrator

### User Management

- `GET /api/v1/users/me` - Get current authenticated user information

### Student Profile

- `GET /api/v1/students/profile` - Get student profile details
- `PUT /api/v1/students/update-school` - Update student's school information

### App Blocking

- `GET /api/v1/blocking/status` - Get current blocking status
- `GET /api/v1/blocking/rules` - Get all blocked apps for the current user
- `POST /api/v1/blocking/emergency-exceptions` - Request emergency exception
- `GET /api/v1/blocking/school-schedule` - Get school schedule with holidays

## Security Features

### Authentication & Authorization

- **JWT-based authentication**: Secure, stateless authentication using signed tokens
- **Phone number validation**: Strict validation for Uzbekistan phone numbers (+998XXXXXXXXX)
- **Password security**: Bcrypt hashing with automatic salt generation
- **Role-based access**: Endpoints restricted based on user type

### Data Protection

- **Input validation**: Comprehensive validation using Pydantic schemas
- **Database security**: Parameterized queries to prevent SQL injection
- **Error handling**: Proper HTTP status codes and error messages
- **Transaction management**: Ensures database consistency

## Deployment

The API is designed for deployment on Linux servers with the following components:

- **Web Server**: Nginx as reverse proxy
- **Application Server**: Uvicorn with multiple workers
- **Process Management**: SystemD service
- **SSL/TLS**: Let's Encrypt certificates
- **Database**: PostgreSQL 12+

Comprehensive deployment instructions are available in the `deployment_reference.md` file, including:

- Server setup
- Database configuration
- Application deployment
- Security hardening
- Backup procedures
- Monitoring setup

## Development Workflow

### Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with database connection and JWT secret
5. Run the development server: `uvicorn main:app --reload`

### Database Setup

1. Install PostgreSQL
2. Create the database: `createdb newedu`
3. Run the setup script: `psql -U postgres -d newedu -f setup_database_postgres.sql`

### Creating a Superuser

Use the provided script to create an admin user:

```bash
python create_superuser.py --phone="+998XXXXXXXXX" --name="Admin Name"
```

## Future Development Plans

1. **Study Plan Generation**: AI-powered study plan creation and management
2. **Progress Tracking**: Monitoring and visualization of student progress
3. **Gamification Elements**: Points, badges, and rewards system
4. **Parent Portal**: Allowing parents to monitor their children's progress
5. **Content Management**: System for teachers to upload and manage educational content

## Conclusion

The NewEdu API provides a robust foundation for an educational platform that aims to revolutionize how Uzbek youth access and engage with education. Its modular design, comprehensive security features, and scalable architecture make it well-suited for growth as the platform expands to serve more users and incorporate additional features.
