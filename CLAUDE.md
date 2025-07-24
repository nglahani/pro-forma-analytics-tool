# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **pro-forma-analytics-tool** - a real estate financial analysis project that transforms static Excel-based pro formas into data-driven forecasting using Prophet time series analysis and Monte Carlo simulations.

## Current State - USER WORKFLOW READY ✅

The repository is now **production-ready** for user input workflow implementation with:

### ✅ Clean Architecture Foundation
- **Domain/Application/Infrastructure** separation with dependency injection
- **Immutable entities** with comprehensive validation  
- **Repository pattern** with SQLite implementations
- **Testing infrastructure** with BDD/TDD support (95%+ coverage targets)

### ✅ Validated Data & Forecasting Engine
- **4 specialized SQLite databases** with optimized schemas
- **688+ historical data points** covering 11 key pro forma metrics
- **Prophet forecasting engine** with performance validation
- **5 major MSAs** with 15+ years of annual data (2010-2025)

### ✅ Production-Grade Monte Carlo Engine
- **500+ scenario generation** with economic correlations
- **Statistical validation**: 5/5 quality checks passed
- **Comprehensive visualization dashboard** for validation
- **Market scenario classification** (bull/bear/neutral/growth/stress markets)

### ✅ User Input Infrastructure
- `PropertyInputData` with complete validation framework
- `PropertyDataManager` for property lifecycle management
- **Integration test suite** validating complete user workflow
- **Serialization support** for API/UI consumption

### ✅ Simplified Property Input System (NEW)
- **7 Required Data Fields**: Residential units, renovation time, commercial units, equity share, rent rates, cash percentage
- **Database Backend**: SQLite storage with full CRUD operations for building listings
- **Mixed-Use Support**: Residential + commercial property combinations
- **Pro Forma Integration**: Seamless workflow to Monte Carlo analysis
- **Production Ready**: Complete with validation, testing, and documentation

### ✅ 11 Pro Forma Metrics Covered
1. **Treasury 10Y Rate** - 48 records (national rates)
2. **Commercial Mortgage Rate** - 48 records (national rates)  
3. **Fed Funds Rate** - 48 records (national rates)
4. **Cap Rate** - 80 records (by MSA)
5. **Vacancy Rate** - 80 records (by MSA)
6. **Rent Growth** - 80 records (by MSA)
7. **Expense Growth** - 80 records (by MSA)
8. **LTV Ratio** - 80 records (lending requirements)
9. **Closing Cost (%)** - 80 records (lending requirements)
10. **Lender Reserve Requirements** - 80 records (lending requirements)
11. **Property Growth** - 80 records (by MSA)

## File Structure (Production-Ready)

```
├── CLAUDE.md                     # This guide
├── src/                          # 🏗️ Clean Architecture Implementation
│   ├── domain/                   # Business entities and rules
│   │   ├── entities/            # Immutable domain entities
│   │   └── repositories/        # Repository interfaces
│   ├── application/             # Use case orchestration
│   │   └── services/            # Application services
│   ├── infrastructure/          # External concerns
│   │   ├── repositories/        # Repository implementations
│   │   └── container.py         # Dependency injection
│   └── presentation/            # UI/API layer
│       └── visualizations/      # Charts and dashboards
├── core/                        # 🔧 Legacy Core (Being Phased Out)
│   ├── property_inputs.py       # Property data structures
│   ├── logging_config.py        # Logging setup
│   └── exceptions.py            # Custom exceptions
├── monte_carlo/                 # 🎲 Monte Carlo Engine
│   └── simulation_engine.py    # Scenario generation
├── forecasting/                 # 📈 Prophet Integration
│   └── prophet_engine.py       # Time series forecasting
├── tests/                       # 🧪 Test Suite (BDD/TDD)
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # Test fixtures
├── config/                      # Configuration
│   ├── geography.py            # MSA/county mappings
│   ├── parameters.py           # Pro forma parameter definitions
│   └── settings.py             # Global settings
├── data/                        # 📊 Data Infrastructure
│   ├── databases/              # SQLite databases with schemas
│   └── api_sources/            # FRED API integration
├── validation_charts/           # ✅ Monte Carlo validation results
├── archive/                     # 📁 Archived legacy files
└── requirements.txt            # Python dependencies
```

## Development Context

### 🎯 NEXT PHASE: User Input Workflow (Ready to Begin) 🚀
The system is **production-ready** for user input workflow implementation:
- **Property Input Collection**: `PropertyInputData` structure ready for UI integration
- **Monte Carlo Integration**: Seamless workflow from user inputs to scenario analysis
- **Visualization Infrastructure**: Comprehensive charts and validation dashboards
- **Testing Framework**: Integration tests validate complete user workflow

### 🔧 Quick Start Commands
```bash
# Check system status
python data_manager.py status

# Verify all metrics have data
python data_manager.py verify

# Run Monte Carlo validation
python simple_monte_carlo_validation.py

# Run test suite
python -m pytest tests/ -v

# Full system reset (if needed)
python data_manager.py setup
```

## Key Technical Details

### Database Structure (Optimized for Performance)
- **market_data.db**: Interest rates, cap rates, economic indicators
- **property_data.db**: Rental market, property tax, operating expenses  
- **economic_data.db**: Regional indicators, property growth, lending requirements
- **forecast_cache.db**: Prophet forecasts, correlations, Monte Carlo results

### Monte Carlo Engine Features
- **Economic Correlations**: 23 correlation rules modeling real-world relationships
- **Market Classification**: Automatic bull/bear/neutral/growth/stress market detection
- **Scenario Diversity**: Growth scores (0.376-0.557), Risk scores (0.385-0.593)
- **Performance Validation**: 5/5 quality checks passed with comprehensive visualizations

### Geographic Coverage
- New York-Newark-Jersey City MSA
- Los Angeles-Long Beach-Anaheim MSA  
- Chicago-Naperville-Elgin MSA
- Washington-Arlington-Alexandria MSA
- Miami-Fort Lauderdale-West Palm Beach MSA

### Data Quality (Production-Validated)
- ✅ All 11 pro forma metrics have complete coverage
- ✅ 15+ years of annual historical data per metric
- ✅ Consistent geographic and temporal alignment
- ✅ No missing data gaps identified
- ✅ Monte Carlo simulation producing realistic scenarios
- ✅ Statistical validation with comprehensive quality checks

## Reference Materials

- `Reference_ Docs/MultiFamily_RE_Pro_Forma.xlsx` - Original Excel pro forma structure
- `excel_analysis_consolidated.py` - Tools for Excel analysis if needed

## Build/Test Commands

Production-ready testing infrastructure:
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/integration/ -v   # Integration tests

# Run with coverage
python -m pytest tests/ --cov=src --cov=core --cov=monte_carlo
```

**Dependencies**:
- **Python 3.8+** 
- **SQLite** (no external database required)
- **pandas, numpy** for data processing
- **prophet** for time series forecasting
- **pytest** for testing framework
- **matplotlib** for visualizations

## Next Development Priorities ⭐

### **Immediate Priority: User Input Workflow Implementation**

1. **Property Input Forms** - Web/desktop UI for `PropertyInputData` collection
2. **Financial Calculation Engine** - NPV, IRR, Cash-on-Cash return calculations  
3. **Investment Decision Framework** - Recommendation engine based on Monte Carlo results
4. **Results Dashboard** - Interactive visualization of analysis results

### **Secondary Priorities**

5. **API Development** - RESTful endpoints for property analysis
6. **Export Capabilities** - PDF reports and Excel export functionality
7. **Advanced Analytics** - Sensitivity analysis and stress testing
8. **Multi-Property Portfolio** - Portfolio-level analysis and optimization

### **Ready for Immediate Implementation**

The codebase architecture supports **immediate user workflow development**:
- ✅ Property data structures are production-ready
- ✅ Monte Carlo engine is validated and performing correctly
- ✅ Testing infrastructure supports TDD/BDD development  
- ✅ Clean architecture enables rapid feature development

---

# Development Workflow - Kiro-Style Spec-Driven Development

## How Kiro Works

Kiro is an AI assistant that helps build features systematically through a structured spec-driven development process.

### Core Philosophy

Instead of jumping straight into code, Kiro guides development through three phases:

1. **Requirements** - What needs to be built
2. **Design** - How it will be built  
3. **Tasks** - Step-by-step implementation plan

This ensures every feature is well-planned before implementation begins.

## The Spec Structure

Each feature gets its own folder in `.kiro/specs/{feature-name}/` containing:

- **`requirements.md`** - User stories and acceptance criteria
- **`design.md`** - Technical architecture and implementation approach
- **`tasks.md`** - Actionable coding checklist

## Workflow Process

### Phase 1: Requirements Gathering

1. Create initial requirements based on feature idea
2. Use user stories format: *"As a [role], I want [feature], so that [benefit]"*
3. Include acceptance criteria in EARS format (Easy Approach to Requirements Syntax)
   - Example: *"WHEN user clicks submit THEN system SHALL validate all fields"*
4. Iterate until requirements are approved

### Phase 2: Design Documentation

1. Research and create comprehensive `design.md`
2. Cover architecture, components, data models, error handling, testing strategy
3. May include Mermaid diagrams for visual representation
4. Address all requirements from the previous phase
5. Iterate until design is approved

### Phase 3: Task Planning

1. Break down design into actionable coding tasks in `tasks.md`
2. Create numbered checklist items (1.1, 1.2, etc.)
3. Each task references specific requirements
4. Focus only on code implementation activities
5. Prioritize incremental, testable progress
6. Iterate until task list is approved

## Key Features

- **Iterative Approval** - Explicit approval required for each document before moving to next phase
- **Requirement Traceability** - Tasks link back to specific requirements
- **Incremental Development** - Tasks build on each other progressively
- **Code-Focused** - Tasks only include activities a coding agent can execute

## Task Execution

Once spec is complete, execute tasks by:

1. Opening the `tasks.md` file
2. Clicking "Start task" next to individual task items
3. Implement one task at a time, stopping for review between tasks

## Getting Started

To begin a new feature spec:
1. Describe your feature idea
2. I'll guide you through the three-phase process
3. For existing specs, I can help review, update any phase, or execute implementation tasks

## Pro-Forma Analytics Specific Guidelines

### Business Domain Context
- **Real Estate Investment Analysis** - Focus on investor decision-making workflows
- **Financial Modeling** - Emphasis on accuracy, validation, and risk assessment
- **Data-Driven Decisions** - Replace manual assumptions with statistical forecasting

### Architecture Constraints
- **Clean Architecture** - Maintain domain/application/infrastructure separation
- **TDD/BDD Testing** - All features must include comprehensive test coverage
- **Prophet + Monte Carlo** - Leverage existing forecasting and simulation infrastructure

### Feature Prioritization
1. **Financial Calculation Engine** (highest priority - missing core business logic)
2. **Investment Decision Framework** (high priority - complete user workflow)
3. **Visualization & Reporting** (medium priority - user experience)
4. **API & Integration** (lower priority - external access)