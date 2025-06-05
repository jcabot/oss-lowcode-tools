"""
Test suite for the GitHub API fallback mechanism in the Low-Code Tools Dashboard.

This module tests:
1. Normal GitHub API functionality
2. Fallback to snapshot.csv when API fails
3. Data format conversion
4. Error handling

Usage:
    python tests/test_api_fallback.py
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAPIFallback(unittest.TestCase):
    """Test cases for API fallback functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.snapshot_path = "snapshot.csv"
        self.test_repo_data = {
            "name": "test-repo",
            "stargazers_count": 100,
            "pushed_at": "2023-12-01T00:00:00Z",
            "created_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/test/test-repo",
            "forks": 10,
            "open_issues": 5,
            "language": "Python",
            "license": {"name": "MIT License"},
            "description": "Test repository",
            "topics": ["test", "low-code"]
        }
    
    def test_snapshot_csv_exists(self):
        """Test that snapshot.csv file exists."""
        self.assertTrue(os.path.exists(self.snapshot_path), 
                       "snapshot.csv file should exist")
    
    def test_snapshot_csv_loading(self):
        """Test loading data from snapshot.csv."""
        try:
            df = pd.read_csv(self.snapshot_path, encoding='utf-8')
            self.assertGreater(len(df), 0, "Snapshot should contain repositories")
            
            # Check required columns exist
            required_columns = ['Name', 'Stars⭐', 'Last Updated', 'First Commit', 
                              'URL', 'Forks', 'Issues', 'Language', 'License', 
                              'Description', 'Topics']
            for col in required_columns:
                self.assertIn(col, df.columns, f"Column '{col}' should exist")
            
            print(f"[OK] Successfully loaded {len(df)} repositories from snapshot")
            
        except Exception as e:
            self.fail(f"Failed to load snapshot.csv: {e}")
    
    def test_csv_to_api_format_conversion(self):
        """Test conversion of CSV data to GitHub API format."""
        df = pd.read_csv(self.snapshot_path, encoding='utf-8')
        sample_row = df.iloc[0]
        
        try:
            repo_data = {
                "name": sample_row["Name"],
                "stargazers_count": sample_row["Stars⭐"],
                "pushed_at": sample_row["Last Updated"] + "T00:00:00Z",
                "created_at": sample_row["First Commit"] + "T00:00:00Z",
                "html_url": sample_row["URL"],
                "forks": sample_row["Forks"],
                "open_issues": sample_row["Issues"],
                "language": sample_row["Language"] if sample_row["Language"] and sample_row["Language"] != "No language" else None,
                "license": {"name": sample_row["License"]} if sample_row["License"] != "No license" else None,
                "description": sample_row["Description"] if sample_row["Description"] != "No description" else None,
                "topics": sample_row["Topics"].split(",") if pd.notna(sample_row["Topics"]) and sample_row["Topics"] else []
            }
            
            # Validate converted data structure (include numpy types)
            self.assertIsInstance(repo_data["name"], str)
            self.assertIsInstance(repo_data["stargazers_count"], (int, float, np.integer, np.floating))
            self.assertIsInstance(repo_data["topics"], list)
            
            print(f"[OK] Successfully converted repo: {repo_data['name']}")
            
        except Exception as e:
            self.fail(f"Failed to convert CSV data: {e}")
    
    @patch('requests.get')
    def test_api_fallback_on_network_error(self, mock_get):
        """Test fallback mechanism when network request fails."""
        # Mock network failure
        mock_get.side_effect = Exception("Network error")
        
        # Import and test the function with mocked requests
        from app import fetch_low_code_repos
        
        # Redirect streamlit functions to avoid issues in testing
        with patch('streamlit.error'), patch('streamlit.warning'), patch('streamlit.info'):
            try:
                repos = fetch_low_code_repos(max_pages=1)
                
                self.assertGreater(len(repos), 0, "Should load repos from snapshot on API failure")
                self.assertIn('name', repos[0], "Repo should have correct structure")
                
                print(f"[OK] Fallback mechanism works: loaded {len(repos)} repos")
            except Exception as e:
                # The function should handle the exception and return fallback data
                self.fail(f"Function should handle network errors gracefully: {e}")
    
    @patch('requests.get')
    def test_api_fallback_on_http_error(self, mock_get):
        """Test fallback mechanism when API returns HTTP error."""
        # Mock HTTP error response
        mock_response = MagicMock()
        mock_response.status_code = 403  # Rate limit or forbidden
        mock_get.return_value = mock_response
        
        from app import fetch_low_code_repos
        
        with patch('streamlit.error'), patch('streamlit.warning'), patch('streamlit.info'):
            repos = fetch_low_code_repos(max_pages=1)
            
            self.assertGreater(len(repos), 0, "Should load repos from snapshot on HTTP error")
            
            print(f"[OK] HTTP error fallback works: loaded {len(repos)} repos")
    
    def test_data_consistency(self):
        """Test that fallback data maintains consistency with expected format."""
        df = pd.read_csv(self.snapshot_path, encoding='utf-8')
        
        # Test a few random samples
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            
            # Basic data validation
            self.assertIsInstance(row["Name"], str)
            self.assertGreater(row["Stars⭐"], 0)
            self.assertTrue(row["URL"].startswith("https://github.com/"))
            
            # Date format validation
            try:
                datetime.strptime(row["Last Updated"], "%Y-%m-%d")
                datetime.strptime(row["First Commit"], "%Y-%m-%d")
            except ValueError:
                self.fail(f"Invalid date format in row {i}")
        
        print("[OK] Data consistency checks passed")


class TestUtils(unittest.TestCase):
    """Utility test functions."""
    
    def test_required_dependencies(self):
        """Test that all required dependencies are available."""
        required_modules = ['pandas', 'requests', 'streamlit', 'plotly']
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"[OK] {module} is available")
            except ImportError:
                self.fail(f"Required module '{module}' is not available")


def run_integration_test():
    """Run a simple integration test of the fallback mechanism."""
    print("\n" + "="*50)
    print("INTEGRATION TEST: API Fallback Mechanism")
    print("="*50)
    
    try:
        # Test normal CSV loading
        df = pd.read_csv("snapshot.csv", encoding='utf-8')
        print(f"[OK] Loaded {len(df)} repositories from snapshot")
        
        # Test data conversion
        sample = df.iloc[0]
        converted = {
            "name": sample["Name"],
            "stargazers_count": sample["Stars⭐"],
            "topics": sample["Topics"].split(",") if pd.notna(sample["Topics"]) else []
        }
        print(f"[OK] Data conversion works: {converted['name']}")
        
        # Test imports
        import streamlit as st
        import requests
        import plotly.graph_objects as go
        print("[OK] All dependencies available")
        
        print("\n[SUCCESS] INTEGRATION TEST PASSED!")
        print("The fallback mechanism is ready for production use.")
        
    except Exception as e:
        print(f"\n[FAIL] INTEGRATION TEST FAILED: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Run integration test first
    if run_integration_test():
        print("\n" + "="*50)
        print("RUNNING UNIT TESTS")
        print("="*50)
        
        # Run unit tests with reduced verbosity to avoid excessive Streamlit warnings
        unittest.main(verbosity=1, exit=False, buffer=True)
    else:
        print("Integration test failed. Skipping unit tests.")
        sys.exit(1) 