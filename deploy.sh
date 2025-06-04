#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    
    # Check required commands
    for cmd in docker kind kubectl; do
        if ! command -v $cmd &> /dev/null; then
            print_error "$cmd is not installed. Please install it first."
            exit 1
        fi
    done
    
    # Check required files
    if [ ! -f "microservices-k8s.yaml" ]; then
        print_error "microservices-k8s.yaml not found!"
        exit 1
    fi
    
    # Check Dockerfiles
    services=("auth-service" "customer-service" "order-service" "product-service")
    for service in "${services[@]}"; do
        if [ ! -f "${service}/Dockerfile" ]; then
            print_error "Dockerfile not found for ${service}"
            exit 1
        fi
    done
    
    print_status "All prerequisites are installed ✓"
}

# Build Docker images (but don't load yet)
build_images() {
    print_header "Building Docker Images"
    
    services=("auth-service" "customer-service" "order-service" "product-service")
    
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
    
    if kind get clusters | grep -q "microservices"; then
        print_warning "Deleting existing cluster 'microservices'..."
        kind delete cluster --name microservices
    fi

    print_status "Creating Kind configuration..."
    cat > kind-config.yaml << EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 30000
    hostPort: 9000
    protocol: TCP
  - containerPort: 30001
    hostPort: 9001
    protocol: TCP
  - containerPort: 30002
    hostPort: 9002
    protocol: TCP
  - containerPort: 30003
    hostPort: 9003
    protocol: TCP
  - containerPort: 30080
    hostPort: 9080
    protocol: TCP
  - containerPort: 15672
    hostPort: 15672
    protocol: TCP
EOF

    print_status "Creating Kind cluster 'microservices'..."
    if ! kind create cluster --name microservices --config kind-config.yaml; then
        print_error "Failed to create Kind cluster"
        rm -f kind-config.yaml
        exit 1
    fi

    rm -f kind-config.yaml
    
    print_status "Waiting for cluster to be ready..."
    kubectl wait --for=condition=Ready nodes --all --timeout=300s
    
    print_status "Kind cluster created successfully ✓"
}

# Load images into Kind cluster
load_images() {
    print_header "Loading Images into Kind Cluster"
    
    services=("auth-service" "customer-service" "order-service" "product-service")
    
    for service in "${services[@]}"; do
        print_status "Loading ${service} into Kind..."
        kind load docker-image ${service}:latest --name microservices || {
            print_error "Failed to load ${service} image"
            exit 1
        }
    done
    
    print_status "All images loaded successfully ✓"
}

# Deploy services to Kubernetes
deploy_services() {
    print_header "Deploying Services to Kubernetes"
    
    print_status "Applying Kubernetes manifests..."
    if ! kubectl apply -f microservices-k8s.yaml; then
        print_error "Failed to apply Kubernetes manifests"
        exit 1
    fi
    
    print_status "Services deployed successfully ✓"
}

# Wait for pods to be ready
wait_for_pods() {
    print_header "Waiting for Pods to be Ready"
    
    print_status "Waiting for namespace to be created..."
    sleep 10
    
    print_status "Waiting for databases to be ready..."
    kubectl wait --for=condition=Ready pod -l app=auth-db -n microservices --timeout=300s || {
        print_warning "auth-db not ready, continuing..."
    }
    kubectl wait --for=condition=Ready pod -l app=customer-db -n microservices --timeout=300s || {
        print_warning "customer-db not ready, continuing..."
    }
    kubectl wait --for=condition=Ready pod -l app=order-db -n microservices --timeout=300s || {
        print_warning "order-db not ready, continuing..."
    }
    kubectl wait --for=condition=Ready pod -l app=product-db -n microservices --timeout=300s || {
        print_warning "product-db not ready, continuing..."
    }
    kubectl wait --for=condition=Ready pod -l app=keycloak-postgres -n microservices --timeout=300s || {
        print_warning "keycloak-postgres not ready, continuing..."
    }
    
    print_status "Waiting for supporting services..."
    kubectl wait --for=condition=Ready pod -l app=rabbitmq -n microservices --timeout=300s || {
        print_warning "rabbitmq not ready, continuing..."
    }
    kubectl wait --for=condition=Ready pod -l app=redis -n microservices --timeout=300s || {
        print_warning "redis not ready, continuing..."
    }
    
    print_status "Waiting for Keycloak..."
    kubectl wait --for=condition=Ready pod -l app=keycloak -n microservices --timeout=600s || {
        print_warning "keycloak not ready, continuing..."
    }
    
    print_status "Waiting for Django services..."
    kubectl wait --for=condition=Ready pod -l app=auth-service -n microservices --timeout=300s || {
        print_warning "auth-service not ready, continuing..."
    }
    kubectl wait --for=condition=Ready pod -l app=customer-service -n microservices --timeout=300s || {
        print_warning "customer-service not ready, continuing..."
    }
    kubectl wait --for=condition=Ready pod -l app=order-service -n microservices --timeout=300s || {
        print_warning "order-service not ready, continuing..."
    }
    kubectl wait --for=condition=Ready pod -l app=product-service -n microservices --timeout=300s || {
        print_warning "product-service not ready, continuing..."
    }
    
    print_status "Pod deployment phase completed ✓"
}

# Run Django migrations
run_migrations() {
    print_header "Running Django Migrations"
    
    services=("auth-service" "customer-service" "order-service" "product-service")
    
    for service in "${services[@]}"; do
        print_status "Running migrations for ${service}..."
        kubectl exec -n microservices deployment/${service} -- python manage.py migrate --noinput || {
            print_warning "Migrations failed for ${service} (this might be expected if migrations don't exist)"
        }
        
        print_status "Collecting static files for ${service}..."
        kubectl exec -n microservices deployment/${service} -- python manage.py collectstatic --noinput || {
            print_warning "Static files collection failed for ${service}"
        }
    done
    
    print_status "Migrations completed ✓"
}

# Show deployment status
show_status() {
    print_header "Deployment Status"
    
    print_status "Cluster Info:"
    kubectl cluster-info --context kind-microservices
    
    echo ""
    print_status "Pods:"
    kubectl get pods -n microservices -o wide
    
    echo ""
    print_status "Services:"
    kubectl get services -n microservices
    
    echo ""
    print_status "Access URLs:"
    echo "Auth Service: http://localhost:9000"
    echo "Customer Service: http://localhost:9001"
    echo "Order Service: http://localhost:9002"
    echo "Product Service: http://localhost:9003"
    echo "Keycloak: http://localhost:9080"
    echo "RabbitMQ Management: http://localhost:15672"
    
    echo ""
    print_status "Useful Commands:"
    echo "Check pod status: kubectl get pods -n microservices"
    echo "Check logs: kubectl logs -n microservices deployment/<service-name>"
    echo "Port forward: kubectl port-forward -n microservices svc/<service-name> <local-port>:<service-port>"
}

# Main execution
main() {
    print_header "Django Microservices Kind Deployment"
    
    check_prerequisites
    build_images          # Build images first
    create_cluster        # Create cluster second
    load_images          # Load images third
    deploy_services      # Deploy to cluster fourth
    wait_for_pods        # Wait for pods to be ready
    run_migrations       # Run Django migrations
    show_status          # Show final status
    
    print_header "Deployment Complete!"
    print_status "Your Django microservices are now running on Kind ✓"
}

# Handle script arguments
case "${1:-}" in
    "clean")
        print_header "Cleaning Up"
        kubectl delete namespace microservices --ignore-not-found=true
        kind delete cluster --name microservices --quiet
        docker system prune -f
        print_status "Cleanup complete ✓"
        ;;
    "status")
        show_status
        ;;
    "logs")
        if [ -z "${2:-}" ]; then
            print_error "Please specify a service name: $0 logs <service-name>"
            echo "Available services: auth-service, customer-service, order-service, product-service"
            exit 1
        fi
        kubectl logs -n microservices deployment/$2 -f
        ;;
    "rebuild")
        print_header "Rebuilding Images"
        build_images
        load_images
        print_status "Images rebuilt and loaded ✓"
        ;;
    *)
        main
        ;;
esac