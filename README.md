# 🏛️ Yukthi - Differentiated Case Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6)](https://www.typescriptlang.org/)

> An AI-Powered Legal Case Management System with Bharatiya Nyaya Sanhita (BNS) Integration for Indian Courts

## 🌟 Overview

**Yukthi DCM System** is a comprehensive Differentiated Case Management platform designed to revolutionize court operations in India. It leverages artificial intelligence, natural language processing, and smart scheduling algorithms to automate case classification, optimize judicial resource allocation, and reduce case backlog.

### Key Highlights

- 🤖 **AI-Powered Classification**: Automatic case type detection and BNS section suggestions with 85%+ accuracy
- 📊 **Smart Scheduling**: Greedy allocation algorithm with multi-bench optimization
- 🔍 **Intelligent Search**: Similar case finder using semantic similarity
- 📄 **Document Analysis**: Entity extraction, sentiment analysis, and summarization
- 📈 **Advanced Analytics**: Real-time metrics, predictive analytics, and comprehensive reporting
- 🔐 **Secure & Auditable**: JWT authentication, RBAC, and complete audit trail

## 🏗️ Architecture

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: SQLite (Development) / MongoDB Atlas (Production)
- **ORM**: SQLModel
- **Authentication**: JWT with bcrypt
- **AI/ML**: Scikit-learn, TF-IDF, SVM

#### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: React Hooks
- **UI Components**: Custom components with Lucide icons

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python start_server.py
```

The backend will run on `http://127.0.0.1:8001`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will run on `http://localhost:5173`

### Initial Data Setup

```bash
# Seed the database with demo data
cd backend
python seed_basic_data.py

# Or create a large dataset for testing
python create_large_dataset.py
```

### Default Login Credentials

- **Admin**: `admin@dcm.gov.in` / `admin123`
- **Clerk**: `clerk@dcm.gov.in` / `clerk123`
- **Judge**: `judge1@dcm.gov.in` / `judge123`

## 📚 Features

### 1. Differentiated Case Management (DCM)

Cases are automatically classified into tracks:
- **Fast Track**: Simple cases (45-120 minutes) - e.g., uncontested matters
- **Regular Track**: Standard cases (90-240 minutes) - e.g., property disputes
- **Complex Track**: Intricate cases (180-480+ minutes) - e.g., constitutional matters

### 2. AI-Powered BNS Assist

- Automatic detection of relevant BNS sections
- IPC to BNS mapping for legacy cases
- Confidence scoring for reliability
- Rule-based and ML ensemble models

### 3. Smart Scheduling System

- Priority-based allocation (Urgent → High → Medium → Low)
- 15% capacity slack buffer
- Multi-bench optimization
- Conflict detection and resolution

### 4. Advanced Analytics

- Real-time case statistics
- Classification accuracy tracking
- Workload distribution analysis
- Predictive analytics for resource planning
- Export to CSV/PDF reports

### 5. Document Management

- Upload and categorize legal documents
- AI-powered document analysis
- Entity extraction (names, dates, amounts)
- Full-text search and filtering

### 6. AI Dashboard

Interactive demonstrations of:
- Case classification with confidence scores
- Document analysis and summarization
- Similar cases finder
- Recent AI activities and insights

## 🎯 Core Services

### Backend Services

| Service | Description |
|---------|-------------|
| `CaseIngestionService` | Intelligent case creation with auto-classification |
| `SmartSchedulingService` | Optimized hearing allocation algorithm |
| `EnhancedBNSService` | BNS section suggestion and legal assist |
| `AdvancedAnalyticsService` | Real-time metrics and predictive analytics |
| `DocumentService` | Document upload, analysis, and management |
| `AIService` | Unified AI capabilities (classification, NLP, similarity) |
| `AuditService` | Complete audit trail logging |

### API Endpoints

- **Authentication**: `/api/auth/*` - Login, logout, token management
- **Cases**: `/api/cases/*` - CRUD operations, ingestion, classification
- **Scheduling**: `/api/schedule/*` - Hearing management, smart allocation
- **Analytics**: `/api/analytics/*` - Dashboard metrics, reports
- **AI/NLP**: `/api/ai/*` - Classification, document analysis, similar cases
- **Users**: `/api/users/*` - User management (Admin only)

## 📊 Database Schema

### Core Models

- **User**: Authentication and role management (Admin, Clerk, Judge, Advocate)
- **Case**: Legal cases with classification, priority, status
- **Hearing**: Court scheduling and hearing management
- **Bench**: Court rooms and judge assignments
- **AuditLog**: Complete audit trail of all actions

## 🧠 AI/ML Components

### BNS Classification Model

- **Training Data**: 100+ BNS sections with examples
- **Features**: Keyword matching, TF-IDF vectors, legal pattern recognition
- **Models**: Rule-based (Phase 1), SVM/Ensemble (Phase 2)
- **Accuracy**: ~85% on test data

### NLP Pipeline

1. Text Preprocessing (tokenization, stemming, stopword removal)
2. Feature Extraction (TF-IDF, n-grams)
3. Classification (Ensemble: Rule-based + ML)
4. Confidence Scoring (Weighted averaging)
5. Result Formatting (Structured output with explanations)

## 🔒 Security Features

- JWT-based authentication with secure token management
- Password hashing using bcrypt
- Role-Based Access Control (RBAC)
- Input validation and sanitization
- Complete audit logging
- CORS configuration for API security

## 📖 Documentation

### Project Reports

- `INTELLIGENT_CASE_INGESTION.md` - Case ingestion system documentation
- `MODEL_TRAINING_SUCCESS_REPORT.md` - AI model training results
- `DASHBOARD_ANALYTICS_FIX.md` - Analytics implementation guide
- `BLUEPRINT_COMPARISON.md` - Feature completeness assessment

### Training Data

- Located in `backend/data/enhanced_legal_cases.py`
- 1000+ legal case examples with classifications
- BNS section mappings and examples

## 🧪 Testing

```bash
# Run backend tests
cd backend
python test_enhanced_integration.py

# Check case count and database status
python check_case_count.py
```

## 🚢 Deployment

### Production Setup

1. Update MongoDB connection in `backend/config.py`
2. Set production environment variables
3. Build frontend: `npm run build`
4. Deploy using Docker (Dockerfile provided)
5. Configure reverse proxy (nginx/Apache)

### Environment Variables

```env
DATABASE_URL=mongodb+srv://...
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://127.0.0.1:8001/docs`
- **ReDoc**: `http://127.0.0.1:8001/redoc`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

**Project Yukthi** - Differentiated Case Management System
- GitHub: [@vigneshkriishna](https://github.com/vigneshkriishna)

## 🙏 Acknowledgments

- Bharatiya Nyaya Sanhita (BNS) legal framework
- Indian Penal Code (IPC) to BNS mapping
- FastAPI and React communities
- Open-source contributors

## 📞 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Email: [Your Email]

---

**Made with ❤️ for the Indian Judicial System**

⭐ Star this repository if you find it helpful!
