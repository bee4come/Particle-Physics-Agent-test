# FeynmanCraft ADK Cloud Run Dockerfile
# Full-stack deployment with frontend and backend
FROM node:18-slim AS frontend-builder

# Install frontend dependencies and build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
RUN npm run build

# Main Python image with LaTeX support
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies, Node.js and LaTeX environment
RUN apt-get update && apt-get install -y \
    # Build tools
    build-essential \
    gcc \
    g++ \
    git \
    curl \
    wget \
    # Node.js for frontend serving
    nodejs \
    npm \
    # LaTeX and TikZ-Feynman dependencies
    texlive-latex-base \
    texlive-latex-extra \
    texlive-pictures \
    texlive-science \
    texlive-luatex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    # Conversion tools for multi-format output
    pdf2svg \
    poppler-utils \
    ghostscript \
    imagemagick \
    # Debug and monitoring tools
    htop \
    nano \
    less \
    procps \
    net-tools \
    lsof \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configure ImageMagick security policy for PDF processing
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml

# Verify LaTeX installation
RUN lualatex --version && \
    pdflatex --version && \
    pdf2svg --version && \
    pdftoppm -h

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the agent code and data
COPY feynmancraft_adk/ ./feynmancraft_adk/
COPY frontend/ ./frontend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy environment and scripts
COPY .env ./
COPY start.sh ./
COPY stop.sh ./
COPY status.sh ./

# Make scripts executable
RUN chmod +x start.sh stop.sh status.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Cloud Run specific environment variables
ENV FEYNMANCRAFT_ADK_LOG_LEVEL=DEBUG
ENV KB_MODE=local
ENV DEFAULT_SEARCH_K=5

# LaTeX compilation settings
ENV LATEX_COMPILE_ENGINE=lualatex
ENV LATEX_COMPILE_TIMEOUT=30
ENV LATEX_OUTPUT_FORMATS=pdf,svg,png

# Port configuration for Cloud Run
ENV PORT=8080
ENV BACKEND_PORT=8000
ENV FRONTEND_PORT=5173
ENV HOST=0.0.0.0

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Create temp directories for LaTeX compilation
RUN mkdir -p /tmp/latex_compiler && \
    chmod 755 /tmp/latex_compiler

# Create logs directory
RUN mkdir -p /app/logs

# Expose all ports for debugging and services
EXPOSE 8080 8000 5173 3000 9229

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${BACKEND_PORT}/health || curl -f http://localhost:${FRONTEND_PORT}/ || exit 1

# Create startup script for full-stack deployment
COPY <<EOF /app/cloud-run-start.sh
#!/bin/bash
set -e

echo "🚀 Starting FeynmanCraft Full-Stack Deployment..."

# Install frontend dependencies if needed
cd /app/frontend
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm ci
fi

# Build frontend if dist doesn't exist
if [ ! -d "dist" ]; then
    echo "🏗️ Building frontend..."
    npm run build
fi

# Start frontend server in background
echo "🌐 Starting frontend server on port \${FRONTEND_PORT}..."
nohup npm run preview -- --host 0.0.0.0 --port \${FRONTEND_PORT} > /app/logs/frontend.log 2>&1 &
FRONTEND_PID=\$!
echo "Frontend PID: \$FRONTEND_PID"

# Wait for frontend to start
sleep 5

# Start backend server
echo "⚙️ Starting ADK backend server on port \${BACKEND_PORT}..."
cd /app
export PORT=\${BACKEND_PORT}
adk web --port=\${BACKEND_PORT} --host=\${HOST} /app
EOF

RUN chmod +x /app/cloud-run-start.sh

# Run the full-stack application
CMD ["/app/cloud-run-start.sh"]