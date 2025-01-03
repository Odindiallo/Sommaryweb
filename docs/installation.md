# Installation Guide

This guide will help you set up the Documentation Management System on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11 or higher
- PostgreSQL 16
- Node.js 20 or higher
- pip (Python package manager)
- Git

## Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd documentation-system
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://user:password@localhost:5432/docdb
   ALLOWED_HOSTS=localhost,127.0.0.1
   TIME_ZONE=UTC
   ```

5. **Setup Database**
   - Create PostgreSQL database:
     ```sql
     CREATE DATABASE docdb;
     ```
   - Run migrations:
     ```bash
     python manage.py migrate
     ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

## Frontend Setup

1. **Install Node.js Dependencies**
   ```bash
   npm install
   ```

2. **Build Frontend Assets**
   ```bash
   npm run build
   ```

## Verification

1. Access the application at `http://127.0.0.1:8000`
2. Log in to the admin interface at `http://127.0.0.1:8000/admin`
3. API documentation is available at `http://127.0.0.1:8000/api/docs`

## Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_ROOT and STATIC_URL settings

3. **Permission Issues**
   - Check file permissions
   - Verify user has access to database
