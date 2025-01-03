# Documentation Management System

A robust web application for creating, organizing, and searching documentation with user authentication and admin capabilities.

## Features

- User Authentication (Register, Login, Logout)
- Documentation Management
  - Create and edit documentation entries
  - Organize content by topics/categories
  - Rich text editor support
  - File attachments
- Advanced Search Functionality
  - Full-text search
  - Filter by topics
  - Sort by date/relevance
- Admin Interface
  - User management
  - Content moderation
  - Analytics dashboard

## Tech Stack

- **Backend Framework**: Django 5.0
- **Database**: PostgreSQL 16
- **Frontend**:
  - HTML5
  - CSS (Tailwind CSS 3.4)
  - JavaScript (ES6+)
- **Additional Tools**:
  - Django REST Framework 3.14
  - Django Crispy Forms
  - Python-dotenv
  - Markdown Support

## Prerequisites

- Python 3.11+
- PostgreSQL 16
- Node.js 20+ (for Tailwind CSS)
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd documentation-system
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
npm install
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env file with your configuration
```

6. Run database migrations:
```bash
python manage.py migrate
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Start development server:
```bash
python manage.py runserver
```

## Project Structure

```
documentation_system/
├── docs/                    # Project documentation
├── core/                    # Main Django application
│   ├── static/             # Static files (CSS, JS, images)
│   ├── templates/          # HTML templates
│   └── ...
├── documentation/          # Documentation app
│   ├── models.py          # Data models
│   ├── views.py           # View logic
│   ├── urls.py            # URL routing
│   └── ...
├── users/                  # User management app
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Development Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Write comprehensive docstrings and comments
- Create unit tests for new features
- Follow Git flow for version control

## API Documentation

The API documentation will be available at `/api/docs/` after running the server.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team.
