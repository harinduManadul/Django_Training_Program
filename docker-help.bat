@echo off
REM Device Monitoring System - Docker Helper Script for Windows
REM Usage: docker-help.bat [command]

setlocal enabledelayedexpansion

if "%1%"=="" goto help
if "%1%"=="help" goto help

if "%1%"=="start" goto start
if "%1%"=="stop" goto stop
if "%1%"=="restart" goto restart
if "%1%"=="logs" goto logs
if "%1%"=="logs-web" goto logs_web
if "%1%"=="logs-db" goto logs_db
if "%1%"=="shell" goto shell
if "%1%"=="migrate" goto migrate
if "%1%"=="superuser" goto superuser
if "%1%"=="test" goto test
if "%1%"=="check" goto check
if "%1%"=="ps" goto status
if "%1%"=="clean" goto clean
if "%1%"=="clean-all" goto clean_all

echo Unknown command: %1%
goto help

:start
echo === Starting Services ===
docker-compose up -d
echo.
echo Services started!
echo.
echo Access the application at:
echo   Django: http://localhost:8000
echo   Admin: http://localhost:8000/admin/
echo   pgAdmin: http://localhost:5050
goto end

:stop
echo === Stopping Services ===
docker-compose stop
echo Services stopped!
goto end

:restart
echo === Restarting Services ===
docker-compose restart
echo Services restarted!
goto end

:logs
echo === Showing All Logs (Press Ctrl+C to exit) ===
docker-compose logs -f
goto end

:logs_web
echo === Showing Django Web Logs (Press Ctrl+C to exit) ===
docker-compose logs -f web
goto end

:logs_db
echo === Showing PostgreSQL Logs (Press Ctrl+C to exit) ===
docker-compose logs -f db
goto end

:shell
echo === Opening Django Shell ===
docker-compose exec web python manage.py shell
goto end

:migrate
echo === Running Migrations ===
docker-compose exec web python manage.py migrate
echo Migrations completed!
goto end

:superuser
echo === Creating Superuser ===
docker-compose exec web python manage.py createsuperuser
goto end

:test
echo === Running Tests ===
docker-compose exec web python manage.py test
goto end

:check
echo === Running System Checks ===
docker-compose exec web python manage.py check
goto end

:status
echo === Container Status ===
docker-compose ps
goto end

:clean
echo === Cleaning Stopped Containers ===
docker system prune -f
echo Cleanup complete!
goto end

:clean_all
echo !WARNING: This will remove all containers and volumes!
echo !This DELETES all data!
echo.
set /p confirm="Are you sure? (yes/no): "
if /i "%confirm%"=="yes" (
    docker-compose down -v
    echo All containers and volumes removed!
) else (
    echo Cancelled.
)
goto end

:help
echo Device Monitoring System - Docker Helper
echo.
echo Usage: docker-help.bat [command]
echo.
echo Commands:
echo   start           Start all Docker services
echo   stop            Stop all Docker services
echo   restart         Restart all services
echo   logs            View logs from all services
echo   logs-web        View Django web service logs
echo   logs-db         View PostgreSQL database logs
echo   shell           Open Django shell
echo   migrate         Run Django migrations
echo   superuser       Create a Django superuser
echo   test            Run tests
echo   check           Run Django system checks
echo   ps              Show running containers
echo   clean           Remove stopped containers
echo   clean-all       Remove all containers and volumes (DELETE DATA!)
echo   help            Show this help message
echo.
echo Examples:
echo   docker-help.bat start
echo   docker-help.bat logs-web
echo   docker-help.bat superuser
goto end

:end
endlocal
