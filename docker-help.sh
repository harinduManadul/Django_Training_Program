#!/bin/bash

# Device Monitoring System - Docker Helper Script
# Usage: ./docker-help.sh [command]

set -e

COMPOSE_FILE="docker-compose.yml"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

show_help() {
    cat << EOF
Device Monitoring System - Docker Helper

Usage: bash docker-help.sh [command]

Commands:
    start           Start all Docker services
    stop            Stop all Docker services
    restart         Restart all services
    logs            View logs from all services
    logs-web        View Django web service logs
    logs-db         View PostgreSQL database logs
    shell           Open Django shell
    migrate         Run Django migrations
    superuser       Create a Django superuser
    test            Run tests
    check           Run Django system checks
    clean           Remove stopped containers
    clean-all       Remove all containers and volumes (DELETE DATA!)
    ps              Show running containers
    exec            Execute a command (usage: bash docker-help.sh exec [command])
    help            Show this help message

Examples:
    bash docker-help.sh start
    bash docker-help.sh logs-web
    bash docker-help.sh exec python manage.py shell
    bash docker-help.sh superuser

EOF
}

# Commands
start_services() {
    print_header "Starting Services"
    docker-compose up -d
    print_success "Services started!"
    echo -e "${GREEN}Access the application:${NC}"
    echo "  Django: http://localhost:8000"
    echo "  Admin: http://localhost:8000/admin/"
    echo "  pgAdmin: http://localhost:5050"
}

stop_services() {
    print_header "Stopping Services"
    docker-compose stop
    print_success "Services stopped!"
}

restart_services() {
    print_header "Restarting Services"
    docker-compose restart
    print_success "Services restarted!"
}

view_logs() {
    print_header "Showing All Logs (Press Ctrl+C to exit)"
    docker-compose logs -f
}

view_web_logs() {
    print_header "Showing Django Web Logs (Press Ctrl+C to exit)"
    docker-compose logs -f web
}

view_db_logs() {
    print_header "Showing PostgreSQL Logs (Press Ctrl+C to exit)"
    docker-compose logs -f db
}

django_shell() {
    print_header "Opening Django Shell"
    docker-compose exec web python manage.py shell
}

run_migrations() {
    print_header "Running Migrations"
    docker-compose exec web python manage.py migrate
    print_success "Migrations completed!"
}

create_superuser() {
    print_header "Creating Superuser"
    docker-compose exec web python manage.py createsuperuser
}

run_tests() {
    print_header "Running Tests"
    docker-compose exec web python manage.py test
}

system_check() {
    print_header "Running System Checks"
    docker-compose exec web python manage.py check
}

show_status() {
    print_header "Container Status"
    docker-compose ps
}

clean_stopped() {
    print_header "Cleaning Stopped Containers"
    docker system prune -f
    print_success "Cleanup complete!"
}

clean_all() {
    print_header "WARNING: This will remove all containers and volumes!"
    read -p "Are you sure? This DELETES all data! (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        docker-compose down -v
        print_success "All containers and volumes removed!"
    else
        echo "Cancelled."
    fi
}

exec_command() {
    print_header "Executing Command in Web Container"
    shift  # Remove 'exec' from arguments
    docker-compose exec web "$@"
}

# Main logic
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        view_logs
        ;;
    logs-web)
        view_web_logs
        ;;
    logs-db)
        view_db_logs
        ;;
    shell)
        django_shell
        ;;
    migrate)
        run_migrations
        ;;
    superuser)
        create_superuser
        ;;
    test)
        run_tests
        ;;
    check)
        system_check
        ;;
    ps)
        show_status
        ;;
    clean)
        clean_stopped
        ;;
    clean-all)
        clean_all
        ;;
    exec)
        exec_command "$@"
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
