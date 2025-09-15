#!/usr/bin/env python3
"""
Test script for the Physics Validator Agent with updated conservation rules.

This script tests the streamlined Physics Validator Agent's 7 tools and 
validates the new conservation law coverage in pprules.json.
"""

import asyncio
import sys
import json
import logging
from pathlib import Path

# Add the project root to Python path (one level up since we're in test/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_physics_rules_database():
    """Test the integrity and coverage of the physics rules database."""
    logger.info("🔍 Testing Physics Rules Database...")
    
    try:
        # Load the rules database
        rules_path = project_root / "feynmancraft_adk" / "data" / "pprules.json"
        with open(rules_path, 'r') as f:
            data = json.load(f)
        
        rules = data.get('rules', [])
        conservation_rules = [r for r in rules if r.get('category') == 'Conservation Laws']
        computational_rules = [r for r in rules if r.get('computational', False)]
        
        logger.info(f"✓ Total rules in database: {len(rules)}")
        logger.info(f"✓ Conservation Laws rules: {len(conservation_rules)}")
        logger.info(f"✓ Computational rules: {len(computational_rules)}")
        
        # Check for new conservation rules
        new_conservation_titles = [
            "Color charge conservation (SU(3)_C)",
            "B-L conservation in electroweak theory", 
            "Hypercharge conservation (electroweak)",
            "Strangeness conservation",
            "Isospin conservation",
            "G-parity conservation",
            "R-parity conservation (SUSY)",
            "Individual lepton number conservation",
            "Chiral charge conservation"
        ]
        
        found_new_rules = 0
        for title in new_conservation_titles:
            found = any(r.get('title') == title for r in rules)
            if found:
                found_new_rules += 1
                logger.info(f"✓ Found new rule: {title}")
            else:
                logger.warning(f"✗ Missing rule: {title}")
        
        logger.info(f"✓ Found {found_new_rules}/{len(new_conservation_titles)} new conservation rules")
        
        # Check rule numbering integrity
        rule_numbers = [r.get('rule_number') for r in rules if r.get('rule_number')]
        max_rule = max(rule_numbers) if rule_numbers else 0
        duplicates = len(rule_numbers) - len(set(rule_numbers))
        
        logger.info(f"✓ Highest rule number: {max_rule}")
        if duplicates == 0:
            logger.info("✓ No duplicate rule numbers")
        else:
            logger.error(f"✗ Found {duplicates} duplicate rule numbers")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        return False

async def test_physics_search_functions():
    """Test the physics search functionality."""
    logger.info("🔎 Testing Physics Search Functions...")
    
    try:
        # Import physics search functions
        from feynmancraft_adk.tools.physics.search import (
            search_physics_rules,
            search_rules_by_particles,
            search_rules_by_process
        )
        
        logger.info("✓ Successfully imported physics search functions")
        
        # Test basic search
        logger.info("Testing search for 'conservation'...")
        result = await search_physics_rules("conservation")
        if result and isinstance(result, list) and len(result) > 0:
            logger.info(f"✓ Found {len(result)} conservation rules")
        else:
            logger.warning("✗ No conservation rules found")
        
        # Test search for new conservation laws
        test_queries = [
            "color charge",
            "B-L conservation", 
            "hypercharge",
            "isospin"
        ]
        
        for query in test_queries:
            logger.info(f"Testing search for '{query}'...")
            result = await search_physics_rules(query)
            if result and isinstance(result, list) and len(result) > 0:
                logger.info(f"✓ Found {len(result)} rules for '{query}'")
            else:
                logger.warning(f"✗ No rules found for '{query}'")
        
        # Test particle-based search
        logger.info("Testing particle-based search...")
        result = search_rules_by_particles(["electron", "positron"])
        if result and isinstance(result, list) and len(result) > 0:
            logger.info(f"✓ Found {len(result)} rules for electron-positron")
        else:
            logger.warning("✗ No rules found for electron-positron")
        
        # Test process-based search
        logger.info("Testing process-based search...")
        result = search_rules_by_process("electron positron annihilation")
        if result and isinstance(result, list) and len(result) > 0:
            logger.info(f"✓ Found {len(result)} rules for annihilation process")
        else:
            logger.warning("✗ No rules found for annihilation process")
        
        return True
        
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Search test failed: {e}")
        return False

async def test_experimental_mcp_integration():
    """Test experimental MCP integration if available."""
    logger.info("🔬 Testing Experimental MCP Integration...")
    
    try:
        # Import experimental MCP functions
        from experimental.particlephysics_mcp import (
            search_particle_experimental,
            list_decays_experimental
        )
        
        logger.info("✓ Successfully imported experimental MCP functions")
        
        # Test particle search
        logger.info("Testing particle search for 'electron'...")
        result = await search_particle_experimental("electron")
        if result:
            logger.info(f"✓ Found experimental data for electron: {type(result)}")
        else:
            logger.info("ℹ️ No experimental data returned (MCP may not be running)")
        
        # Test decay search
        logger.info("Testing decay search for 'muon'...")
        result = await list_decays_experimental("muon")
        if result:
            logger.info(f"✓ Found decay data for muon: {type(result)}")
        else:
            logger.info("ℹ️ No decay data returned (MCP may not be running)")
        
        return True
        
    except ImportError as e:
        logger.warning(f"ℹ️ Experimental MCP not available: {e}")
        return False
    except Exception as e:
        logger.warning(f"ℹ️ MCP test failed (expected if server not running): {e}")
        return False

async def test_physics_validation_workflow():
    """Test the physics validation workflow."""
    logger.info("⚗️ Testing Physics Validation Workflow...")
    
    try:
        # Import validation functions
        from feynmancraft_adk.tools.physics.search import (
            validate_process_against_rules
        )
        
        logger.info("✓ Successfully imported validation functions")
        
        # Test process validation
        test_process = {
            "initial_particles": ["electron", "positron"],
            "final_particles": ["photon", "photon"],
            "interaction": "electromagnetic"
        }
        
        logger.info("Testing process validation for e+ e- → γ γ...")
        result = validate_process_against_rules(
            "electron positron annihilation to two photons",
            ["electron", "positron", "photon"]
        )
        if result:
            logger.info(f"✓ Process validation result: {type(result)}")
        else:
            logger.warning("✗ Process validation returned no result")
        
        return True
        
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Validation test failed: {e}")
        return False

async def test_conservation_law_coverage():
    """Test coverage of conservation laws in the database."""
    logger.info("📊 Testing Conservation Law Coverage...")
    
    try:
        # Import search function
        from feynmancraft_adk.tools.physics.search import search_physics_rules
        
        # Test coverage of fundamental conservation laws
        fundamental_laws = [
            "energy conservation",
            "momentum conservation", 
            "charge conservation",
            "lepton number conservation",
            "baryon number conservation"
        ]
        
        coverage_count = 0
        for law in fundamental_laws:
            result = await search_physics_rules(law)
            if result and isinstance(result, list) and len(result) > 0:
                coverage_count += 1
                logger.info(f"✓ Found rules for {law}")
            else:
                logger.warning(f"✗ No rules found for {law}")
        
        logger.info(f"✓ Conservation law coverage: {coverage_count}/{len(fundamental_laws)}")
        
        # Test new conservation laws added
        new_laws = [
            "color charge conservation",
            "B-L conservation",
            "hypercharge conservation", 
            "isospin conservation"
        ]
        
        new_coverage_count = 0
        for law in new_laws:
            result = await search_physics_rules(law)
            if result and isinstance(result, list) and len(result) > 0:
                new_coverage_count += 1
                logger.info(f"✓ Found rules for {law}")
            else:
                logger.warning(f"✗ No rules found for {law}")
        
        logger.info(f"✓ New conservation law coverage: {new_coverage_count}/{len(new_laws)}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Coverage test failed: {e}")
        return False

async def main():
    """Run all Physics Validator Agent tests."""
    print("🧪 PHYSICS VALIDATOR AGENT TEST SUITE")
    print("=" * 60)
    
    test_results = []
    
    # Run all test suites
    test_suites = [
        ("Physics Rules Database", test_physics_rules_database),
        ("Physics Search Functions", test_physics_search_functions),
        ("Conservation Law Coverage", test_conservation_law_coverage),
        ("Physics Validation Workflow", test_physics_validation_workflow),
        ("Experimental MCP Integration", test_experimental_mcp_integration),
    ]
    
    for test_name, test_func in test_suites:
        print(f"\n{test_name}...")
        try:
            result = await test_func()
            test_results.append((test_name, result))
            if result:
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)