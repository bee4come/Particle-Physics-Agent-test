# FeynmanCraft ADK Quick Start Guide

**AI-Powered Multi-Agent Feynman Diagram Generation with LaTeX Compilation**

## 🚀 3-Minute Hackathon Setup

### 1. Clone the Project
```bash
git clone <repository-url>
cd Particle-Physics-Agent
```

### 2. Environment Setup

#### Python Environment
```bash
# Create Conda environment
conda create --name fey python=3.11 -y
conda activate fey

# Install dependencies
pip install -r requirements.txt
```

#### LaTeX Environment (Required for Diagram Compilation)
```bash
# macOS (choose one):
brew install --cask mactex          # Full installation (~4GB)
brew install --cask basictex        # Minimal installation (~100MB)

# Ubuntu/Debian:
sudo apt install texlive-latex-base texlive-latex-extra texlive-pictures texlive-science texlive-luatex

# Install conversion tools:
# macOS:
brew install pdf2svg poppler ghostscript

# Ubuntu/Debian:
sudo apt install pdf2svg poppler-utils ghostscript
```

For detailed LaTeX setup instructions, see [LATEX_SETUP.md](LATEX_SETUP.md) or [INSTALL_LATEX_MACOS.md](INSTALL_LATEX_MACOS.md).

### 3. Configure API Key
```bash
# Copy example configuration
cp .env.example .env

# Edit .env file and set:
# GOOGLE_API_KEY=your-api-key-here
```

### 4. Run the System

#### Option A: One-Click Launch (Recommended)
```bash
# Start all services with management scripts
./start.sh

# Visit http://localhost:5173 for full frontend
# Visit http://localhost:8000 for basic interface
```

#### Option B: Manual Launch
```bash
# Start ADK Web UI only
adk web . --port 8000

# Or start both backend and frontend:
# Terminal 1: Backend
adk web . --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

### 5. Test Examples

Enter in ADK Web UI:
- "Generate Feynman diagram for electron-positron annihilation"
- "Draw a Z boson decay to lepton pair diagram"
- "Show Compton scattering process"
- "muon decay diagram"

## 🔧 Quick Troubleshooting

### Common Issues
- **adk command not found**: Run `pip install google-adk`
- **API authentication failed**: Check your GOOGLE_API_KEY in .env file
- **Port conflict**: Try different port with `--port 8001`

That's it! The system should now be running and ready for demonstration.

## 🎯 What You Get

### Seven-Agent AI System
1. **PlannerAgent**: Natural language parsing
2. **KBRetrieverAgent**: Knowledge base search
3. **PhysicsValidatorAgent**: AI physics validation
4. **DeepResearchAgent**: Advanced research using Google Search API
5. **DiagramGeneratorAgent**: TikZ code generation
6. **TikZValidatorAgent**: LaTeX compilation with PDF/SVG/PNG output
7. **FeedbackAgent**: Response synthesis

### Features
- Multi-format output (PDF, SVG, PNG)
- Local and remote LaTeX compilation
- MCP integration for physics validation
- React 19 frontend with real-time updates
- One-click deployment scripts

## 🚀 Google Cloud Run Deployment

For production deployment:

```bash
# Set your Google Cloud project
export PROJECT_ID=your-project-id

# Deploy with LaTeX environment
./deploy-cloudrun.sh
```

Perfect for demonstrations and production use! 🚀