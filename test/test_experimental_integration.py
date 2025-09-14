#!/usr/bin/env python3
"""
Test script for the experimental ParticlePhysics MCP integration.

This script tests the basic functionality of the new experimental MCP server
and its integration with the agent search functions.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the project root to Python path (one level up since we're in test/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_experimental_mcp():
    """Test the experimental MCP client functionality."""
    try:
        logger.info("Testing experimental ParticlePhysics MCP client...")
        
        # Import the experimental MCP client
        from experimental.particlephysics_mcp import (
            search_particle_experimental,
            list_decays_experimental
        )
        
        logger.info("✓ Successfully imported experimental MCP functions")
        
        # Test particle search
        logger.info("Testing particle search for 'electron'...")
        result = await search_particle_experimental("electron")
        logger.info(f"Search result: {result}")
        
        # Test decay listing
        logger.info("Testing decay listing for 'muon'...")
        decay_result = await list_decays_experimental("muon")
        logger.info(f"Decay result: {decay_result}")
        
        logger.info("✓ Basic experimental MCP tests completed")
        
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Test error: {e}")
        return False
    
    return True

async def test_agent_search_integration():
    """Test the agent search integration functionality."""
    try:
        logger.info("Testing agent search integration...")
        
        # Import the integration functions with absolute imports
        import feynmancraft_adk.integrations
        from feynmancraft_adk.integrations import (
            enhanced_agent_search_with_particle_info,
            quick_particle_validation_for_agent,
            get_diagram_relevant_particle_info
        )
        
        logger.info("✓ Successfully imported integration functions")
        
        # Test enhanced search
        logger.info("Testing enhanced agent search...")
        result = await enhanced_agent_search_with_particle_info(
            "electron-positron annihilation",
            ["electron", "positron", "photon"]
        )
        logger.info(f"Enhanced search result keys: {list(result.keys())}")
        
        # Test quick validation
        logger.info("Testing quick particle validation...")
        validation_result = await quick_particle_validation_for_agent(["electron", "muon"])
        logger.info(f"Validation result: {validation_result.get('status', 'unknown')}")
        
        # Test diagram info
        logger.info("Testing diagram particle info...")
        diagram_info = await get_diagram_relevant_particle_info(["electron", "photon"])
        logger.info(f"Diagram info keys: {list(diagram_info.keys())}")
        
        logger.info("✓ Agent search integration tests completed")
        
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Test error: {e}")
        return False
    
    return True

async def main():
    """Main test function."""
    logger.info("Starting experimental MCP integration tests...")
    
    success = True
    
    # Test experimental MCP
    if not await test_experimental_mcp():
        success = False
    
    # Test agent search integration
    if not await test_agent_search_integration():
        success = False
    
    if success:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
