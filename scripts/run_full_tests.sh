#!/bin/bash
# Complete Test Validation Script for Unix/Linux
# Usage: ./scripts/run_full_tests.sh

echo "🚀 Starting Comprehensive Test Validation..."
echo "=============================================="

echo -e "\nTEST 1: Environment Check"
python --version
python data_manager.py status

echo -e "\nTEST 2-6: Core Test Suites (91 tests total)"
python -m pytest tests/unit/application/ tests/unit/infrastructure/test_edge_cases.py tests/integration/test_complete_dcf_workflow.py tests/performance/ -q

echo -e "\nTEST 7: End-to-End Demo"
python demo_end_to_end_workflow.py

echo -e "\nTEST 8: Code Quality"
black --check src/ tests/ && echo "✅ Formatting OK"
isort --check-only --profile black src/ tests/ && echo "✅ Imports OK"
flake8 src/ tests/ && echo "✅ Linting OK"

echo -e "\nTEST 13: Linux Compatibility (Docker)"
docker build -f Dockerfile.test -t proforma-linux-test .

echo -e "\n🎉 All tests completed!"
echo "Expected: 91/91 tests passing, NPV ~$7.8M, IRR ~64.8%"