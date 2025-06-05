# Test Suite for Low-Code Tools Dashboard

This directory contains tests for the GitHub API fallback mechanism and general functionality of the Low-Code Tools Dashboard.

## Quick Start

### Run All Tests (Recommended)
```bash
python run_tests.py
```

### Run Specific Test Types
```bash
python run_tests.py simple    # Quick tests for daily development
python run_tests.py full      # Comprehensive fallback tests
```

## Test Files

### `test_simple.py`
Quick and easy tests for daily development use.

**Usage:**
```bash
python tests/test_simple.py
```

**Tests:**
- [OK] Snapshot CSV loading
- [OK] Dependencies availability  
- [OK] Data format conversion

### `test_api_fallback.py`
Comprehensive test suite with unit tests for the fallback mechanism.

**Usage:**
```bash
python tests/test_api_fallback.py
```

**Tests:**
- [OK] Snapshot CSV existence and loading
- [OK] CSV to GitHub API format conversion
- [OK] Network error fallback simulation
- [OK] HTTP error fallback simulation
- [OK] Data consistency validation
- [OK] Dependencies checking

### `run_tests.py` (Test Runner)
Convenient test runner script with clean output formatting.

**Usage:**
```bash
python run_tests.py           # Run all tests
python run_tests.py simple    # Run only simple tests
python run_tests.py full      # Run comprehensive tests
```

## When to Run Tests

### Daily Development
```bash
python run_tests.py simple
```
Quick verification that everything is working correctly.

### Before Deployment
```bash
python run_tests.py all
```
Complete test suite to ensure fallback mechanism works.

### After Changes
Run tests after modifying:
- `app.py` (especially `fetch_low_code_repos` function)
- `snapshot.csv` (data updates)
- Dependencies (requirements.txt updates)

## Expected Output

### Successful Test Run
```
🚀 Low-Code Tools Dashboard Test Runner
==================================================
🧪 Running Simple Tests...
==================================================
==================================================
SIMPLE DASHBOARD TESTS
==================================================
Testing snapshot.csv loading...
[OK] Loaded 174 repositories
[OK] Sample repo: n8n (104022 stars)

Testing dependencies...
[OK] pandas
[OK] streamlit
[OK] requests
[OK] plotly

Testing data conversion...
[OK] Converted: n8n with 20 topics

==================================================
SUCCESS: ALL TESTS PASSED!
The dashboard is ready to use.
==================================================

🔬 Running Comprehensive Tests...
==================================================

==================================================
INTEGRATION TEST: API Fallback Mechanism
==================================================
[OK] Loaded 174 repositories from snapshot
[OK] Data conversion works: n8n
[OK] All dependencies available

[SUCCESS] INTEGRATION TEST PASSED!
The fallback mechanism is ready for production use.

==================================================
RUNNING UNIT TESTS
==================================================

==================================================
🎉 ALL TESTS PASSED!
✅ The dashboard is ready for use.
==================================================
```

## Troubleshooting

### Common Issues

**"snapshot.csv not found"**
- Ensure you're running tests from the project root directory
- Verify `snapshot.csv` exists in the project root

**"Module not found"**
- Install missing dependencies: `pip install streamlit pandas plotly requests`
- Check your Python environment

**"Unicode/Encoding errors"**
- Tests have been updated to avoid Unicode issues on Windows
- All emojis replaced with [OK]/[FAIL] markers for compatibility

### Manual Testing

You can also manually test the fallback by temporarily:

1. **Disconnecting from internet** and running the dashboard
2. **Modifying the GitHub API URL** in `app.py` to an invalid endpoint
3. **Setting very low rate limits** to trigger API failures

The dashboard should automatically switch to snapshot data with appropriate user notifications.

## Test Structure

```
tests/
├── README.md              # This file
├── test_simple.py         # Quick daily tests
└── test_api_fallback.py   # Comprehensive fallback tests

run_tests.py               # Test runner script (in project root)
```

## Adding New Tests

When adding new functionality, consider adding tests for:
- New data sources or APIs
- New data processing functions
- New UI components that depend on data
- Error handling scenarios

Follow the existing test patterns and update this README accordingly.

## Continuous Integration

These tests are designed to be CI/CD friendly:
- No external dependencies beyond the app requirements
- Clean exit codes (0 = success, 1 = failure)
- Minimal output for automated systems
- Cross-platform compatibility (Windows/Unix) 