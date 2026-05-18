# SmartConverter FastAPI 🚀

A professional, industry-level FastAPI application for file conversion with PDF-to-Word and OCR capabilities.

## Features

- **PDF to Word Conversion**: Convert PDF documents to Word format
- **OCR (Optical Character Recognition)**: Extract text from images
- **Professional Architecture**: Clean, modular, and scalable code structure
- **Type Safety**: Full Pydantic validation and type hints
- **Error Handling**: Comprehensive error handling and logging
- **Testing**: Unit tests with pytest
- **Docker Support**: Containerized deployment
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Project Structure

```text
├── app/
│   ├── __init__.py
│   ├── main.py                 # TechMindsForge FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   └── exceptions.py       # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_service.py     # File handling logic
│   │   └── conversion_service.py # Conversion logic
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── api.py          # API router
│           └── endpoints/
│               ├── __init__.py
│               ├── health.py   # Health check endpoint
│               └── conversion.py # Conversion endpoints
├── tests/
│   ├── __init__.py
│   ├── test_main.py           # Main application tests
│   └── test_services.py       # Service layer tests
├── uploads/                   # Uploaded files (auto-created)
├── outputs/                   # Converted files (auto-created)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── nginx.conf              # Nginx configuration
└── README.md               # This file
```

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd TechMindsForge.PythonFastAPI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# For Windows users, update TESSERACT_PATH if needed
```

### 3. Install Tesseract OCR

**Windows:**

```bash
# Download and install Tesseract from:
# https://github.com/UB-Mannheim/tesseract/wiki
# Update TESSERACT_PATH in .env if needed
```

**Linux:**

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**macOS:**

```bash
brew install tesseract
```

### 4. Run the Application

```bash
# Development mode
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### 5. Access the API

- **API Documentation**: <http://127.0.0.1:8001/docs>
- **ReDoc Documentation**: <http://127.0.0.1:8001/redoc>
- **Health Check**: <http://127.0.0.1:8001/api/v1/health>

## API Endpoints

### Health Check

```http
GET /api/v1/health
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Using Docker directly

```bash
# Build the image
docker build -t smart-convert-api .

# Run the container
docker run -p 8001:8001 -v $(pwd)/uploads:/app/uploads -v $(pwd)/outputs:/app/outputs smart-convert-api
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_main.py
```

## Development

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/
```

### Adding New Features

1. **New Endpoints**: Add to `app/api/v1/endpoints/`
2. **New Services**: Add to `app/services/`
3. **New Models**: Add to `app/models/schemas.py`
4. **Configuration**: Update `app/core/config.py`

## Configuration

Key configuration options in `.env`:

```env
# Application
APP_NAME=Smart Convert API
DEBUG=False

# File Upload
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs

# OCR
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Production Deployment

1. **Environment Variables**: Set production values in `.env`
2. **Security**: Configure CORS origins appropriately
3. **File Storage**: Consider using cloud storage for uploads/outputs
4. **Monitoring**: Add logging and monitoring solutions
5. **SSL**: Configure HTTPS with reverse proxy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
