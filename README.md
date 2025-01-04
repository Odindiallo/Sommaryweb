# DocFlow - Modern Documentation Management System

A modern, user-friendly web application for creating, organizing, and managing documentation with integrated URL summarization capabilities.

![DocFlow Logo](docs/logo.png)

## Features

### Documentation Management
- Create and edit documentation with a rich text editor
- Organize content with categories and tags
- File attachments support
- Advanced search functionality
- Public and private document support

### URL Summarizer
- Summarize web articles and content
- Extract key information from URLs
- Save summaries as documentation
- AI-powered content analysis
- Website design analysis with:
  - Color palette extraction
  - Typography analysis
  - Layout structure detection
  - Asset inventory (images, icons)
  - HTML structure analysis

### Modern UI/UX
- Clean, modern interface with gradient accents
- Responsive design for all devices
- Smooth transitions and animations
- Intuitive navigation system
- Dark/light mode support (coming soon)

### User Management
- Secure authentication system
- User profiles and preferences
- Role-based access control
- Admin dashboard for user management

## Tech Stack

### Backend
- **Framework**: Django 5.0
- **Database**: PostgreSQL 16
- **API**: Django REST Framework 3.14
- **AI Integration**: OpenAI GPT-3.5

### Frontend
- **CSS Framework**: Tailwind CSS 3.4
- **Icons**: Font Awesome 5
- **JavaScript**: ES6+
- **Rich Text Editor**: CKEditor 4

### Development Tools
- **Version Control**: Git
- **Package Management**: pip, npm
- **Environment**: python-dotenv
- **Testing**: pytest

## Prerequisites

- Python 3.11+
- PostgreSQL 16
- Node.js 20+ (for Tailwind CSS)
- Git

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Odindiallo/Sommaryweb.git
   cd Sommaryweb
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings:
   # - Database credentials
   # - Secret key
   # - OpenAI API key
   ```

4. **Initialize database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
docflow/
├── config/                 # Project configuration
│   ├── settings.py        # Django settings
│   └── urls.py           # Main URL routing
├── core/                  # Core functionality
│   ├── views.py          # Main views
│   └── templates/        # Base templates
├── documentation/         # Documentation app
│   ├── models.py         # Document models
│   ├── views.py          # Document views
│   └── templates/        # Document templates
├── url_summarizer/        # URL Summarizer app
│   ├── views.py          # Summarizer logic
│   └── templates/        # Summarizer templates
├── users/                 # User management
│   ├── models.py         # User models
│   └── views.py          # Auth views
└── static/               # Static assets
    ├── css/              # Compiled CSS
    └── js/               # JavaScript files
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [OpenAI](https://openai.com/)
- [Font Awesome](https://fontawesome.com/)
