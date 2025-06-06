#!/bin/bash

echo "🚀 Running migrations..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored status messages
print_status() {
    echo -e "${YELLOW}📦 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${RED}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to run migration for a service
run_migration() {
    local service=$1
    
    print_status "Running migrations for ${service}..."
    
    if docker-compose exec -T ${service} python manage.py migrate --noinput; then
        print_success "Migrations completed for ${service}"
        return 0
    else
        print_warning "Migrations failed for ${service} (this might be expected if migrations don't exist)"
        return 1
    fi
}

# Main migration function
run_migrations() {
    local services=("auth" "customer" "order" "product")
    local failed_services=()
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 5
    
    for service in "${services[@]}"; do
        echo ""
        if ! run_migration "${service}"; then
            failed_services+=("${service}")
        fi
        echo ""
    done
    
    # Summary
    echo "=================================================="
    if [ ${#failed_services[@]} -eq 0 ]; then
        print_success "🎉 All migrations completed successfully!"
    else
        print_error "Some migrations failed:"
        for failed_service in "${failed_services[@]}"; do
            echo -e "  ${RED}- ${failed_service}${NC}"
        done
        echo ""
        print_warning "Note: This might be normal if some services don't have migrations yet"
    fi
}

# Run the migrations
run_migrations
