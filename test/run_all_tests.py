#!/usr/bin/env python3
"""
Test runner for all Python tests in the test directory.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test(test_file: Path) -> bool:
    """Run a single test file and return success status."""
    try:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_file.name}")
        print(f"{'='*60}")
        
        # Run the test
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=test_file.parent.parent,  # Run from project root
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {test_file.name} - PASSED")
            return True
        else:
            print(f"❌ {test_file.name} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {test_file.name} - ERROR: {e}")
        return False

def main():
    """Run all tests in the test directory."""
    print("🚀 Particle Physics Agent Test Runner")
    print("="*50)
    
    # Get test directory
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    print(f"Test directory: {test_dir}")
    print(f"Project root: {project_root}")
    
    # Find all Python test files
    test_files = list(test_dir.glob("test_*.py"))
    demo_files = list(test_dir.glob("demo_*.py"))
    
    all_files = test_files + demo_files
    all_files.sort()
    
    if not all_files:
        print("❌ No test files found!")
        return 1
    
    print(f"\nFound {len(all_files)} test files:")
    for f in all_files:
        print(f"  • {f.name}")
    
    # Run all tests
    passed = 0
    failed = 0
    
    for test_file in all_files:
        if run_test(test_file):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Test Summary")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📋 Total:  {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
