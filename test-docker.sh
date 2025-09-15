#!/bin/bash
set -e

echo "🧪 Testing FeynmanCraft ADK Docker Build..."

# Stop any running services first
echo "🛑 Stopping any running services..."
./stop.sh 2>/dev/null || true
docker-compose down 2>/dev/null || true

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create .env with GOOGLE_API_KEY"
    exit 1
fi

# Build Docker image
echo "🏗️ Building Docker image..."
docker build -t feynmancraft-adk:test .

# Test Docker run
echo "🚀 Testing Docker container..."
docker run -d \
    --name feynmancraft-test \
    -p 8080:8080 \
    -p 8000:8000 \
    -p 5173:5173 \
    -p 9229:9229 \
    --env-file .env \
    -v $(pwd)/logs:/app/logs \
    feynmancraft-adk:test

echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend (port 8000): OK"
else
    echo "❌ Backend (port 8000): Failed"
fi

# Check frontend
if curl -f http://localhost:5173/ > /dev/null 2>&1; then
    echo "✅ Frontend (port 5173): OK"
else
    echo "❌ Frontend (port 5173): Failed"
fi

# Check main port
if curl -f http://localhost:8080/ > /dev/null 2>&1; then
    echo "✅ Main port (8080): OK"
else
    echo "❌ Main port (8080): Failed"
fi

# Show logs
echo "📋 Container logs:"
docker logs feynmancraft-test --tail 20

# Show running processes
echo "📊 Running processes:"
docker exec feynmancraft-test ps aux

echo ""
echo "🌐 Test URLs:"
echo "Frontend: http://localhost:5173/"
echo "Backend: http://localhost:8000/"
echo "Main: http://localhost:8080/"
echo ""
echo "To view logs: docker logs -f feynmancraft-test"
echo "To stop test: docker stop feynmancraft-test && docker rm feynmancraft-test"
echo ""
echo "🧪 Docker test completed!"