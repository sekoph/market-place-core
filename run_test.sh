#!/bin/bash

echo "🧪 Running tests..."

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

# Function to run tests for a service
run_test() {
    local service=$1
    
    print_status "Running tests for ${service}..."
    
    if docker-compose exec -T ${service} python manage.py test --noinput; then
        print_success "Tests passed for ${service}"
        return 0
    else
        print_error "Tests failed for ${service}"
        return 1
    fi
}

# Main test function
run_tests() {
    local services=("customer" "order" "product")
    local failed_services=()
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 5
    
    for service in "${services[@]}"; do
        echo ""
        if ! run_test "${service}"; then
            failed_services+=("${service}")
        fi
        echo ""
    done
    
    # Summary
    echo "=================================================="
    if [ ${#failed_services[@]} -eq 0 ]; then
        print_success "🎉 All tests passed successfully!"
    else
        print_error "Some tests failed:"
        for failed_service in "${failed_services[@]}"; do
            echo -e "  ${RED}- ${failed_service}${NC}"
        done
        echo ""
        print_error "Please check the test output above for details"
        exit 1
    fi
}

# Run the tests
run_tests