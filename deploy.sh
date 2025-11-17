#!/bin/bash
# NexTrade Deployment Script
# Automated deployment script for various environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="NexTrade Multi-Agent Trading System"
VERSION="1.0.0"
DOCKER_IMAGE="nextrade:latest"

# Functions
print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing_deps=0
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        missing_deps=1
    else
        print_success "Docker found: $(docker --version)"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose is not installed (optional)"
    else
        print_success "Docker Compose found: $(docker-compose --version)"
    fi
    
    # Check .env file
    if [ ! -f .env ]; then
        print_error ".env file not found. Copy .env.example to .env and configure it."
        missing_deps=1
    else
        print_success ".env file found"
    fi
    
    if [ $missing_deps -eq 1 ]; then
        print_error "Missing prerequisites. Please install them and try again."
        exit 1
    fi
}

# Build Docker image
build_image() {
    print_header "Building Docker Image"
    
    docker build -t $DOCKER_IMAGE . || {
        print_error "Failed to build Docker image"
        exit 1
    }
    
    print_success "Docker image built successfully"
}

# Deploy with Docker Compose
deploy_docker_compose() {
    print_header "Deploying with Docker Compose"
    
    docker-compose down || true
    docker-compose up -d
    
    print_success "Application deployed with Docker Compose"
    print_success "API: http://localhost:8000"
    print_success "UI: http://localhost:8501"
    print_success "API Docs: http://localhost:8000/docs"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    print_header "Deploying to Kubernetes"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        exit 1
    fi
    
    # Apply configurations
    kubectl apply -f kubernetes.yaml
    
    print_success "Kubernetes resources created"
    
    # Wait for pods to be ready
    print_warning "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=nextrade -n nextrade --timeout=300s
    
    # Get service URLs
    print_success "Deployment complete!"
    echo "Run 'kubectl get services -n nextrade' to see service endpoints"
}

# Run locally without Docker
deploy_local() {
    print_header "Deploying Locally (Development Mode)"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check uv
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed. Install from: https://docs.astral.sh/uv/"
        exit 1
    fi
    
    # Install dependencies
    print_warning "Installing dependencies..."
    uv pip install -e .
    
    # Run verification
    python check_setup.py
    
    # Start application
    print_success "Starting Streamlit application..."
    streamlit run streamlit_app.py
}

# Health check
health_check() {
    print_header "Running Health Check"
    
    # Check API
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "API is healthy"
    else
        print_error "API is not responding"
    fi
    
    # Check UI
    if curl -f http://localhost:8501 &> /dev/null; then
        print_success "UI is healthy"
    else
        print_error "UI is not responding"
    fi
}

# View logs
view_logs() {
    print_header "Viewing Logs"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose logs -f
    else
        print_error "Docker Compose not available"
        exit 1
    fi
}

# Stop deployment
stop_deployment() {
    print_header "Stopping Deployment"
    
    if [ "$1" == "docker" ]; then
        docker-compose down
        print_success "Docker Compose deployment stopped"
    elif [ "$1" == "kubernetes" ]; then
        kubectl delete -f kubernetes.yaml
        print_success "Kubernetes deployment stopped"
    else
        print_error "Unknown deployment type: $1"
        exit 1
    fi
}

# Show usage
show_usage() {
    cat << EOF
$APP_NAME - Deployment Script v$VERSION

Usage: ./deploy.sh [COMMAND]

Commands:
    build               Build Docker image
    deploy-docker       Deploy using Docker Compose
    deploy-k8s          Deploy to Kubernetes
    deploy-local        Run locally without Docker
    health              Run health check
    logs                View application logs
    stop-docker         Stop Docker Compose deployment
    stop-k8s            Stop Kubernetes deployment
    help                Show this help message

Examples:
    ./deploy.sh build               # Build Docker image
    ./deploy.sh deploy-docker       # Deploy with Docker Compose
    ./deploy.sh deploy-local        # Run locally
    ./deploy.sh health              # Check application health
    ./deploy.sh logs                # View logs
    ./deploy.sh stop-docker         # Stop deployment

EOF
}

# Main execution
main() {
    case "$1" in
        build)
            check_prerequisites
            build_image
            ;;
        deploy-docker)
            check_prerequisites
            build_image
            deploy_docker_compose
            sleep 5
            health_check
            ;;
        deploy-k8s)
            check_prerequisites
            build_image
            deploy_kubernetes
            ;;
        deploy-local)
            deploy_local
            ;;
        health)
            health_check
            ;;
        logs)
            view_logs
            ;;
        stop-docker)
            stop_deployment docker
            ;;
        stop-k8s)
            stop_deployment kubernetes
            ;;
        help|--help|-h|"")
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
