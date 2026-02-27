# Docker & Docker Compose Setup Guide

This guide explains how to run the Device Monitoring System using Docker and Docker Compose.

## Prerequisites

- **Docker** installed (https://www.docker.com/products/docker-desktop)
- **Docker Compose** (comes with Docker Desktop)
- Git

## Quick Start (5 Minutes)

### Step 1: Clone and Navigate to Project

```bash
cd Django_Training_Program
```

### Step 2: Copy Environment File

```bash
cp .env.docker .env
```

Optionally, edit `.env` to change:

- `SECRET_KEY`: Generate a strong key
- `DB_PASSWORD`: Strong database password
- `DEBUG`: Set to `False` for production

### Step 3: Start Docker Compose

```bash
docker-compose up -d
```

This will:

- Build the Django image
- Start PostgreSQL (port 5432)
- Start Django web server (port 8000)
- Start pgAdmin (port 5050)

### Step 4: Initialize Database

```bash
docker-compose exec web python manage.py createsuperuser
```

### Step 5: Access Services

- **Django App**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin/
- **pgAdmin**: http://localhost:5050
  - Email: admin@example.com (or your PGADMIN_EMAIL)
  - Password: admin (or your PGADMIN_PASSWORD)

---

## Detailed Docker Compose Setup

### What's Included

| Service     | Image               | Port | Purpose                |
| ----------- | ------------------- | ---- | ---------------------- |
| **web**     | Custom (Dockerfile) | 8000 | Django application     |
| **db**      | postgres:15-alpine  | 5432 | PostgreSQL database    |
| **pgadmin** | dpage/pgadmin4      | 5050 | Database UI (optional) |

### Configuration Files

- **Dockerfile**: Builds custom Django image
- **docker-compose.yml**: Orchestrates all services
- **.env.docker**: Environment template (copy to .env)

---

## Common Commands

### Start Services

```bash
# Start all services in background
docker-compose up -d

# Start with logs displayed
docker-compose up

# Start specific service
docker-compose up -d web
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop but keep data
docker-compose stop

# Stop and remove volumes (DELETE DATA)
docker-compose down -v
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow web service logs
docker-compose logs -f web

# View last 50 lines
docker-compose logs --tail=50
```

### Run Commands Inside Container

```bash
# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Django shell
docker-compose exec web python manage.py shell

# Type checking
docker-compose exec web mypy . --show-error-codes

# System checks
docker-compose exec web python manage.py check
```

### Database Management

```bash
# Connect to PostgreSQL with psql
docker-compose exec db psql -U device_user -d device_monitoring

# List databases
\l

# Exit psql
\q

# Backup database
docker-compose exec db pg_dump -U device_user device_monitoring > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U device_user device_monitoring
```

---

## Docker Compose Environment Variables

Environment variables control the Docker setup. Edit `.env` file:

```env
# Django Settings
SECRET_KEY=your-strong-secret-key
DEBUG=False                              # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1,web

# Database
DB_NAME=device_monitoring
DB_USER=device_user
DB_PASSWORD=your_strong_password        # Change this!
DB_HOST=db                              # Internal Docker service name
DB_PORT=5432                            # PostgreSQL default port

# pgAdmin (for database UI)
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin                  # Change this!
```

---

## Accessing Services

### Django Application

```bash
# Web browser
http://localhost:8000

# API Login example
curl -X POST http://localhost:8000/useapi/userrouter/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

### Django Admin

```bash
http://localhost:8000/admin/
# Username: admin (or whatever you created)
# Password: (whatever you set during createsuperuser)
```

### pgAdmin (Database GUI)

```bash
http://localhost:5050

# First login:
Email: admin@example.com
Password: admin

# Add Server connection:
1. Right-click "Servers" → "Register" → "Server"
2. General tab:
   - Name: device_monitoring
3. Connection tab:
   - Host: db
   - Port: 5432
   - Username: device_user
   - Password: (your DB_PASSWORD from .env)
4. Click Save
```

---

## Volume Management

Docker Compose uses named volumes to persist data:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect django_training_program_postgres_data

# Remove specific volume (DELETE DATA)
docker volume rm django_training_program_postgres_data

# Remove all unused volumes
docker volume prune
```

### Volume Mapping

| Host            | Container                  | Purpose          |
| --------------- | -------------------------- | ---------------- |
| `postgres_data` | `/var/lib/postgresql/data` | Database files   |
| `static_volume` | `/app/staticfiles`         | Static files     |
| `media_volume`  | `/app/mediafiles`          | User uploads     |
| `pgadmin_data`  | `/var/lib/pgadmin`         | pgAdmin settings |
| `.` (project)   | `/app`                     | Source code      |

---

## Building & Rebuilding Images

### Build Image

```bash
# Build without cache
docker-compose build --no-cache

# Build specific service
docker-compose build web

# Build with progress shown
docker-compose build --progress=plain
```

### Rebuild After Changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Rebuild only web service
docker-compose up -d --build web
```

---

## Troubleshooting

### Issue: "Cannot connect to Docker daemon"

**Cause**: Docker service not running

**Solution**:

```bash
# Windows: Start Docker Desktop
# macOS: open /Applications/Docker.app
# Linux: sudo systemctl start docker
```

### Issue: Port 8000 already in use

**Cause**: Another service using port 8000

**Solution**:

```bash
# Change port in docker-compose.yml
# From: "8000:8000"
# To:   "8001:8000"

# Or stop the other service
docker-compose down
```

### Issue: "db service unhealthy"

**Cause**: PostgreSQL not started

**Cause**: Check logs

```bash
docker-compose logs db
```

**Solution**: Wait a few seconds and restart

```bash
docker-compose restart db
```

### Issue: "ModuleNotFoundError" after adding dependencies

**Cause**: Dependencies not installed in image

**Solution**:

```bash
# Rebuild the image
docker-compose build --no-cache web

# Restart services
docker-compose up -d
```

### Issue: Database connection error

**Cause**: Wrong credentials in .env

**Solution**:

```bash
# Check .env file matches docker-compose.yml
cat .env

# Verify in running container
docker-compose exec web env | grep DB_

# Restart services
docker-compose down
docker-compose up -d
```

### Issue: Can't access pgAdmin

**Cause**: pgAdmin service not running

**Solution**:

```bash
# Check status
docker-compose ps

# Restart pgAdmin
docker-compose restart pgadmin

# View logs
docker-compose logs pgadmin
```

---

## Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Change all default passwords in `.env`
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS/SSL
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Use strong `DB_PASSWORD`
- [ ] Backup database regularly

### Environment File for Production

Create `.env.production`:

```env
SECRET_KEY=<generate-strong-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=device_monitoring_prod
DB_USER=prod_user
DB_PASSWORD=<very-strong-password>
DB_HOST=db
DB_PORT=5432
```

Run with production env:

```bash
docker-compose --env-file .env.production up -d
```

### Scaling (Advanced)

```bash
# Run multiple web instances
docker-compose up -d --scale web=3

# Use load balancer (nginx) in front
# See: https://docs.docker.com/compose/networking/
```

---

## Database Persistence

Data persists between container restarts via volumes:

```bash
# Stop containers (data preserved)
docker-compose stop

# Start again (data restored)
docker-compose start

# Remove everything (INCLUDING DATA)
docker-compose down -v
```

---

## Health Checks

Docker Compose includes health checks:

```bash
# View health status
docker-compose ps

# Should show: "healthy" for db service

# Re-run health check
docker-compose restart db
```

---

## Cleanup

### Remove Unused Resources

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove all (orphaned) resources
docker system prune

# Full cleanup (REMOVES ALL DOCKER DATA)
docker system prune -a --volumes
```

---

## Docker Compose vs Local Development

| Feature              | Docker              | Local                      |
| -------------------- | ------------------- | -------------------------- |
| **Setup Time**       | 5 min               | 15 min                     |
| **Database**         | PostgreSQL (latest) | SQLite or local PostgreSQL |
| **Isolation**        | Complete (safe)     | System-wide                |
| **Performance**      | Good                | Slightly faster            |
| **Team Consistency** | Same for everyone   | Varies                     |
| **Deployment**       | Same as prod        | Can differ from prod       |

---

## Next Steps

1. **Run the application**

   ```bash
   docker-compose up -d
   docker-compose exec web python manage.py createsuperuser
   ```

2. **Access services**
   - Django: http://localhost:8000
   - Admin: http://localhost:8000/admin/
   - pgAdmin: http://localhost:5050

3. **Test API**

   ```bash
   curl -X POST http://localhost:8000/useapi/userrouter/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "your_password"}'
   ```

4. **Monitor services**
   ```bash
   docker-compose logs -f
   ```

---

## Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Reference**: https://docs.docker.com/compose/compose-file/
- **PostgreSQL in Docker**: https://hub.docker.com/_/postgres
- **pgAdmin Documentation**: https://www.pgadmin.org/docs/

---

**Last Updated**: February 27, 2026  
**Docker Version**: 3.9 (Compose file format)  
**Status**: ✅ Production Ready
