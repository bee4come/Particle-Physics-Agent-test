# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent AI system for generating TikZ Feynman diagrams from natural language descriptions. It uses Google Agent Development Kit (ADK) v1.0.0 with 7 specialized agents collaborating to parse requests, validate physics, and generate LaTeX code.

## Common Development Commands

### Environment Setup
```bash
# Create and activate conda environment
conda create --name fey python=3.11 -y
conda activate fey

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY
```

### Running the Application
```bash
# Start ADK Web UI (main entry point)
adk web . --port 8000

# Docker deployment
docker build -t feynmancraft-adk .
docker run -p 8000:8000 --env-file .env feynmancraft-adk
```

### Testing
```bash
# Run tests (pytest configured)
pytest

# Test with example queries once running:
# - "Generate Feynman diagram for electron-positron annihilation"
# - "Draw a Z boson decay to lepton pair diagram"
```

## Architecture

### Multi-Agent System Structure
The system orchestrates 7 specialized agents in `/feynmancraft_adk/sub_agents/`:

1. **PlannerAgent** (`planner_agent.py`) - Parses natural language, extracts particles/interactions
2. **KBRetrieverAgent** (`kb_retriever_agent.py`) - Searches local knowledge base using vector similarity
3. **PhysicsValidatorAgent** (`physics_validator_agent.py`) - Validates physics using MCP tools
4. **DiagramGeneratorAgent** (`diagram_generator_agent.py`) - Generates TikZ-Feynman LaTeX code
5. **TikZValidatorAgent** (`tikz_validator_agent.py`) - Compiles and validates LaTeX
6. **DeepResearchAgent** (`deep_research_agent.py`) - Performs advanced research using Google Search API
7. **FeedbackAgent** (`feedback_agent.py`) - Aggregates results and synthesizes responses

### Key Components
- **Root Agent**: `/feynmancraft_adk/agent.py` - Orchestrates sub-agents
- **Knowledge Base**: `/feynmancraft_adk/data/feynman_kb.json` - 150+ physics examples
- **Physics Rules**: `/feynmancraft_adk/data/pprules.json` - Particle physics constraints
- **MCP Integration**: `/feynmancraft_adk/integrations/mcp/` - 20+ physics validation tools
- **LaTeX MCP Client**: `/feynmancraft_adk/integrations/mcp/latex_mcp_client.py` - Remote LaTeX compilation
- **Tools**: `/feynmancraft_adk/tools/` - KB search, physics validation, LaTeX compilation
- **LaTeX Compiler**: `/feynmancraft_adk/tools/latex_compiler.py` - Local TikZ compilation with multi-format support

### Technology Stack
- **Framework**: Google ADK 1.0.0 for multi-agent orchestration
- **LLMs**: Gemini 2.5 Flash (most agents) and 2.5 Pro (complex reasoning tasks)
- **Vector Search**: Annoy for local knowledge base similarity search
- **Validation**: Pydantic for data models, MCP for physics rules
- **LaTeX Compilation**: Local compiler with pdflatex/lualatex support, multi-format output (PDF/SVG/PNG)
- **Web Framework**: ADK's built-in web interface with React 19 frontend

### Agent Communication Flow
1. User submits natural language request
2. PlannerAgent extracts physics entities
3. KBRetrieverAgent finds similar examples
4. PhysicsValidatorAgent checks physics validity
5. DeepResearchAgent performs advanced research if needed
6. DiagramGeneratorAgent creates TikZ code
7. TikZValidatorAgent compiles LaTeX
8. FeedbackAgent returns final result with diagram

### Configuration Notes
- Complex reasoning agents use `gemini-2.5-pro` for advanced tasks
- Most agents use `gemini-2.5-flash` for cost efficiency
- Only research query model uses `gemini-2.0-flash`
- Knowledge base is local-only (no BigQuery)
- Default search returns top 5 results (`DEFAULT_SEARCH_K=5`)
- Logging controlled via `FEYNMANCRAFT_ADK_LOG_LEVEL`

### Development Tips
- Agent logic is in `/feynmancraft_adk/sub_agents/`
- Add new physics examples to `/feynmancraft_adk/data/feynman_kb.json`
- MCP tools are defined in `/feynmancraft_adk/integrations/mcp/`
- LaTeX compilation supports both local and remote MCP modes
- The system supports continuous conversation for multiple diagrams
- Frontend uses AppFixed.tsx as main entry point
- Use start.sh/stop.sh scripts for one-click deployment
- Focus on prompt engineering rather than external physics libraries

### LaTeX Compilation Environment
The system supports dual compilation modes:
- **Local Mode**: Direct LaTeX compilation via `latex_compiler.py` with multi-format output
- **MCP Mode**: Remote compilation via LaTeX MCP server for distributed deployment
- **Requirements**: pdflatex, lualatex, tikz-feynman package, conversion tools (pdf2svg, pdftoppm)

## Current Work Progress (2025-06-27)
- Frontend integrated from gemini-fullstack-langgraph-quickstart  
- Fixed styling and connection issues
- Implemented logging system with LogPanelFixed component
- Fixed deep research agent Google Search API issues
- Optimized model configuration for cost efficiency (gemini-2.0-flash for most agents)
- **FIXED**: Agent transfer mechanism - deep_research_agent now properly transfers back to root_agent
  - Added explicit transfer instructions to `deep_research_agent_prompt.py`
  - Added status reporting requirement for better workflow visibility
  - Ensured proper state management with `state.deep_research_results`
- Issues resolved:
  - ✅ Agent transfer mechanism stuck after deep_research_agent completes
  - ✅ System not progressing from deep_research to diagram_generator_agent
  - ✅ Root_agent orchestration logic debugged and confirmed working
- Last commit: Fix agent transfer mechanism for deep research workflow