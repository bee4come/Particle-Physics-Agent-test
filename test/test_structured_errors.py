#!/usr/bin/env python3
"""
Test script for structured error handling system
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path (one level up since we're in test/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from feynmancraft_adk.error_handler import (
    handle_mcp_error, 
    handle_tikz_error,
    handle_agent_error,
    handle_physics_error
)

logging.basicConfig(level=logging.INFO)

async def test_structured_errors():
    """Test all types of structured errors"""
    session_id = "test_session_123"
    trace_id = "test_trace_456"
    
    print("Testing MCP connection error...")
    mcp_error = handle_mcp_error(
        "Failed to connect to ParticlePhysics MCP Server",
        session_id=session_id,
        trace_id=trace_id,
        tool="search_particle_mcp"
    )
    print(f"Created MCP error: {mcp_error.id}")
    
    print("\nTesting TikZ compilation error...")
    tikz_error = handle_tikz_error(
        "LaTeX compilation failed with syntax errors",
        session_id=session_id,
        trace_id=trace_id,
        agent="DiagramGeneratorAgent"
    )
    print(f"Created TikZ error: {tikz_error.id}")
    
    print("\nTesting agent workflow error...")
    agent_error = handle_agent_error(
        "Agent transfer failed during workflow execution",
        session_id=session_id,
        agent="PlannerAgent",
        trace_id=trace_id
    )
    print(f"Created agent error: {agent_error.id}")
    
    print("\nTesting physics validation error...")
    physics_error = handle_physics_error(
        "Conservation of energy violated in proposed process",
        session_id=session_id,
        trace_id=trace_id
    )
    print(f"Created physics error: {physics_error.id}")
    
    print(f"\nAll errors have been emitted via SSE to session {session_id}")
    print("Check the frontend to see the structured error cards!")

if __name__ == "__main__":
    asyncio.run(test_structured_errors())