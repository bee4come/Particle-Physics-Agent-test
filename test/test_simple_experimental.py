#!/usr/bin/env python3
"""
Simple test script for the experimental ParticlePhysics MCP server.

This script tests the experimental MCP server functionality directly.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the experimental directory to Python path (go up to project root, then into experimental)
project_root = Path(__file__).parent.parent
experimental_path = project_root / "experimental"
sys.path.insert(0, str(experimental_path))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_experimental_mcp_simple():
    """Simple test of the experimental MCP client."""
    try:
        logger.info("Testing experimental ParticlePhysics MCP client...")
        
        # Import the experimental MCP client
        from particlephysics_mcp import (
            search_particle_experimental,
            list_decays_experimental
        )
        
        logger.info("✓ Successfully imported experimental MCP functions")
        
        # Test particle search
        logger.info("Testing particle search for 'electron'...")
        result = await search_particle_experimental("electron")
        logger.info(f"Search result type: {type(result)}")
        logger.info(f"Search result: {result}")
        
        # Test decay listing
        logger.info("Testing decay listing for 'muon'...")
        decay_result = await list_decays_experimental("muon")
        logger.info(f"Decay result type: {type(decay_result)}")
        logger.info(f"Decay result: {decay_result}")
        
        # Test with a known stable particle
        logger.info("Testing search for 'proton'...")
        proton_result = await search_particle_experimental("proton")
        logger.info(f"Proton result: {proton_result}")
        
        logger.info("✓ Experimental MCP tests completed successfully")
        return True
        
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    logger.info("Starting simple experimental MCP tests...")
    
    success = await test_experimental_mcp_simple()
    
    if success:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
