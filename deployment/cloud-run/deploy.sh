#!/bin/bash
set -e

# FeynmanCraft ADK Cloud Run Deployment Script

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
SERVICE_NAME="feynmancraft-adk"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying FeynmanCraft ADK to Cloud Run..."
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create .env with GOOGLE_API_KEY"
    exit 1
fi

# Source environment variables
source .env

# Check if Google API key is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY not found in .env file"
    exit 1
fi

# Set current project
echo "📋 Setting up Google Cloud project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create secret for API key
echo "🔐 Creating secrets..."
echo -n "$GOOGLE_API_KEY" | gcloud secrets create feynmancraft-google-api-key --data-file=- --replication-policy="automatic" || true

# Grant Cloud Run access to secrets
echo "🔑 Setting up IAM permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" || true

# Build and push Docker image
echo "🏗️ Building Docker image..."
docker build -t $IMAGE_NAME .

echo "📤 Pushing image to Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 1 \
    --concurrency 100 \
    --timeout 300 \
    --port 8080 \
    --set-env-vars "PORT=8080,BACKEND_PORT=8000,FRONTEND_PORT=5173,HOST=0.0.0.0,FEYNMANCRAFT_ADK_LOG_LEVEL=INFO,KB_MODE=local,DEFAULT_SEARCH_K=5,LATEX_COMPILE_ENGINE=lualatex,LATEX_COMPILE_TIMEOUT=30,LATEX_OUTPUT_FORMATS=pdf,svg,png,NODE_ENV=production" \
    --set-secrets "GOOGLE_API_KEY=feynmancraft-google-api-key:latest"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "✅ Deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"
echo "🔧 Backend API: $SERVICE_URL"
echo "🎨 Frontend: $SERVICE_URL"
echo ""
echo "📊 To view logs:"
echo "gcloud run services logs read $SERVICE_NAME --platform managed --region $REGION"
echo ""
echo "🛠️ To update the service:"
echo "./deployment/cloud-run/deploy.sh"