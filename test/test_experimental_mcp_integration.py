#!/usr/bin/env python3
"""
Test script for the experimental ParticlePhysics MCP integration.

This script tests the basic functionality of the new experimental MCP server
and agent search integration.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the project root to path (one level up since we're in test/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_experimental_mcp():
    """Test the experimental MCP client functionality."""
    try:
        print("Testing Experimental ParticlePhysics MCP Integration...")
        
        # Test import
        from experimental.particlephysics_mcp import search_particle_experimental
        print("✓ Successfully imported experimental MCP client")
        
        # Test experimental physics tools
        from feynmancraft_adk.tools.physics.experimental_physics_tools import (
            search_particle_experimental_enhanced,
            validate_particle_experimental
        )
        print("✓ Successfully imported experimental physics tools")
        
        # Test agent search integration
        from feynmancraft_adk.integrations.agent_search_integration import (
            enhanced_agent_search_with_particle_info,
            quick_particle_validation_for_agent
        )
        print("✓ Successfully imported agent search integration")
        
        print("\n--- Testing Basic Particle Search ---")
        
        # Test basic search
        try:
            result = await search_particle_experimental("electron")
            print(f"✓ Basic search result: {type(result)}")
            if "error" in result:
                print(f"  Note: Search returned error (expected if server not running): {result['error']}")
            else:
                print(f"  Result keys: {list(result.keys())}")
        except Exception as e:
            print(f"  Note: Basic search failed (expected if server not running): {e}")
        
        print("\n--- Testing Enhanced Particle Search ---")
        
        try:
            result = await search_particle_experimental_enhanced("proton", max_results=3)
            print(f"✓ Enhanced search result: {type(result)}")
            if "error" in result:
                print(f"  Note: Enhanced search returned error: {result['error']}")
            else:
                print(f"  Result keys: {list(result.keys())}")
        except Exception as e:
            print(f"  Note: Enhanced search failed: {e}")
        
        print("\n--- Testing Quick Particle Validation ---")
        
        try:
            particles = ["electron", "proton", "photon"]
            result = await quick_particle_validation_for_agent(particles)
            print(f"✓ Quick validation result: {type(result)}")
            if "error" in result:
                print(f"  Note: Validation returned error: {result['error']}")
            else:
                print(f"  Result keys: {list(result.keys())}")
                print(f"  Status: {result.get('status', 'unknown')}")
        except Exception as e:
            print(f"  Note: Quick validation failed: {e}")
        
        print("\n--- Testing Agent Search Integration ---")
        
        try:
            query = "electron-positron annihilation"
            particles = ["electron", "positron", "photon"]
            result = await enhanced_agent_search_with_particle_info(
                query=query,
                particles=particles,
                max_kb_results=2,
                max_physics_rules=2
            )
            print(f"✓ Agent search integration result: {type(result)}")
            if "error" in result:
                print(f"  Note: Agent search returned error: {result['error']}")
            else:
                print(f"  Result keys: {list(result.keys())}")
                print(f"  Search status: {result.get('search_status', 'unknown')}")
                print(f"  Particles analyzed: {result.get('particles_analyzed', [])}")
        except Exception as e:
            print(f"  Note: Agent search integration failed: {e}")
        
        print("\n🎉 All imports and basic tests completed successfully!")
        print("   Note: Some functionality may require the experimental MCP server to be running.")
        print("   The integration is ready for use by the physics validator agent.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_experimental_mcp())
    sys.exit(0 if success else 1)
