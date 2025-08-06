# News Aggregator

A modern, production-ready news aggregation API built with FastAPI, featuring async operations, comprehensive error handling, and cloud-native deployment capabilities.

## 🚀 Features

- **Async/Await Architecture**: Full async support for high performance
- **Multiple News Sources**: Reddit and NewsAPI.org integration
- **RESTful API**: Well-documented endpoints with OpenAPI/Swagger
- **Database Support**: SQLAlchemy with PostgreSQL/SQLite
- **Caching**: Redis integration for performance optimization
- **Production Ready**: Comprehensive logging, monitoring, and error handling
- **Cloud Native**: Docker containers and Azure deployment ready
- **Security**: Environment-based configuration, input validation
- **Testing**: Comprehensive test suite with coverage reporting
- **Code Quality**: Pre-commit hooks, linting, and type checking

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+ (optional, for caching)
- Docker & Docker Compose (for containerized deployment)

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/maaddae/news-aggregator.git
cd news-aggregator
```

### 2. Environment Setup

Create a virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` and configure your settings:
```bash
# Required: Get your API key from https://newsapi.org/
NEWS_API_KEY=your_actual_api_key_here
SECRET_KEY=your-super-secret-key-here

# Optional: Configure database (defaults to SQLite)
DATABASE_URL=sqlite:///./news.db
# For PostgreSQL: postgresql://user:password@localhost:5432/newsdb
```

### 4. Database Setup

Initialize the database:
```bash
cd src
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
"
```

### 5. Run the Application

**Development mode:**
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
cd src
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Start all services (app + PostgreSQL + Redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Build and Run Manually

```bash
# Build the image
docker build -t news-aggregator .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e NEWS_API_KEY=your_api_key \
  -e SECRET_KEY=your_secret_key \
  news-aggregator
```

## 📊 API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint with API info |
| `GET` | `/health` | Health check with dependency status |
| `GET` | `/docs` | Interactive API documentation |

### News Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/news/` | Get paginated news articles |
| `GET` | `/api/v1/news/search` | Search articles by headline |
| `POST` | `/api/v1/news/fetch` | Fetch fresh articles from sources |
| `GET` | `/api/v1/news/sources` | Get available news sources |

### Example Usage

**Get news articles:**
```bash
curl "http://localhost:8000/api/v1/news/?page=1&per_page=10&source=reddit"
```

**Search articles:**
```bash
curl "http://localhost:8000/api/v1/news/search?q=technology&page=1"
```

**Fetch fresh articles:**
```bash
curl -X POST "http://localhost:8000/api/v1/news/fetch?source=reddit"
```

## 🧪 Testing

### Run All Tests

```bash
# Install test dependencies (included in requirements.txt)
pip install pytest pytest-asyncio pytest-cov

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# API tests only
pytest tests/api/
```

## 🔧 Development

### Code Quality Tools

**Install pre-commit hooks:**
```bash
pre-commit install
```

**Manual code quality checks:**
```bash
# Code formatting
black .

# Import sorting
isort .

# Linting
flake8 .

# Type checking
mypy .

# Security checks
bandit -r src/
```

### Project Structure

```
news-aggregator/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   └── app/
│       ├── api/                # API routes and endpoints
│       ├── core/               # Core configuration and logging
│       ├── models/             # Database models
│       ├── schemas/            # Pydantic models for API
│       ├── services/           # Business logic layer
│       └── utils/              # Utility functions
├── tests/                      # Test suite
├── docker-compose.yml          # Multi-service deployment
├── Dockerfile                  # Container configuration
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
└── .env.example               # Environment template
```

## 🚀 Cloud Deployment

### Azure App Service

1. **Create App Service:**
```bash
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name my-news-aggregator \
  --runtime "PYTHON|3.11"
```

2. **Configure environment variables:**
```bash
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name my-news-aggregator \
  --settings NEWS_API_KEY="your_key" SECRET_KEY="your_secret"
```

3. **Deploy:**
```bash
az webapp deployment source config-zip \
  --resource-group myResourceGroup \
  --name my-news-aggregator \
  --src news-aggregator.zip
```

### Azure Container Apps

```bash
# Build and push to registry
docker build -t myregistry.azurecr.io/news-aggregator .
docker push myregistry.azurecr.io/news-aggregator

# Deploy container app
az containerapp create \
  --name news-aggregator \
  --resource-group myResourceGroup \
  --environment myEnvironment \
  --image myregistry.azurecr.io/news-aggregator \
  --target-port 8000 \
  --ingress external
```

## 📈 Monitoring & Observability

### Health Checks

- **Health endpoint**: `/health` - Application and dependency status
- **Readiness endpoint**: `/ready` - Service readiness check

### Logging

Structured logging with configurable levels:
```bash
# Set log level via environment
LOG_LEVEL=DEBUG

# View logs in production
docker logs news-aggregator-app
```

### Metrics (Coming Soon)

- Prometheus metrics endpoint
- Request/response time tracking
- Error rate monitoring
- Database performance metrics

## 🔒 Security

### Environment Variables

Never commit sensitive data. Use environment variables for:
- API keys (`NEWS_API_KEY`)
- Database credentials (`DATABASE_URL`)
- Secret keys (`SECRET_KEY`)

### Security Headers

The application includes:
- CORS configuration
- Trusted host middleware
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install pre-commit hooks (`pre-commit install`)
4. Make your changes with tests
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/maaddae/news-aggregator/issues)
- **Documentation**: `/docs` endpoint when running the application
- **API Reference**: `/redoc` endpoint for alternative documentation

## 🗺️ Roadmap

- [ ] Rate limiting implementation
- [ ] Webhook support for real-time updates
- [ ] User authentication and personalization
- [ ] Content categorization with ML
- [ ] GraphQL API support
- [ ] Kubernetes deployment manifests
- [ ] Advanced caching strategies
- [ ] Content deduplication
- [ ] Analytics dashboard
