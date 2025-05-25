# HR Document OCR System

A comprehensive full-stack application for processing HR documents using OCR technology with AI-enhanced data extraction. The system extracts structured information from PDF documents, validates the data, and stores it in a MongoDB database.

## 🌟 Features

- **Document Processing**: Upload and process PDF documents using OCR technology
- **Drag & Drop Interface**: Intuitive drag-and-drop file upload with real-time feedback
- **AI-Enhanced Extraction**: Uses Claude AI to intelligently extract and structure HR data
- **Data Validation**: Comprehensive validation for CPF, dates, skills, and work experience
- **Modern Web Interface**: React-based frontend with Tailwind CSS styling and bilingual support
- **RESTful API**: FastAPI backend with automatic documentation
- **Database Storage**: MongoDB integration for persistent data storage
- **Real-time Feedback**: Toast notifications and form validation with error handling
- **Template System**: Pre-filled templates for common HR data structures

## 🏗️ Architecture

```
engenharia-software-tp/
├── frontend/          # React + TypeScript frontend
├── backend/           # FastAPI Python backend
├── infra/            # Docker infrastructure
├── scripts/          # Automation scripts
└── README.md         # Project documentation
```

### Technology Stack

**Frontend:**
- React 19.1.0 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Lucide React for icons
- React Toastify for notifications

**Backend:**
- FastAPI for REST API
- Python 3.8+ with async support
- Tesseract OCR for text extraction
- Claude AI (Anthropic) for intelligent data extraction
- MongoDB for data storage
- Pydantic for data validation

**Infrastructure:**
- Docker Compose for containerization
- MongoDB with Mongo Express admin interface

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:
- Node.js 18+ and npm
- Python 3.8+
- Docker and Docker Compose
- Tesseract OCR
- poppler-utils

### System Dependencies (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

### 1. Clone and Setup

```bash
git clone <repository-url>
cd engenharia-software-tp
```

### 2. Start Infrastructure

```bash
cd infra
docker-compose up -d
```

This will start:
- MongoDB on port `27017`
- Mongo Express admin interface on port `8081`

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
# Edit .env file with your configuration (see Environment Variables section)

# Start the backend
python run.py
```

Backend will be available at: `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
# Required
ANTHROPIC_API_KEY=your_claude_api_key_here

# Optional (with defaults)
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO

# MongoDB (if using custom setup)
MONGODB_URL=mongodb://admin:password123@localhost:27017/
MONGODB_DATABASE=hr_documents
```

### Getting Claude API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Generate an API key
4. Add it to your `.env` file

## 📖 API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/process-pdf` | Upload and process PDF documents |
| `POST` | `/api/v1/store-document` | Store validated HR data |
| `POST` | `/api/v1/validate` | Validate HR data without storing |
| `GET` | `/api/v1/template` | Get template data for forms |
| `GET` | `/health` | Health check endpoint |

### Example API Usage

**Process PDF Document:**
```bash
curl -X POST "http://localhost:8000/api/v1/process-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

**Store Document:**
```bash
curl -X POST "http://localhost:8000/api/v1/store-document" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "cpf": "123.456.789-00",
    "date": "2024-03-20T00:00:00",
    "position": "Software Engineer",
    "salary": 5000.00
  }'
```

## 📊 Data Models

### HR Data Structure

The system processes and validates the following data structure:

```typescript
interface HRData {
  name: string;                    // Full name (min 3 chars)
  cpf: string;                     // Brazilian CPF format
  date: datetime;                  // Document date
  position?: string;               // Job position
  department?: string;             // Department
  salary?: number;                 // Salary (> 0)
  contract_type?: string;          // Contract type
  start_date?: datetime;           // Start date
  main_skills?: string[];          // Soft skills
  hard_skills?: string[];          // Technical skills
  work_experience: WorkExperience[]; // Work history
}

interface WorkExperience {
  company: string;                 // Company name
  position: string;                // Job title
  start_date: datetime;            // Start date
  end_date?: datetime;             // End date (optional for current job)
  current_job: boolean;            // Is current position
  description: string;             // Job description (min 10 chars)
  achievements: string[];          // Key achievements
  technologies_used: string[];     // Technologies used
}
```

### Validation Rules

- **CPF**: Must be a valid Brazilian CPF with proper formatting
- **Dates**: Cannot be in the future; work end dates must be after start dates
- **Skills**: Minimum 2 characters per skill
- **Work Experience**: Description minimum 10 characters
- **Salary**: Must be greater than zero if provided

## 🛠️ Development

### Project Structure

```
backend/
├── app/
│   ├── api/              # API routes and endpoints
│   ├── core/             # Core configuration
│   ├── models/           # Pydantic data models
│   ├── services/         # Business logic services
│   └── utils/            # Utility functions
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point

frontend/
├── src/
│   ├── components/       # React components
│   ├── types/           # TypeScript type definitions
│   ├── lib/             # Utility libraries
│   └── assets/          # Static assets
├── package.json         # Node.js dependencies
└── vite.config.ts       # Vite configuration
```

### Available Scripts

**Backend:**
```bash
python run.py              # Start development server
pip install -r requirements.txt  # Install dependencies
```

**Frontend:**
```bash
npm run dev                # Start development server
npm run build              # Build for production
npm run preview            # Preview production build
npm run lint               # Run ESLint
```

**Infrastructure:**
```bash
docker-compose up -d       # Start services
docker-compose down        # Stop services
docker-compose logs        # View logs
```

## 🧪 Testing

### Manual Testing

1. **Upload Test**: Use the frontend to upload a sample PDF document
2. **API Test**: Use the Swagger UI to test API endpoints directly
3. **Database Test**: Check Mongo Express at `http://localhost:8081` to verify data storage

### Sample Test Data

Template data is available at `/api/v1/template` endpoint for testing the complete flow.

## 📦 Deployment

### Production Environment

1. **Environment Variables**: Update `.env` with production values
2. **Database**: Use a production MongoDB instance
3. **SSL**: Configure HTTPS for production
4. **CORS**: Update allowed origins in `backend/app/main.py`

### Build for Production

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
# Configure production environment variables
# Use a production ASGI server like Gunicorn
```

## 🔍 Monitoring and Logs

- **Backend Logs**: Check `backend/app.log` or console output
- **Database Monitoring**: Use Mongo Express at `http://localhost:8081`
- **Health Check**: GET `/health` endpoint for service status

## 🐛 Troubleshooting

### Common Issues

1. **Tesseract OCR not found**:
   ```bash
   sudo apt-get install tesseract-ocr
   ```

2. **PDF processing fails**:
   ```bash
   sudo apt-get install poppler-utils
   ```

3. **Claude API errors**: Verify your `ANTHROPIC_API_KEY` in `.env`

4. **MongoDB connection issues**: Ensure Docker containers are running:
   ```bash
   docker-compose ps
   ```

5. **CORS errors**: Check allowed origins in backend CORS middleware

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

### Code Style

- **Backend**: Follow PEP 8 standards
- **Frontend**: ESLint configuration enforces code style
- **Commits**: Use conventional commit messages

## 📄 License

This project is developed for educational purposes as part of a Software Engineering course.

## 🔗 Related Documentation

- [Frontend README](./frontend/README.md) - React-specific documentation
- [Backend README](./backend/README.md) - FastAPI-specific documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Anthropic Claude API](https://docs.anthropic.com/)

## 📞 Support

For questions or issues:
1. Check existing documentation
2. Review API documentation at `/docs`
3. Check logs for error details
4. Create an issue in the repository

---

**Built with ❤️ for Software Engineering studies** 