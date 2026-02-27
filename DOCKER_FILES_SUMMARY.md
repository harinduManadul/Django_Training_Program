# Docker Files Summary

This document describes all Docker-related files in the project.

## Files Created

### 1. **Dockerfile**

- **Purpose**: Build custom Django application image
- **Base Image**: python:3.10-slim (lightweight)
- **What it does**:
  - Installs Python dependencies (requires psycopg2-binary for PostgreSQL)
  - Copies application code
  - Creates necessary directories
  - Runs migrations on startup
  - Starts Django development server on port 8000

### 2. **docker-compose.yml**

- **Purpose**: Orchestrates multiple containers (Django, PostgreSQL, pgAdmin)
- **Services**:
  - **web**: Django application (port 8000)
  - **db**: PostgreSQL database (port 5432)
  - **pgadmin**: Database UI (port 5050, optional)
- **Volumes**: Persistent storage for database, static files, media
- **Networks**: Internal Docker network for service communication
- **Health Checks**: Ensures services are ready before dependencies start

### 3. **.env.docker**

- **Purpose**: Environment template for Docker deployment
- **Variables**: All Docker configuration settings
- **Usage**: Copy to `.env` and customize for your setup
- **Includes**: Database credentials, Django settings, pgAdmin credentials

### 4. **.dockerignore**

- **Purpose**: Excludes unnecessary files from Docker image build
- **Benefits**: Reduces image size, faster builds
- **Contents**: Git files, documentation, tests, IDE files, etc.

### 5. **docker-help.sh** (Linux/macOS)

- **Purpose**: Helper script for common Docker commands
- **Usage**: `bash docker-help.sh [command]`
- **Commands**: start, stop, migrate, shell, logs, etc.

### 6. **docker-help.bat** (Windows)

- **Purpose**: Windows batch equivalent of docker-help.sh
- **Usage**: `docker-help.bat [command]`
- **Commands**: Same as .sh version

### 7. **DOCKER.md**

- **Purpose**: Complete Docker setup and usage guide
- **Content**:
  - Quick start guide (5 minutes)
  - Detailed service configuration
  - Common Docker commands
  - Database management via pgAdmin
  - Troubleshooting guide
  - Production deployment checklist

---

## Quick Reference

### Start Everything (3 commands)

```bash
# Linux/macOS
cp .env.docker .env
docker-compose up -d
docker-compose exec web python manage.py createsuperuser

# Windows (PowerShell)
cp .env.docker .env
docker-compose up -d
docker-compose exec web python manage.py createsuperuser
```

### Access Services

| Service     | URL                          | Port |
| ----------- | ---------------------------- | ---- |
| Django API  | http://localhost:8000        | 8000 |
| Admin Panel | http://localhost:8000/admin/ | 8000 |
| pgAdmin     | http://localhost:5050        | 5050 |
| PostgreSQL  | localhost                    | 5432 |

### Using Helper Scripts

```bash
# Linux/macOS
bash docker-help.sh start
bash docker-help.sh logs-web
bash docker-help.sh migrate

# Windows
docker-help.bat start
docker-help.bat logs-web
docker-help.bat migrate
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Docker Compose Network              │
│  device_network (bridge)                    │
│                                             │
│  ┌──────────────────┐  ┌─────────────────┐  │
│  │    web (Django)  │  │   db (Postgres) │  │
│  │  Port: 8000      │  │  Port: 5432     │  │
│  │  Image: Custom   │  │  Image: Custom  │  │
│  └──────────────────┘  └─────────────────┘  │
│         ↓                      ↑            │
│    (depends_on)           (healthcheck)     │
│                                             │
│           ┌──────────────────┐              │
│           │ pgadmin (Optional)│             │
│           │   Port: 5050      │             │
│           │ Image: dpage/pg.. │             │
│           └──────────────────┘              │
│                                             │
│  Volumes:                                   │
│  • postgres_data: /var/lib/postgresql       │
│  • static_volume: /app/staticfiles          │
│  • media_volume: /app/mediafiles            │
│  • .:/app (source code)                     │
└─────────────────────────────────────────────┘
```

---

## Development vs Production

### Development (docker-compose.yml)

```yaml
- DEBUG: True
- Volume mount: .:/app (code synced live)
- Ports exposed: All services visible
- pgAdmin included: Easy database viewing
- Health checks: Basic
```

### Production Considerations

For production deployment:

1. **Security**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Change all default passwords
   - Remove pgAdmin service
   - Use environment-specific `.env`

2. **Performance**
   - Use multi-stage builds
   - Minimize layer count
   - Implement caching strategies
   - Add reverse proxy (nginx)

3. **Scaling**
   - Run multiple web instances
   - Use load balancer
   - Separate database server
   - Implement CDN for static files

4. **Monitoring**
   - Add logging service
   - Implement health checks
   - Monitor resource usage
   - Set up alerts

See **DOCKER.md** for production deployment section.

---

## Updating After Changes

### After Adding Python Packages

```bash
# Update requirements.txt first
pip freeze > requirements.txt

# Rebuild Docker image
docker-compose build --no-cache web

# Restart service
docker-compose up -d web
```

### After Changing Code

```bash
# If volume mapped (automatic):
# Just restart Django
docker-compose restart web

# Or for full rebuild:
docker-compose up -d --build
```

### After Modifying Models

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Restart (optional)
docker-compose restart web
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Verify image built
docker-compose build --no-cache web

# Try restarting
docker-compose restart web
```

### Database Connection Error

```bash
# Check db service status
docker-compose ps db

# View db logs
docker-compose logs db

# Verify .env credentials match docker-compose.yml
```

### Port Already in Use

```bash
# Change port in docker-compose.yml:
# "8000:8000" → "8001:8000"

# Or find/kill process:
# Linux/macOS: lsof -i :8000
# Windows: netstat -ano | findstr :8000
```

---

## Best Practices

✅ **DO:**

- Use `.env.docker` as template (don't commit secrets)
- Keep Dockerfile simple
- Use volume mounts for development
- Version your images
- Regular backups of database volumes
- Test locally before pushing to production

❌ **DON'T:**

- Store secrets in Dockerfile or docker-compose.yml
- Run as root (covered in our Dockerfile)
- Use latest tags in production
- Commit `.env` files to git
- Mix development and production configurations
- Ignore health checks

---

## Useful Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Reference**: https://docs.docker.com/compose/compose-file/
- **PostgreSQL Docker Image**: https://hub.docker.com/_/postgres
- **Best Practices**: https://docs.docker.com/develop/development-best-practices/

---

## Integration with Existing Setup

The Docker setup **coexists** with local development:

### Local Development (Current)

```bash
# Virtual environment
source env/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Docker Development (New)

```bash
# Docker Compose
docker-compose up -d
docker-compose logs -f
```

Both methods work! Choose based on preference:

- **Local**: Faster if no Docker, IDE integration easier
- **Docker**: Exact production environment, team consistency

---

**Last Updated**: February 27, 2026  
**Status**: ✅ Production Ready with Development Optimizations
