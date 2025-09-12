#!/bin/bash

# Google Cloud Run Deployment Script for FeynmanCraft ADK
# This script handles the complete deployment process including LaTeX environment setup

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"feynmancraft-adk"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
MEMORY=${MEMORY:-"4Gi"}
CPU=${CPU:-"2"}
MAX_INSTANCES=${MAX_INSTANCES:-"10"}
TIMEOUT=${TIMEOUT:-"900"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 > /dev/null; then
        log_error "Not authenticated with gcloud. Please run: gcloud auth login"
        exit 1
    fi
    
    # Check if project ID is set
    if [ "$PROJECT_ID" = "your-project-id" ]; then
        log_error "Please set PROJECT_ID environment variable or update the script"
        log_info "Example: export PROJECT_ID=your-actual-project-id"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required Google Cloud APIs..."
    
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        containerregistry.googleapis.com \
        --project=$PROJECT_ID \
        --quiet
    
    log_info "APIs enabled successfully"
}

# Build and push Docker image
build_image() {
    log_info "Building Docker image with LaTeX environment..."
    log_warn "This may take 10-15 minutes due to LaTeX installation"
    
    # Build image with Cloud Build for better performance
    gcloud builds submit \
        --tag $IMAGE_NAME \
        --project=$PROJECT_ID \
        --timeout=1800s \
        --machine-type=e2-highcpu-8
    
    log_info "Docker image built and pushed successfully"
}

# Deploy to Cloud Run
deploy_service() {
    log_info "Deploying to Cloud Run..."
    
    gcloud run deploy $SERVICE_NAME \
        --image=$IMAGE_NAME \
        --region=$REGION \
        --project=$PROJECT_ID \
        --platform=managed \
        --allow-unauthenticated \
        --memory=$MEMORY \
        --cpu=$CPU \
        --timeout=$TIMEOUT \
        --concurrency=10 \
        --max-instances=$MAX_INSTANCES \
        --set-env-vars="FEYNMANCRAFT_ADK_LOG_LEVEL=INFO,KB_MODE=local,LATEX_COMPILE_ENGINE=lualatex,LATEX_OUTPUT_FORMATS=pdf,svg,png" \
        --labels="app=feynmancraft-adk,version=0.3.4,environment=production" \
        --quiet
    
    log_info "Service deployed successfully"
}

# Get service URL
get_service_url() {
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.url)")
    
    log_info "Service URL: $SERVICE_URL"
    echo ""
    echo "=================================================="
    echo "Deployment Summary:"
    echo "=================================================="
    echo "Project ID: $PROJECT_ID"
    echo "Service Name: $SERVICE_NAME"
    echo "Region: $REGION"
    echo "Service URL: $SERVICE_URL"
    echo "Memory: $MEMORY"
    echo "CPU: $CPU"
    echo "Max Instances: $MAX_INSTANCES"
    echo "=================================================="
    echo ""
    log_info "You can test the service with:"
    echo "curl $SERVICE_URL/health"
    echo ""
    log_info "To view logs:"
    echo "gcloud logs read --project=$PROJECT_ID --service=$SERVICE_NAME --limit=50"
}

# Test deployment
test_deployment() {
    log_info "Testing deployment..."
    
    # Wait for service to be ready
    sleep 30
    
    # Test health endpoint
    if curl -f -s "$SERVICE_URL/health" > /dev/null; then
        log_info "Health check passed"
    else
        log_warn "Health check failed, but service may still be starting"
    fi
    
    # Test basic functionality
    log_info "Testing LaTeX compilation..."
    
    TEST_PAYLOAD='{
        "query": "Generate a simple electron-positron annihilation diagram"
    }'
    
    if curl -X POST -H "Content-Type: application/json" -d "$TEST_PAYLOAD" "$SERVICE_URL/run" -s > /dev/null; then
        log_info "Basic functionality test passed"
    else
        log_warn "Basic functionality test failed, check logs for details"
    fi
}

# Cleanup function
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "Deployment failed!"
        log_info "To debug, check the build logs:"
        echo "gcloud builds log --project=$PROJECT_ID"
        log_info "To check service logs:"
        echo "gcloud logs read --project=$PROJECT_ID --service=$SERVICE_NAME --limit=50"
    fi
}

# Main execution
main() {
    echo "========================================"
    echo "FeynmanCraft ADK Cloud Run Deployment"
    echo "========================================"
    echo ""
    
    trap cleanup EXIT
    
    check_prerequisites
    enable_apis
    build_image
    deploy_service
    get_service_url
    test_deployment
    
    log_info "Deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Set your GOOGLE_API_KEY in the Cloud Run service environment variables"
    echo "2. Test the service with some Feynman diagram requests"
    echo "3. Monitor performance and adjust resources as needed"
    echo ""
    log_info "To update environment variables:"
    echo "gcloud run services update $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --set-env-vars=GOOGLE_API_KEY=your-key-here"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Environment variables:"
        echo "  PROJECT_ID      Google Cloud Project ID (required)"
        echo "  REGION          Cloud Run region (default: us-central1)"
        echo "  SERVICE_NAME    Service name (default: feynmancraft-adk)"
        echo "  MEMORY          Memory allocation (default: 4Gi)"
        echo "  CPU             CPU allocation (default: 2)"
        echo "  MAX_INSTANCES   Maximum instances (default: 10)"
        echo ""
        echo "Example:"
        echo "  PROJECT_ID=my-project ./deploy-cloudrun.sh"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac