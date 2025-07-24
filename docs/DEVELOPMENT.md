# Development Guide

> **Complete guide for developers working on the pro forma analytics tool**

This guide covers development setup, testing, architecture patterns, and contribution guidelines.

---

## 🚀 Quick Development Setup

### **1. Environment Setup**
```bash
# Clone repository
git clone [repository-url]
cd pro-forma-analytics-tool

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Verify Installation**
```bash
# Test complete system
python test_simplified_system.py

# Expected output:
# [SUCCESS] All 7 data points captured!
# [SUCCESS] Property saved to database
# SYSTEM STATUS: FULLY OPERATIONAL
```

### **3. Run Test Suite**
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov=property_data --cov=monte_carlo
```

---

## 🏗️ Architecture Overview

### **Consolidated Architecture** (Post-Consolidation)
```
pro-forma-analytics-tool/
├── property_data.py              # Unified property input system
├── monte_carlo_validator.py      # Consolidated validation system
├── simplified_input_form.py      # User input interface
├── test_simplified_system.py     # Integration testing
├── src/                          # Clean architecture (domain/app/infra)
├── database/                     # Database operations
├── monte_carlo/                  # Monte Carlo engine
├── data/                         # SQLite databases and API sources
├── tests/                        # Test suite
├── docs/                         # Consolidated documentation
└── archive/                      # Legacy files
```

**Ready to contribute to the pro forma analytics tool?**

**Start with**: `python test_simplified_system.py`
- Install dependencies with `pip install -r requirements.txt`
- Run data management scripts to view or update mock data

## Current Focus
- Data modeling
- Mock/test data management
- Database schema design

## Roadmap
- Implement API integrations for each metric
- Add analytics and reporting scripts
- Develop web dashboard and REST API (future)

## Note
Docker, FastAPI, and cloud deployment instructions will be added as those features are developed.