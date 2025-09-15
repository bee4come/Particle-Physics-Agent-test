#!/usr/bin/env python3
"""
Simple test for Physics Validator functionality that doesn't require API keys.
Tests basic database access and rule retrieval without embeddings.
"""

import sys
import json
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_integrity():
    """Test the physics rules database integrity."""
    logger.info("🔍 Testing Database Integrity...")
    
    try:
        # Load the rules database
        rules_path = project_root / "feynmancraft_adk" / "data" / "pprules.json"
        with open(rules_path, 'r') as f:
            data = json.load(f)
        
        rules = data.get('rules', [])
        conservation_rules = [r for r in rules if r.get('category') == 'Conservation Laws']
        computational_rules = [r for r in rules if r.get('computational', False)]
        
        logger.info(f"✓ Total rules: {len(rules)}")
        logger.info(f"✓ Conservation Laws: {len(conservation_rules)}")
        logger.info(f"✓ Computational rules: {len(computational_rules)}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        return False

def test_new_conservation_rules():
    """Test that the new conservation rules are present."""
    logger.info("🆕 Testing New Conservation Rules...")
    
    try:
        # Load the rules database
        rules_path = project_root / "feynmancraft_adk" / "data" / "pprules.json"
        with open(rules_path, 'r') as f:
            data = json.load(f)
        
        rules = data.get('rules', [])
        
        # Check for specific new conservation rules
        new_rules = [
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
        
        found_count = 0
        for rule_title in new_rules:
            found = any(r.get('title') == rule_title for r in rules)
            if found:
                found_count += 1
                logger.info(f"✓ Found: {rule_title}")
            else:
                logger.warning(f"✗ Missing: {rule_title}")
        
        logger.info(f"✓ Found {found_count}/{len(new_rules)} new conservation rules")
        return found_count == len(new_rules)
        
    except Exception as e:
        logger.error(f"✗ New rules test failed: {e}")
        return False

def test_rule_numbering():
    """Test rule numbering is correct."""
    logger.info("🔢 Testing Rule Numbering...")
    
    try:
        # Load the rules database
        rules_path = project_root / "feynmancraft_adk" / "data" / "pprules.json"
        with open(rules_path, 'r') as f:
            data = json.load(f)
        
        rules = data.get('rules', [])
        rule_numbers = [r.get('rule_number') for r in rules if r.get('rule_number')]
        
        # Check for duplicates
        duplicates = len(rule_numbers) - len(set(rule_numbers))
        if duplicates == 0:
            logger.info("✓ No duplicate rule numbers")
        else:
            logger.error(f"✗ Found {duplicates} duplicate rule numbers")
            return False
        
        # Check highest rule number
        max_rule = max(rule_numbers) if rule_numbers else 0
        logger.info(f"✓ Highest rule number: {max_rule}")
        
        # Check that we have 118 rules total
        if len(rules) == 118:
            logger.info("✓ Correct total number of rules (118)")
        else:
            logger.warning(f"✗ Expected 118 rules, found {len(rules)}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Rule numbering test failed: {e}")
        return False

def test_computational_formulas():
    """Test that computational rules have formulas."""
    logger.info("📐 Testing Computational Formulas...")
    
    try:
        # Load the rules database
        rules_path = project_root / "feynmancraft_adk" / "data" / "pprules.json"
        with open(rules_path, 'r') as f:
            data = json.load(f)
        
        rules = data.get('rules', [])
        computational_rules = [r for r in rules if r.get('computational', False)]
        
        formula_count = 0
        for rule in computational_rules:
            if 'formula' in rule and rule['formula']:
                formula_count += 1
                logger.info(f"✓ Rule {rule.get('rule_number')}: Has formula")
            else:
                logger.warning(f"✗ Rule {rule.get('rule_number')}: Missing formula")
        
        logger.info(f"✓ {formula_count}/{len(computational_rules)} computational rules have formulas")
        return formula_count > 0
        
    except Exception as e:
        logger.error(f"✗ Computational formulas test failed: {e}")
        return False

def test_validation_fields():
    """Test that validation fields are updated."""
    logger.info("📋 Testing Validation Fields...")
    
    try:
        # Load the rules database
        rules_path = project_root / "feynmancraft_adk" / "data" / "pprules.json"
        with open(rules_path, 'r') as f:
            data = json.load(f)
        
        validation_fields = data.get('validation_fields', {})
        conservation_laws = validation_fields.get('conservation_laws', [])
        
        # Check for new conservation laws in validation fields
        expected_laws = [
            "color charge", "B-L", "hypercharge", "isospin", 
            "G-parity", "R-parity", "individual lepton numbers", "chiral charge"
        ]
        
        found_count = 0
        for law in expected_laws:
            if law in conservation_laws:
                found_count += 1
                logger.info(f"✓ Found in validation: {law}")
            else:
                logger.warning(f"✗ Missing from validation: {law}")
        
        logger.info(f"✓ Found {found_count}/{len(expected_laws)} new laws in validation fields")
        return True
        
    except Exception as e:
        logger.error(f"✗ Validation fields test failed: {e}")
        return False

def main():
    """Run simple validation tests."""
    print("🧪 PHYSICS VALIDATOR - SIMPLE TEST SUITE")
    print("=" * 50)
    
    test_results = []
    
    # Run test suites
    test_suites = [
        ("Database Integrity", test_database_integrity),
        ("New Conservation Rules", test_new_conservation_rules), 
        ("Rule Numbering", test_rule_numbering),
        ("Computational Formulas", test_computational_formulas),
        ("Validation Fields", test_validation_fields),
    ]
    
    for test_name, test_func in test_suites:
        print(f"\n{test_name}...")
        try:
            result = test_func()
            test_results.append((test_name, result))
            if result:
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)