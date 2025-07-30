@echo off
REM Complete Test Validation Script for Windows
REM Usage: scripts\run_full_tests.bat

echo 🚀 Starting Comprehensive Test Validation...
echo ==============================================

echo.
echo TEST 1: Environment Check
python --version
python data_manager.py status

echo.
echo TEST 2-6: Core Test Suites (91 tests total)
python -m pytest tests/unit/application/ tests/unit/infrastructure/test_edge_cases.py tests/integration/test_complete_dcf_workflow.py tests/performance/ -q

echo.
echo TEST 7: End-to-End Demo
python demo_end_to_end_workflow.py

echo.
echo TEST 8: Code Quality
black --check src/ tests/ && echo ✅ Formatting OK
isort --check-only --profile black src/ tests/ && echo ✅ Imports OK  
flake8 src/ tests/ && echo ✅ Linting OK

echo.
echo TEST 13: Linux Compatibility (Docker)
docker build -f Dockerfile.test -t proforma-linux-test .

echo.
echo 🎉 All tests completed!
echo Expected: 91/91 tests passing, NPV ~$7.8M, IRR ~64.8%
pause