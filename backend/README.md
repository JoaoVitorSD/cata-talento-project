# HR Document OCR Backend

This is a FastAPI-based backend service that processes HR documents using OCR technology to extract relevant information.

## Prerequisites

- Python 3.8+
- Tesseract OCR
- poppler-utils (for PDF processing)

## Installation

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
sudo apt-get install -y poppler-utils
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Environment Setup:
```bash
# Create .env file
cp .env.example .env

# Edit .env file with your configuration
# Required variables:
# - ANTHROPIC_API_KEY: Your Claude API key
# - LOG_LEVEL: Logging level (INFO, DEBUG, etc.)
# - HOST: Server host (default: 0.0.0.0)
# - PORT: Server port (default: 8000)
```

## Running the Application

There are two ways to run the development server:

1. Using the run script (recommended):
```bash
python run.py
```
This will automatically load environment variables from .env file.

2. Using uvicorn directly:
```bash
uvicorn app.main:app --reload --host $(grep HOST .env | cut -d '=' -f2) --port $(grep PORT .env | cut -d '=' -f2)
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

- `POST /api/v1/process-pdf`: Upload and process a PDF file to extract HR data
  - Request: Multipart form data with PDF file
  - Response: JSON object containing extracted HR data

## Environment Variables

The application uses the following environment variables:

- `ANTHROPIC_API_KEY`: Required for Claude API access
- `DEBUG`: Enable/disable debug mode (True/False)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR, etc.)
- `HOST`: Server host address
- `PORT`: Server port number

Create a `.env` file in the root directory with these variables before running the application. 