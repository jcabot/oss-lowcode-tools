#!/usr/bin/env python3
"""
Test runner for the Low-Code Tools Dashboard

Simple script to run all tests with clean output.

Usage:
    python run_tests.py           # Run all tests
    python run_tests.py simple    # Run only simple tests
    python run_tests.py full      # Run comprehensive tests
"""

import sys
import subprocess
import os

def run_simple_tests():
    """Run the simple test suite."""
    print("🧪 Running Simple Tests...")
    print("=" * 50)
    
    result = subprocess.run([
        sys.executable, "tests/test_simple.py"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_comprehensive_tests():
    """Run the comprehensive test suite."""
    print("\n🔬 Running Comprehensive Tests...")
    print("=" * 50)
    
    # Suppress Streamlit warnings by redirecting stderr
    if os.name == 'nt':  # Windows
        result = subprocess.run([
            sys.executable, "tests/test_api_fallback.py"
        ], capture_output=True, text=True)
    else:  # Unix/Linux/Mac
        result = subprocess.run([
            sys.executable, "tests/test_api_fallback.py"
        ], capture_output=True, text=True)
    
    # Filter out Streamlit warnings from output
    output_lines = result.stdout.split('\n')
    filtered_lines = [line for line in output_lines 
                     if 'ScriptRunContext' not in line 
                     and 'Session state does not function' not in line
                     and 'streamlit run' not in line]
    
    filtered_output = '\n'.join(filtered_lines)
    print(filtered_output)
    
    if result.stderr and 'ScriptRunContext' not in result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def main():
    """Main test runner."""
    args = sys.argv[1:] if len(sys.argv) > 1 else ['all']
    test_type = args[0].lower()
    
    print("🚀 Low-Code Tools Dashboard Test Runner")
    print("=" * 50)
    
    if test_type in ['simple', 'quick']:
        success = run_simple_tests()
    elif test_type in ['full', 'comprehensive', 'complete']:
        success = run_comprehensive_tests()
    elif test_type in ['all', 'both']:
        simple_success = run_simple_tests()
        comprehensive_success = run_comprehensive_tests()
        success = simple_success and comprehensive_success
    else:
        print(f"❌ Unknown test type: {test_type}")
        print("Available options: simple, full, all")
        return 1
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The dashboard is ready for use.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the output above for details.")
    print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 