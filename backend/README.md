# DCM System Backend

A FastAPI-based backend for the Smart Differentiated Case Flow Management (DCM) System with BNS Assist.

## Features

- **Case Management**: Create, update, and track legal cases
- **DCM Classification**: Automatic case classification into Fast/Regular/Complex tracks
- **Intelligent Scheduling**: Greedy allocation algorithm for hearing scheduling
- **BNS Assist**: AI-powered suggestion of BNS sections (Phase 1: rule-based)
- **Role-Based Access Control**: Judge/Clerk/Admin/Lawyer/Public roles
- **Audit Logging**: Complete audit trail of all system changes
- **Analytics & Reports**: Comprehensive dashboards and export capabilities

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLModel/SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- **Authentication**: JWT with OAuth2 Password flow
- **NLP**: Rule-based keyword matching (Phase 1), TF-IDF + SVM planned
- **Export**: CSV and PDF report generation

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
copy .env.example .env
# Edit .env with your settings
```

5. Run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core configuration and database
│   ├── models/         # SQLModel data models
│   ├── routers/        # FastAPI route handlers
│   ├── services/       # Business logic services
│   └── __init__.py
├── tests/              # Test files
├── main.py            # FastAPI application entry point
├── requirements.txt   # Python dependencies
└── .env.example      # Environment variables template
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Cases
- `POST /cases/` - Create new case
- `GET /cases/` - List cases
- `GET /cases/{id}` - Get case details
- `PUT /cases/{id}` - Update case
- `POST /cases/{id}/classify` - Classify case using DCM rules
- `POST /cases/{id}/override-track` - Override case track (Judge only)

### Scheduling
- `POST /schedule/allocate` - Allocate cases to cause lists
- `GET /schedule/hearings` - List hearings
- `GET /schedule/cause-list/{date}` - Get cause list for date

### Reports
- `GET /reports/metrics` - Get analytics summary
- `GET /reports/export/cause-list` - Export cause list

### NLP
- `POST /nlp/suggest-laws` - Suggest BNS sections
- `GET /nlp/section/{number}` - Get BNS section details
- `GET /nlp/search` - Search BNS sections

## Services

### DCM Rules Engine (`app/services/dcm_rules.py`)
Classifies cases into tracks based on:
- Keywords in case synopsis
- Case type and priority
- Estimated duration
- Title analysis

### Scheduler (`app/services/scheduler.py`)
Greedy allocation algorithm with:
- Priority-based case ordering
- 15% capacity slack
- Conflict detection
- Multi-bench support

### BNS Assist (`app/services/nlp/bns_assist.py`)
Phase 1 features:
- Rule-based keyword matching
- IPC to BNS section mapping
- Confidence scoring
- Section search

### Audit Service (`app/services/audit.py`)
Comprehensive logging of:
- User actions
- Case modifications
- System events
- Data changes (before/after)

## Testing

Run tests:
```bash
pytest
```

Run specific test:
```bash
pytest tests/test_basic.py
```

## Development

### Code Style
- Follow PEP 8
- Use type hints
- Document functions/classes

### Database Migrations
The system uses SQLModel with automatic table creation. For production, implement proper migrations.

### Adding New Features
1. Define models in `app/models/`
2. Create services in `app/services/`
3. Add routes in `app/routers/`
4. Write tests in `tests/`

## Configuration

Key environment variables:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration
- `DAILY_HEARING_SLOTS`: Hearing capacity per day
- `SLACK_PERCENTAGE`: Scheduling slack (0.15 = 15%)

## Security

- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt
- SQL injection protection via SQLModel
- CORS configuration
- Audit logging for compliance

## Deployment

### Production Setup
1. Use PostgreSQL instead of SQLite
2. Set strong SECRET_KEY
3. Configure proper CORS origins
4. Set up reverse proxy (nginx)
5. Use production WSGI server (gunicorn)

### Docker (planned)
Docker support will be added in future versions.

## Roadmap

### Phase 1 (Current)
- ✅ Basic case management
- ✅ Rule-based DCM classification
- ✅ Greedy scheduling algorithm
- ✅ Rule-based BNS suggestions
- ✅ RBAC and audit logging

### Phase 2 (Planned)
- TF-IDF + Linear SVM for NLP
- Advanced scheduling algorithms
- PDF report generation
- Email notifications
- Mobile API support

### Phase 3 (Future)
- Deep learning NLP models
- Predictive case duration
- Intelligent case assignment
- Integration with court systems
- Multi-language support

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the audit logs for debugging
3. Run the test suite to validate setup
