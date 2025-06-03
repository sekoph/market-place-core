#!/bin/bash

# Django Microservices Kind Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v kind &> /dev/null; then
        print_error "Kind is not installed. Please install Kind first."
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    print_status "All prerequisites are installed ✓"
}

# Build Docker images
build_images() {
    print_header "Building Docker Images"
    
    # Check if Dockerfiles exist
    services=("auth-service" "customer-service" "order-service" "product-service")
    
    for service in "${services[@]}"; do
        if [ ! -f "${service}/Dockerfile" ]; then
            print_error "Dockerfile not found for ${service}. Please ensure ${service}/Dockerfile exists."
            exit 1
        fi
    done
    
    # Build images
    for service in "${services[@]}"; do
        print_status "Building ${service}..."
        docker build -f ${service}/Dockerfile -t ${service}:latest . || {
            print_error "Failed to build ${service}"
            exit 1
        }
    done
    
    print_status "All images built successfully ✓"
}

# Create Kind cluster
create_cluster() {
    print_header "Creating Kind Cluster"
    
    # Check if cluster already exists
    if kind get clusters | grep -q "microservices"; then
        print_warning "Cluster 'microservices' already exists. Deleting..."
        kind delete cluster --name microservices
    fi
    
    print_status "Creating new Kind cluster..."
    kind create cluster --config kind-config.yaml --name microservices || {
        print_error "Failed to create Kind cluster"
        exit 1
    }
    
    # Wait for cluster to be ready
    print_status "Waiting for cluster to be ready..."
    kubectl wait --for=condition=Ready nodes --all --timeout=300s
    
    print_status "Kind cluster created successfully ✓"
}

# Load images into Kind
load_images() {
    print_header "Loading Images into Kind"
    
    services=("auth-service" "customer-service" "order-service" "product-service")
    
    for service in "${services[@]}"; do
        print_status "Loading ${service}:latest..."
        kind load docker-image ${service}:latest --name microservices || {
            print_error "Failed to load ${service} image"
            exit 1
        }
    done
    
    print_status "All images loaded successfully ✓"
}

# Deploy to Kubernetes
deploy_services() {
    print_header "Deploying Services to Kubernetes"
    
    if [ ! -f "microservices-k8s.yaml" ]; then
        print_error "microservices-k8s.yaml not found. Please ensure the Kubernetes manifest file exists."
        exit 1
    fi
    
    print_status "Applying Kubernetes manifests..."
    kubectl apply -f microservices-k8s.yaml || {
        print_error "Failed to apply Kubernetes manifests"
        exit 1
    }
    
    print_status "Services deployed successfully ✓"
}

# Wait for pods to be ready
wait_for_pods() {
    print_header "Waiting for Pods to be Ready"
    
    print_status "Waiting for all pods to be ready (this may take a few minutes)..."
    
    # Wait for databases first
    kubectl wait --for=condition=Ready pod -l app=auth-db -n microservices --timeout=300s
    kubectl wait --for=condition=Ready pod -l app=customer-db -n microservices --timeout=300s
    kubectl wait --for=condition=Ready pod -l app=order-db -n microservices --timeout=300s
    kubectl wait --for=condition=Ready pod -l app=product-db -n microservices --timeout=300s
    kubectl wait --for=condition=Ready pod -l app=keycloak-postgres -n microservices --timeout=300s
    
    # Wait for infrastructure services
    kubectl wait --for=condition=Ready pod -l app=rabbitmq -n microservices --timeout=300s
    kubectl wait --for=condition=Ready pod -l app=redis -n microservices --timeout=300s
    
    # Wait for Keycloak
    kubectl wait --for=condition=Ready pod -l app=keycloak -n microservices --timeout=300s
    
    # Wait for Django services
    kubectl wait --for=condition=Ready pod -l app=auth-service -n microservices --timeout=300s
    kubectl wait --for=condition=Ready pod -l app=customer-service -n microservices --timeout=300s
    kubectl wait --for=condition=Ready pod -l app=order-service -n microservices --timeout=300s
    kubectl wait --for=condition=Ready pod -l app=product-service -n microservices --timeout=300s
    
    print_status "All pods are ready ✓"
}

# Run Django migrations
run_migrations() {
    print_header "Running Django Migrations"
    
    services=("auth-service" "customer-service" "order-service" "product-service")
    
    for service in "${services[@]}"; do
        print_status "Running migrations for ${service}..."
        kubectl exec -n microservices deployment/${service} -- python manage.py migrate || {
            print_warning "Migrations failed for ${service} (this might be expected if migrations don't exist)"
        }
    done
    
    print_status "Migrations completed ✓"
}

# Show deployment status
show_status() {
    print_header "Deployment Status"
    
    print_status "Pods:"
    kubectl get pods -n microservices
    
    echo ""
    print_status "Services:"
    kubectl get services -n microservices
    
    echo ""
    print_status "Access URLs:"
    echo "Auth Service: http://localhost:30000"
    echo "Customer Service: http://localhost:30001"
    echo "Order Service: http://localhost:30002"
    echo "Product Service: http://localhost:30003"
    echo "Keycloak: http://localhost:30080"
    echo "RabbitMQ Management: http://localhost:15672"
}

# Main execution
main() {
    print_header "Django Microservices Kind Deployment"
    
    check_prerequisites
    build_images
    create_cluster
    load_images
    deploy_services
    wait_for_pods
    run_migrations
    show_status
    
    print_header "Deployment Complete!"
    print_status "Your Django microservices are now running on Kind ✓"
    print_status "Use 'kubectl get pods -n microservices' to check pod status"
    print_status "Use 'kubectl logs -n microservices deployment/<service-name>' to view logs"
}

# Handle script arguments
case "${1:-}" in
    "clean")
        print_header "Cleaning Up"
        kubectl delete namespace microservices --ignore-not-found=true
        kind delete cluster --name microservices --quiet
        print_status "Cleanup complete ✓"
        ;;
    "status")
        show_status
        ;;
    "logs")
        if [ -z "${2:-}" ]; then
            print_error "Please specify a service name: $0 logs <service-name>"
            exit 1
        fi
        kubectl logs -n microservices deployment/$2 -f
        ;;
    *)
        main
        ;;
esac