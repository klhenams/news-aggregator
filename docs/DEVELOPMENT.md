# Development Setup

This document explains how to set up and work with the News Aggregator in development mode.

## Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.dev.example .env.dev
   ```

2. **Start development environment:**
   ```bash
   make dev
   ```

3. **Open your browser:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - PgAdmin: http://localhost:5050 (admin@example.com / admin)
   - RedisInsight: http://localhost:8081 (Redis admin interface)
   - Jupyter Lab: http://localhost:8888

## Development Tools

### Available Services

- **web**: Main FastAPI application with hot reloading
- **db**: PostgreSQL database (port 5433)
- **redis**: Redis cache (port 6380)
- **jupyter**: Jupyter Lab for data exploration
- **pgadmin**: Database administration interface
- **redis-admin**: RedisInsight administration interface (ARM64 compatible)
- **locust**: Load testing tool (optional)
- **docs**: Documentation server (optional)

### Make Commands

```bash
# Start development environment
make dev

# Run tests
make test
make test-watch    # Watch mode
make test-cov      # With coverage

# Code quality
make lint          # Run all linters
make format        # Format code
make mypy          # Type checking

# Shell access
make shell         # Web container shell
make db-shell      # Database shell
make redis-cli     # Redis CLI

# Logs
make logs          # All services
make web-logs      # Just web service

# Documentation
make docs          # Start docs server

# Load testing
make load-test     # Start Locust

# Cleanup
make clean         # Stop and remove containers
make clean-all     # Remove everything including images
```

## Development Workflow

### 1. Code Changes
- Edit files in `src/` directory
- Changes are automatically reloaded in the web container
- Use your preferred IDE/editor

### 2. Testing
```bash
# Run all tests
make test

# Run specific test file
make shell
pytest tests/test_specific.py

# Run with coverage
make test-cov
```

### 3. Database Changes
```bash
# Access database
make db-shell

# Or use PgAdmin at http://localhost:5050
```

### 4. Debugging
```bash
# Access container shell
make shell

# Use debugpy for remote debugging (port 5678 exposed)
# Add this to your code:
# import debugpy; debugpy.listen(("0.0.0.0", 5678)); debugpy.wait_for_client()
```

### 5. Load Testing
```bash
# Start Locust
make load-test

# Open http://localhost:8089
# Configure users and spawn rate
```

## Environment Variables

Development environment uses `.env.dev` file:

```bash
# Required
NEWS_API_KEY=your_api_key
REDDIT_USER_AGENT=YourApp/1.0

# Optional (have defaults)
DEBUG=true
LOG_LEVEL=DEBUG
DATA_SOURCE=database
```

## Database

Development uses PostgreSQL with:
- Database: `newsdb_dev`
- User: `postgres`
- Password: `password`
- Port: `5433` (to avoid conflicts)

Access via:
- PgAdmin: http://localhost:5050
- Direct connection: `localhost:5433`
- Container shell: `make db-shell`

## Redis

Development Redis:
- Port: `6380` (to avoid conflicts)
- No password
- Database: 0

Access via:
- RedisInsight: http://localhost:8081
- CLI: `make redis-cli`

## Hot Reloading

The development setup includes:
- **FastAPI**: Automatic reload on Python file changes
- **Volumes**: Source code mounted as volumes
- **Uvicorn**: `--reload` flag enabled

## IDE Integration

### VS Code
1. Install Python extension
2. Set Python interpreter to container Python:
   ```bash
   docker-compose -f docker-compose.dev.yml exec web which python
   ```
3. Configure debugger to connect to port 5678

### PyCharm
1. Configure Docker Compose interpreter
2. Set breakpoints and debug remotely
3. Use port 5678 for debugpy connection

## Troubleshooting

### Port Conflicts
Development uses different ports:
- PostgreSQL: 5433 (instead of 5432)
- Redis: 6380 (instead of 6379)

### Container Issues
```bash
# Rebuild containers
make dev-build

# Check logs
make logs

# Clean restart
make clean && make dev
```

### Database Issues
```bash
# Reset database
make db-reset

# Access database directly
make db-shell
```

### Permission Issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER src/
```

## Performance

### Profiling
```bash
# CPU profiling
make profile

# Memory profiling
make shell
memory_profiler your_script.py
```

### Monitoring
- Check logs: `make logs`
- Health endpoint: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics (if implemented)

## Production Differences

Development environment differs from production:
- Debug mode enabled
- Verbose logging
- Development database
- Hot reloading
- Additional tools (Jupyter, PgAdmin, etc.)
- Relaxed security settings
