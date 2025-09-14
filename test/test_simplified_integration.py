#!/usr/bin/env python3
"""
Test the simplified agent search integration that uses only ParticlePhysics MCP.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from feynmancraft_adk.integrations.agent_search_integration import (
    enhanced_agent_search_with_particle_info,
    quick_particle_validation_for_agent,
    get_diagram_relevant_particle_info,
    extract_particles_from_query
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_simplified_integration():
    """Test the simplified integration using only MCP."""
    
    print("🧪 Testing Simplified Agent Search Integration (MCP Only)")
    print("=" * 60)
    
    # Test 1: Extract particles from query
    print("\n1. Testing particle extraction from query...")
    test_query = "electron muon scattering with photon exchange"
    extracted = extract_particles_from_query(test_query)
    print(f"Query: {test_query}")
    print(f"Extracted particles: {extracted}")
    
    # Test 2: Quick validation
    print("\n2. Testing quick particle validation...")
    test_particles = ["electron", "muon", "photon"]
    validation_result = await quick_particle_validation_for_agent(test_particles)
    print(f"Validation result: {validation_result}")
    
    # Test 3: Enhanced search with particles
    print("\n3. Testing enhanced search with specific particles...")
    search_result = await enhanced_agent_search_with_particle_info(
        "electron muon scattering", 
        particles=["electron", "muon"]
    )
    print(f"Search result summary:")
    print(f"  - Status: {search_result.get('status', 'unknown')}")
    print(f"  - Source: {search_result.get('source', 'unknown')}")
    print(f"  - Particles found: {len(search_result.get('mcp_particle_info', []))}")
    
    # Test 4: Enhanced search without particles (auto-extraction)
    print("\n4. Testing enhanced search with particle extraction...")
    auto_search_result = await enhanced_agent_search_with_particle_info(
        "tau decay with neutrino"
    )
    print(f"Auto-search result:")
    print(f"  - Status: {auto_search_result.get('status', 'unknown')}")
    print(f"  - Extracted particles: {auto_search_result.get('particles_extracted', [])}")
    print(f"  - MCP results: {len(auto_search_result.get('mcp_particle_info', []))}")
    
    # Test 5: Diagram-relevant info
    print("\n5. Testing diagram-relevant particle info...")
    diagram_info = await get_diagram_relevant_particle_info(["electron", "photon"])
    print(f"Diagram info:")
    print(f"  - Total particles: {diagram_info.get('total_particles', 0)}")
    print(f"  - Valid particles: {diagram_info.get('valid_particles', 0)}")
    print(f"  - Success rate: {diagram_info.get('success_rate', 0):.2f}")
    print(f"  - Hints: {diagram_info.get('diagram_hints', [])}")
    
    print("\n✅ All tests completed!")
    print("\n🎯 Key Benefits of Simplified Approach:")
    print("  - Single source of truth (ParticlePhysics MCP)")
    print("  - Fast and direct particle information retrieval")
    print("  - No redundant local searches")
    print("  - Comprehensive decay and particle data")
    print("  - Simple, maintainable codebase")


async def test_mcp_direct():
    """Test direct MCP functions to ensure they work."""
    print("\n🔧 Testing direct MCP functions...")
    
    try:
        from experimental.particlephysics_mcp import (
            search_particle_experimental,
            list_decays_experimental
        )
        
        # Test direct MCP search
        electron_result = await search_particle_experimental("electron")
        print(f"Direct MCP electron search: {electron_result}")
        
        # Test direct MCP decay
        muon_decays = await list_decays_experimental("muon")
        print(f"Direct MCP muon decays: {muon_decays}")
        
        print("✅ Direct MCP functions working!")
        
    except Exception as e:
        print(f"❌ Direct MCP test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    async def main():
        print("🚀 Starting Simplified Integration Test")
        
        # First test direct MCP
        mcp_works = await test_mcp_direct()
        
        if mcp_works:
            # Then test the integration
            await test_simplified_integration()
        else:
            print("❌ Skipping integration tests due to MCP issues")
    
    asyncio.run(main())
