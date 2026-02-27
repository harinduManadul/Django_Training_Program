# PostgreSQL Setup Guide

This guide explains how to set up PostgreSQL for the Device Monitoring System.

## 📋 Current Status

✅ **Django Settings**: Already configured for PostgreSQL  
✅ **Environment Variables**: Template provided in `.env.example`  
✅ **Database Driver**: `psycopg2-binary` added to `requirements.txt`

---

## 🚀 Option 1: Use Local PostgreSQL (Development)

### Step 1: Install PostgreSQL

**Windows:**

- Download from https://www.postgresql.org/download/windows/
- Run installer, remember the password you set
- PostgreSQL will run as a service

**macOS:**

```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 2: Create Database

**Windows/macOS/Linux:**

```bash
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE device_monitoring;
CREATE USER device_user WITH PASSWORD 'your_secure_password';
ALTER ROLE device_user SET client_encoding TO 'utf8';
ALTER ROLE device_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE device_user SET default_transaction_deferrable TO on;
ALTER ROLE device_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE device_monitoring TO device_user;
\q
```

### Step 3: Update `.env` File

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration - Local PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=device_monitoring
DB_USER=device_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Start Server

```bash
python manage.py runserver 8000
```

---

## ☁️ Option 2: Use Online PostgreSQL (Neon - Recommended for Cloud)

### Step 1: Create Neon Account

1. Go to https://neon.tech
2. Sign up with email
3. Create new project (free tier)

### Step 2: Get Connection String

After creating project, copy the connection string from Neon dashboard:

```
postgresql://neon_user:neon_password@ep-xxxxx.neon.tech/device_monitoring?sslmode=require
```

### Step 3: Update `.env` File

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration - Neon Online PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=device_monitoring
DB_USER=neon_user
DB_PASSWORD=neon_password_from_dashboard
DB_HOST=ep-xxxxx.neon.tech
DB_PORT=5432
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Start Server

```bash
python manage.py runserver 8000
```

---

## 🔍 Verify PostgreSQL Connection

### Test Database Connection

```bash
python manage.py dbshell
```

If successful, you'll see PostgreSQL prompt:

```
device_monitoring=#
```

Type `\q` to exit.

### Verify Migrations

```bash
python manage.py showmigrations
```

Should show all migrations with ✓ checkmarks.

### Check Database Admin

```bash
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print(connection.connection)  # Shows connection info
>>> from users.models import User
>>> User.objects.count()  # Should work
```

---

## 📊 PostgreSQL Configuration Comparison

| Feature           | Local        | Neon          | DigitalOcean |
| ----------------- | ------------ | ------------- | ------------ |
| **Setup Time**    | 10 min       | 2 min         | 10 min       |
| **Cost**          | Free         | Free/Paid     | $15/mo       |
| **Storage**       | Unlimited    | 0.5GB free    | 25GB min     |
| **Always Online** | Your machine | Yes ☁️        | Yes ☁️       |
| **Backups**       | Manual       | Auto ✓        | Auto ✓       |
| **Best For**      | Development  | Testing/Hobby | Production   |

---

## ⚠️ Common Issues & Solutions

### Issue 1: "could not connect to server: Connection refused"

**Cause**: PostgreSQL not running

**Solution - Windows:**

```bash
# Start PostgreSQL service
net start postgresql-x64-15
```

**Solution - macOS:**

```bash
brew services start postgresql@15
```

**Solution - Linux:**

```bash
sudo systemctl start postgresql
```

### Issue 2: "password authentication failed for user"

**Cause**: Wrong password in `.env`

**Solution**:

```bash
# Reset password in PostgreSQL
psql -U postgres
ALTER USER device_user WITH PASSWORD 'new_password';
\q
```

Then update `.env` with new password.

### Issue 3: "database 'device_monitoring' does not exist"

**Cause**: Database not created

**Solution**:

```bash
psql -U postgres
CREATE DATABASE device_monitoring;
\q
```

### Issue 4: "permission denied for schema public"

**Cause**: User doesn't have permissions

**Solution**:

```bash
psql -U postgres -d device_monitoring
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO device_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO device_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO device_user;
\q
```

### Issue 5: "SSL connection error" (Neon)

**Cause**: SSL not enabled

**Solution**: Ensure `.env` has port 5432 and Neon connection string includes `?sslmode=require`

---

## 🔒 Security Best Practices

### Local Development

```env
DB_PASSWORD=local_dev_password_123
```

### Online/Production

```bash
# Generate strong password (bash/Linux/macOS)
openssl rand -base64 32

# Or use online generator: https://passwordsgenerator.net/
```

### Database User Privileges

**Principle of Least Privilege** (Recommended):

```sql
-- Create app user with limited privileges
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE device_monitoring TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

---

## 📝 Switching Between SQLite and PostgreSQL

You can easily switch between databases:

### Use SQLite (Development)

```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### Use PostgreSQL (Production)

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=device_monitoring
DB_USER=device_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

Just restart the server and Django automatically uses the configured database!

---

## 🧪 Test Data Commands

### Create Test User

```bash
python manage.py shell
>>> from users.models import User
>>> from django.contrib.auth.hashers import make_password
>>> user = User.objects.create(
...     name="Test User",
...     username="testuser",
...     email="test@example.com",
...     password=make_password("testpass123"),
...     role="user"
... )
>>> user.save()
```

### Create Test Device

```bash
>>> from devices.models import Device
>>> user = User.objects.get(username="testuser")
>>> device = Device.objects.create(
...     name="Test Sensor",
...     type="sensor",
...     location="Building A",
...     owner=user
... )
>>> device.save()
```

### Create Test Telemetry

```bash
>>> from telemerty.models import DeviceTelemetry
>>> telemetry = DeviceTelemetry.objects.create(
...     device=device,
...     status="ONLINE",
...     cpu=45.5,
...     memory=62.3,
...     temperature=28.5
... )
>>> telemetry.save()
```

---

## 📊 View Database in pgAdmin (GUI)

### Step 1: Install pgAdmin

```bash
pip install pgadmin4
```

### Step 2: Start pgAdmin

```bash
pgadmin4
```

Then open: `http://localhost:5050`

### Step 3: Connect to Database

1. Right-click "Servers" → "Register" → "Server"
2. Name: `device_monitoring`
3. Host: `localhost`
4. Port: `5432`
5. User: `device_user`
6. Password: Your password

Now you can browse tables, run queries, and manage data visually!

---

## 📋 Checklist

Before going to production:

- [ ] Database created and accessible
- [ ] User created with proper permissions
- [ ] `.env` file configured (not committed to git)
- [ ] Dependencies installed (`psycopg2-binary`)
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Test data created
- [ ] Admin panel accessible at `/admin/`
- [ ] API endpoints tested with Postman/curl
- [ ] `DEBUG=False` set for production
- [ ] Strong `SECRET_KEY` set for production
- [ ] Backups configured (if using cloud)

---

## 🆘 Need Help?

**PostgreSQL Documentation**: https://www.postgresql.org/docs/  
**Neon Docs**: https://neon.tech/docs/  
**Django Database Settings**: https://docs.djangoproject.com/en/6.0/ref/settings/#databases

---

**Last Updated**: February 27, 2026
