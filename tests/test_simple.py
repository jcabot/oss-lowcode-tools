"""
Simple test script for the Low-Code Tools Dashboard.

Quick tests to verify:
- Snapshot data loading
- Basic functionality
- Dependencies

Usage: python tests/test_simple.py
"""

import os
import sys
import pandas as pd

def test_snapshot_loading():
    """Test that snapshot.csv loads correctly."""
    print("Testing snapshot.csv loading...")
    try:
        df = pd.read_csv('snapshot.csv', encoding='utf-8')
        print(f"[OK] Loaded {len(df)} repositories")
        print(f"[OK] Sample repo: {df.iloc[0]['Name']} ({df.iloc[0]['Stars⭐']} stars)")
        return True
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False

def test_dependencies():
    """Test that required dependencies are available."""
    print("\nTesting dependencies...")
    required = ['pandas', 'streamlit', 'requests', 'plotly']
    
    for module in required:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError:
            print(f"[FAIL] {module} not available")
            return False
    return True

def test_data_conversion():
    """Test data format conversion."""
    print("\nTesting data conversion...")
    try:
        df = pd.read_csv('snapshot.csv', encoding='utf-8')
        row = df.iloc[0]
        
        # Convert to API format
        repo = {
            "name": row["Name"],
            "stargazers_count": row["Stars⭐"],
            "topics": row["Topics"].split(",") if pd.notna(row["Topics"]) else []
        }
        
        print(f"[OK] Converted: {repo['name']} with {len(repo['topics'])} topics")
        return True
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False

def main():
    """Run all simple tests."""
    print("=" * 50)
    print("SIMPLE DASHBOARD TESTS")
    print("=" * 50)
    
    tests = [
        test_snapshot_loading,
        test_dependencies, 
        test_data_conversion
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    if all(results):
        print("SUCCESS: ALL TESTS PASSED!")
        print("The dashboard is ready to use.")
    else:
        print("FAILED: SOME TESTS FAILED!")
        print("Please check the errors above.")
    print("=" * 50)
    
    return all(results)

if __name__ == "__main__":
    main() 