# Particle Physics Agent

**Intelligent Multi-Agent TikZ Feynman Diagram Generation System** - Based on Google Agent Development Kit (ADK) v1.0.0

![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)
![License](https://img.shields.io/badge/license-MIT%2FApache--2.0-blue)
![ADK](https://img.shields.io/badge/ADK-1.0.0-green)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Status](https://img.shields.io/badge/status-Hackathon-orange)

## 🎯 Project Overview

Particle Physics Agent is an **autonomous learning intelligent research assistant** built on Google Agent Development Kit, capable of automatically generating high-quality TikZ Feynman diagram code from natural language descriptions. This hackathon project demonstrates innovative **multi-agent collaboration** with AI-powered physics validation.

### 🚀 Core Features

- 🤖 **6-Agent Collaboration System**: Specialized agents working together intelligently
- 📊 **Local Knowledge Base**: Vector search + keyword search hybrid retrieval
- 🔬 **Physics Validation**: AI-powered physics consistency checking
- 🌐 **Natural Language Processing**: Supports Chinese and English descriptions
- ⚡ **Smart AI Routing**: Automatic decision-making based on query complexity
- 📐 **TikZ Code Generation**: High-quality LaTeX Feynman diagram code

## 🏗️ System Architecture

### Intelligent Workflow

```
User Request → PlannerAgent → KBRetrieverAgent → PhysicsValidatorAgent
    ↓                              ↓                    ↓
Natural Language Parsing → Knowledge Base Search → AI Physics Validation
    ↓                              ↓                    ↓
DiagramGeneratorAgent → TikZValidatorAgent → FeedbackAgent
    ↓                              ↓                    ↓
TikZ Code Generation → AI Syntax Validation → Final Response Synthesis
```

**Key advantages of this AI-driven approach:**
- Pure prompt-based validation without external dependencies
- Intelligent physics consistency checking
- Streamlined deployment suitable for hackathon demonstrations

## 🤖 Agent System

### Core Agents (6)

1. **PlannerAgent** - Natural language parsing and task planning
2. **KBRetrieverAgent** - Local vector search and keyword retrieval
3. **PhysicsValidatorAgent** - MCP-enhanced physics correctness validation
4. **DiagramGeneratorAgent** - TikZ-Feynman code generation expert
5. **TikZValidatorAgent** - LaTeX compilation validation
6. **FeedbackAgent** - Result aggregation and user feedback

### MCP Tools Integration (20+ tools)

**PhysicsValidatorAgent** integrates the complete MCP particle physics toolkit:
- **Particle Search**: `search_particle_mcp` - Advanced particle database search
- **Property Retrieval**: `get_particle_properties_mcp` - Detailed particle properties
- **Quantum Number Validation**: `validate_quantum_numbers_mcp` - Advanced quantum number validation
- **Decay Analysis**: `get_branching_fractions_mcp` - Decay mode analysis
- **Particle Comparison**: `compare_particles_mcp` - Multi-particle property comparison
- **Unit Conversion**: `convert_units_mcp` - Intelligent physics unit conversion
- **Property Check**: `check_particle_properties_mcp` - Comprehensive property validation

## 🚀 Quick Start

### Requirements

- Python 3.9+
- Google ADK 1.0.0+
- Node.js 18+ (for frontend)
- Conda (recommended)
- Google AI API Key

### Local Development Setup

1. **Clone the project**
   ```bash
   git clone https://github.com/bee4come/Particle-Physics-Agent-test.git
   cd Particle-Physics-Agent-test
   ```

2. **Backend Setup**
   ```bash
   # Create Conda environment
   conda create --name fey python=3.11 -y
   conda activate fey
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   # Edit .env and set your GOOGLE_API_KEY
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

5. **Start the application**
   
   **Option A: Backend + Frontend (Recommended)**
   ```bash
   # Terminal 1: Start ADK backend
   conda activate fey
   adk web . --port 8000
   
   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```
   
   Access the application at `http://localhost:5173/app/` (or the port shown in terminal)
   
   **Option B: Backend Only**
   ```bash
   conda activate fey
   adk web . --port 8000
   ```
   
   Access the basic interface at `http://localhost:8000`

### Docker Deployment

1. **Build and run with Docker**
   ```bash
   # Build the image
   docker build -t feynmancraft-adk .
   
   # Run the container
   docker run -p 8000:8000 --env-file .env feynmancraft-adk
   ```

2. **Docker Compose (Full Stack)**
   ```bash
   # Start both backend and frontend
   docker-compose up -d
   ```
   
   Access at `http://localhost:3000`

### Usage Example

**Enter in the Web interface:**
```
Please generate a Feynman diagram for electron-positron annihilation producing two photons
```

**Or try these examples:**
- "Draw a Z boson decay to lepton pair diagram"
- "Generate Feynman diagram for electroweak penguin with gluonic dressing"
- "Show me a Higgs boson production via gluon fusion"

**System Workflow:**
1. 📋 **PlannerAgent** - Parse natural language and create execution plan
2. 📚 **KBRetrieverAgent** - Search relevant TikZ examples
3. 🔬 **PhysicsValidatorAgent** - Validate physics correctness using MCP tools
4. 🎨 **DiagramGeneratorAgent** - Generate TikZ code
5. ✅ **TikZValidatorAgent** - LaTeX compilation validation
6. 📝 **FeedbackAgent** - Synthesize final response

### Testing

```bash
# Run backend tests
pytest

# Test with example queries
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"query": "Generate Feynman diagram for electron-positron annihilation"}'
```

## 📊 Project Structure

```
Particle-Physics-Agent/
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── hooks/                  # Custom React hooks (ADK integration)
│   │   ├── AppFinal.tsx            # Main app component
│   │   └── main.tsx                # Entry point
│   ├── package.json                # Frontend dependencies
│   └── vite.config.ts              # Vite configuration with ADK proxy
├── feynmancraft_adk/           # Main package (ADK standard structure)
│   ├── __init__.py            # Model configuration and logging setup
│   ├── agent.py               # root_agent definition
│   ├── schemas.py             # Pydantic data models
│   ├── data/                  # Knowledge base data files
│   │   ├── feynman_kb.json        # Local knowledge base
│   │   ├── pprules.json           # Physics rules data
│   │   └── embeddings/            # Vector embedding cache
│   ├── sub_agents/            # 6 core agent implementations
│   │   ├── planner_agent.py           # Natural language parsing and planning
│   │   ├── kb_retriever_agent.py      # Knowledge base retrieval
│   │   ├── physics_validator_agent.py # MCP-enhanced physics validation
│   │   ├── diagram_generator_agent.py # TikZ code generation
│   │   ├── tikz_validator_agent.py    # LaTeX compilation validation
│   │   └── feedback_agent.py          # Result aggregation and feedback
│   ├── shared_libraries/       # Shared utility libraries
│   │   ├── config.py              # Environment configuration
│   │   ├── prompt_utils.py        # Prompt utilities
│   │   └── physics/               # Physics data and tools
│   ├── integrations/           # External service integrations
│   │   └── mcp/                   # MCP tools integration
│   │       ├── mcp_client.py          # MCP client
│   │       ├── mcp_config.json        # MCP configuration
│   │       └── particle_name_mappings.py # Particle name mappings
│   ├── tools/                 # Tool functions
│   │   ├── kb/                    # Knowledge base tools
│   │   │   ├── bigquery.py            # BigQuery integration (unused)
│   │   │   ├── local.py               # Local vector search
│   │   │   ├── search.py              # Unified search interface
│   │   │   ├── data_loader.py         # Data loader
│   │   │   └── embedding_manager.py   # Embedding manager
│   │   ├── physics/               # Physics tools
│   │   │   ├── physics_tools.py       # MCP physics tools
│   │   │   ├── search.py              # Physics rules search
│   │   │   ├── data_loader.py         # Physics data loader
│   │   │   └── embedding_manager.py   # Physics embedding manager
│   │   ├── integrations/          # Integration tool interfaces (directly uses ../integrations/mcp)
│   │   └── latex_compiler.py      # LaTeX compiler
│   ├── docs/                  # Project documentation
│   │   ├── AGENT_TREE.md          # Agent architecture documentation
│   │   └── bigquery_setup.md      # BigQuery setup guide (unused)
│   └── scripts/               # Deployment and management scripts
│       ├── build_local_index.py   # Build local index
│       ├── upload_to_bigquery.py  # Upload to BigQuery (unused)
│       └── release.py             # Release script
├── requirements.txt           # Python dependencies
├── scripts/                   # Build and deployment scripts
│   └── build-and-test.sh         # Docker build and test pipeline
├── docker-compose.yml         # Docker orchestration configuration
├── Dockerfile                 # Docker image build
├── env.template               # Environment variable template
├── QUICKSTART.md             # Quick start guide
├── DEVELOPMENTplan.md        # Development plan
├── CHANGELOG.md              # Change log
├── VERSION                   # Version information
└── README.md                 # This document
```

## 🛠️ Tech Stack

### Core Frameworks
- **Google ADK 1.0.0** - Multi-agent orchestration framework
- **Google Gemini** - Language model (gemini-2.0-flash)
- **MCP (Model Context Protocol)** - Enhanced tool communication protocol
- **Pydantic** - Data validation and serialization

### Frontend Stack
- **React 19** - UI framework with modern hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool with ADK proxy configuration
- **TailwindCSS** - Utility-first CSS framework
- **Lucide React** - Icon library

### Professional Tools
- **TikZ-Feynman** - Feynman diagram drawing
- **LaTeX** - Document compilation
- **MCP Particle Physics Tools** - 20+ professional particle physics tools
- **Annoy** - Local vector similarity search
- **Vertex AI** - Vector embedding generation

### Development Tools
- **Conda** - Environment management
- **pytest** - Testing framework

## 🚀 Deployment Options

### Development Mode
- **Backend**: ADK web server on port 8000
- **Frontend**: Vite dev server with hot reload
- **Best for**: Local development and testing

### Production Docker
- **Single Container**: Backend-only deployment
- **Docker Compose**: Full-stack with nginx proxy
- **Best for**: Cloud deployment and production

### Cloud Deployment
- **Google Cloud Run**: Serverless container deployment
- **AWS ECS**: Container orchestration
- **Azure Container Instances**: Managed containers
- **Best for**: Scalable production workloads

## 🎯 Project Status

This hackathon project demonstrates:
- ✅ Multi-agent AI collaboration using Google ADK
- ✅ Modern React frontend with real-time workflow visualization
- ✅ Intelligent physics validation with prompt-based techniques  
- ✅ Natural language to TikZ diagram generation
- ✅ Local knowledge base with vector search
- ✅ Streamlined deployment without external dependencies

## 🏆 Key Features

### AI-Powered Validation System 🔬
1. **Prompt-Based Validation**: Pure AI-driven physics and syntax validation
2. **Local Knowledge Base**: Fast vector search with 150+ physics examples
3. **Smart Error Detection**: Intelligent syntax and physics consistency checking
4. **Educational Output**: Provides clear explanations and suggestions

### Multi-Agent Architecture
1. **Intelligent Collaboration**: Six specialized agents working together
2. **Natural Language Processing**: Supports both Chinese and English
3. **Quality Assurance**: Multiple validation layers ensure accuracy
4. **Streamlined Workflow**: Optimized for hackathon demonstration

## 📄 License

This project is dual-licensed under MIT License and Apache License 2.0.

Please see the [LICENSE](LICENSE) file for details. You may choose either license when using this project.

## 🙏 Acknowledgments

- **Google ADK Team** - For providing the powerful multi-agent development framework
- **TikZ-Feynman Community** - For the excellent Feynman diagram drawing tools
- **Particle Data Group** - For authoritative particle physics data
- **Open Source Community** - For countless excellent open source tools and libraries

## 📞 Contact

- **Project Homepage**: [GitHub Repository](https://github.com/bee4come/Particle-Physics-Agent-test)
- **Issue Tracker**: [GitHub Issues](https://github.com/bee4come/Particle-Physics-Agent-test/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bee4come/Particle-Physics-Agent-test/discussions)

---

**FeynmanCraft ADK - Making Physics Diagram Generation Intelligent and Simple** 🚀 