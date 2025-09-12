#!/bin/bash

# Local Docker Build Script for FeynmanCraft ADK
# Builds Docker image with Gemini API key for local testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Configuration
IMAGE_NAME="feynmancraft-adk:local"
CONTAINER_NAME="feynmancraft-adk-local"

# Function to check if API key is set
check_api_key() {
    if [ -z "$GOOGLE_API_KEY" ]; then
        log_error "GOOGLE_API_KEY environment variable is not set!"
        echo ""
        echo "Please set your Gemini API key:"
        echo "export GOOGLE_API_KEY='your-api-key-here'"
        echo ""
        echo "Or create a .env file based on .env.example:"
        echo "cp .env.example .env"
        echo "Then edit .env and set GOOGLE_API_KEY=your-api-key-here"
        exit 1
    fi
    
    log_info "API key found (${GOOGLE_API_KEY:0:8}...)"
}

# Function to load environment variables
load_env() {
    # Try to load from .env first, then .env.example
    if [ -f ".env" ]; then
        log_info "Loading environment from .env"
        export $(grep -v '^#' .env | xargs)
    elif [ -f ".env.example" ]; then
        log_info "Loading environment from .env.example"
        export $(grep -v '^#' .env.example | xargs)
    fi
}

# Function to clean up existing containers
cleanup_existing() {
    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        log_warn "Removing existing container: $CONTAINER_NAME"
        docker rm -f $CONTAINER_NAME 2>/dev/null || true
    fi
    
    # Remove existing image if requested
    if [ "$1" = "--clean" ]; then
        if [ "$(docker images -q $IMAGE_NAME)" ]; then
            log_warn "Removing existing image: $IMAGE_NAME"
            docker rmi -f $IMAGE_NAME 2>/dev/null || true
        fi
    fi
}

# Function to build Docker image
build_image() {
    log_info "Building Docker image with LaTeX support..."
    log_warn "This may take 10-15 minutes for the first build due to LaTeX installation"
    
    # Build with build arg for API key and proxy configuration
    docker build \
        -f Dockerfile.local \
        -t $IMAGE_NAME \
        --build-arg GOOGLE_API_KEY="$GOOGLE_API_KEY" \
        --build-arg http_proxy=http://host.docker.internal:7897 \
        --build-arg https_proxy=http://host.docker.internal:7897 \
        --build-arg HTTP_PROXY=http://host.docker.internal:7897 \
        --build-arg HTTPS_PROXY=http://host.docker.internal:7897 \
        . || {
        log_error "Docker build failed!"
        exit 1
    }
    
    log_info "Docker image built successfully: $IMAGE_NAME"
}

# Function to run container
run_container() {
    log_info "Starting container: $CONTAINER_NAME"
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    docker run -d \
        --name $CONTAINER_NAME \
        -p 8000:8000 \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/feynmancraft_adk/data:/app/feynmancraft_adk/data" \
        --restart unless-stopped \
        $IMAGE_NAME || {
        log_error "Failed to start container!"
        exit 1
    }
    
    log_info "Container started successfully"
}

# Function to test deployment
test_deployment() {
    log_info "Waiting for service to start..."
    sleep 10
    
    # Wait for health check
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            log_info "Health check passed!"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Health check failed after $max_attempts attempts"
            echo ""
            echo "Container logs:"
            docker logs $CONTAINER_NAME --tail=20
            return 1
        fi
        
        log_debug "Health check attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    # Test basic functionality
    log_info "Testing basic functionality..."
    
    local test_payload='{
        "query": "Generate a simple electron-positron annihilation diagram"
    }'
    
    if curl -X POST \
           -H "Content-Type: application/json" \
           -d "$test_payload" \
           -s \
           http://localhost:8000/run > /dev/null; then
        log_info "Basic functionality test passed!"
    else
        log_warn "Basic functionality test failed, but service may still work"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --clean        Remove existing image before building"
    echo "  --build-only   Only build the image, don't run container"
    echo "  --run-only     Only run container (assumes image exists)"
    echo "  --logs         Show container logs after starting"
    echo ""
    echo "Examples:"
    echo "  # Full build and run:"
    echo "  export GOOGLE_API_KEY='your-key' && $0"
    echo ""
    echo "  # Clean build:"
    echo "  $0 --clean"
    echo ""
    echo "  # Build only:"
    echo "  $0 --build-only"
    echo ""
    echo "Environment variables:"
    echo "  GOOGLE_API_KEY  Required Gemini API key"
}

# Function to show logs
show_logs() {
    log_info "Container logs (last 50 lines):"
    echo "=========================================="
    docker logs $CONTAINER_NAME --tail=50
    echo "=========================================="
    echo ""
    log_info "To follow logs in real-time:"
    echo "docker logs -f $CONTAINER_NAME"
}

# Main execution
main() {
    echo "========================================"
    echo "FeynmanCraft ADK Local Docker Build"
    echo "========================================"
    echo ""
    
    local build_only=false
    local run_only=false
    local show_logs_flag=false
    local clean_build=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_usage
                exit 0
                ;;
            --clean)
                clean_build=true
                shift
                ;;
            --build-only)
                build_only=true
                shift
                ;;
            --run-only)
                run_only=true
                shift
                ;;
            --logs)
                show_logs_flag=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Load environment variables
    load_env
    
    # Check API key
    check_api_key
    
    if [ "$run_only" != true ]; then
        # Clean up if requested
        if [ "$clean_build" = true ]; then
            cleanup_existing --clean
        else
            cleanup_existing
        fi
        
        # Build image
        build_image
    fi
    
    if [ "$build_only" != true ]; then
        # Run container
        run_container
        
        # Test deployment
        test_deployment
        
        echo ""
        echo "=========================================="
        echo "Deployment Summary"
        echo "=========================================="
        echo "Service URL: http://localhost:8000"
        echo "Health Check: http://localhost:8000/health"
        echo "Container Name: $CONTAINER_NAME"
        echo "Image Name: $IMAGE_NAME"
        echo "=========================================="
        echo ""
        
        log_info "You can now test the service!"
        echo ""
        echo "Example test commands:"
        echo "curl http://localhost:8000/health"
        echo "curl -X POST -H 'Content-Type: application/json' -d '{\"query\": \"electron positron annihilation\"}' http://localhost:8000/run"
        echo ""
        echo "Container management:"
        echo "docker logs -f $CONTAINER_NAME    # Follow logs"
        echo "docker stop $CONTAINER_NAME       # Stop container"
        echo "docker start $CONTAINER_NAME      # Start container"
        echo "docker rm -f $CONTAINER_NAME      # Remove container"
        
        if [ "$show_logs_flag" = true ]; then
            echo ""
            show_logs
        fi
    else
        log_info "Build completed. Image: $IMAGE_NAME"
        echo "To run the container:"
        echo "$0 --run-only"
    fi
}

# Handle script execution
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi