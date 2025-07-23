# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **pro-forma-analytics-tool** - a real estate financial analysis project that transforms static Excel-based pro formas into data-driven forecasting using Prophet time series analysis and Monte Carlo simulations.

## Current State - PHASE 1 COMPLETED ✅

The repository now has a fully functional data infrastructure with:

### ✅ Clean Database Architecture
- **4 specialized SQLite databases** with simplified schemas
- **688+ historical data points** covering 9 key pro forma metrics
- **5 major MSAs** with 15+ years of annual data (2010-2025)

### ✅ Streamlined Data Management
- `data_manager.py` - Consolidated data operations (init/collect/verify/status)
- `collect_simplified_data.py` - Efficient collection for all 9 metrics
- `verify_pro_forma_metrics.py` - Data verification system

### ✅ 9 Pro Forma Metrics Covered
1. **Interest Rate** - 48 records (national rates)
2. **Vacancy Rate** - 80 records (by MSA)
3. **LTV Ratio** - 80 records (lending requirements)
4. **Rent Growth** - 80 records (by MSA)
5. **Closing Cost (%)** - 80 records (lending requirements)
6. **Lender Reserve Requirements** - 80 records (lending requirements)
7. **Property Growth** - 80 records (by MSA)
8. **Market Cap Rate** - 80 records (by MSA)
9. **Expense Growth** - 80 records (by MSA)

## File Structure (Cleaned & Consolidated)

```
├── CLAUDE.md                     # This guide
├── data_manager.py              # 🔑 Main data operations
├── collect_simplified_data.py   # Data collection for all metrics
├── verify_pro_forma_metrics.py  # Data verification
├── excel_analysis_consolidated.py # Excel reference tools
├── config/                      # Configuration
│   ├── geography.py            # MSA/county mappings
│   ├── parameters.py           # Pro forma parameter definitions
│   └── settings.py             # Global settings
├── data/
│   ├── databases/              # 🔑 Core data storage
│   │   ├── database_manager.py # Database operations
│   │   ├── *_schema.sql       # Clean table schemas
│   │   └── *.db               # SQLite databases with data
│   └── api_sources/
│       └── fred_client.py      # FRED API integration
├── Reference_ Docs/
│   └── MultiFamily_RE_Pro_Forma.xlsx # Original reference
└── requirements.txt            # Python dependencies
```

## Development Context

### 🎯 CURRENT PHASE: Monte Carlo Simulation Engine ✅
The system now has a fully functional Monte Carlo simulation engine:
- Prophet forecasting integrated and working
- Enhanced scenario analysis with growth/risk scoring
- Parameter correlation modeling with economic relationships
- Extreme scenario identification and market classification

### 🔧 Quick Start Commands
```bash
# Check system status
python data_manager.py status

# Verify all metrics have data
python data_manager.py verify

# Full system reset (if needed)
python data_manager.py setup
```

## Key Technical Details

### Database Structure
- **market_data.db**: Interest rates, cap rates, economic indicators
- **property_data.db**: Rental market, property tax, operating expenses  
- **economic_data.db**: Regional indicators, property growth, lending requirements
- **forecast_cache.db**: Prophet forecasts, correlations, Monte Carlo results

### Geographic Coverage
- New York-Newark-Jersey City MSA
- Los Angeles-Long Beach-Anaheim MSA  
- Chicago-Naperville-Elgin MSA
- Washington-Arlington-Alexandria MSA
- Miami-Fort Lauderdale-West Palm Beach MSA

### Data Quality
- ✅ All 9 pro forma metrics have complete coverage
- ✅ 15+ years of annual historical data per metric
- ✅ Consistent geographic and temporal alignment
- ✅ No missing data gaps identified

## Reference Materials

- `Reference_ Docs/MultiFamily_RE_Pro_Forma.xlsx` - Original Excel pro forma structure
- `excel_analysis_consolidated.py` - Tools for Excel analysis if needed

## Build/Test Commands

Currently no automated build process. The system uses:
- **Python 3.8+** 
- **SQLite** (no external database required)
- **pandas, numpy** for data processing
- **requests** for API calls

## Next Development Priorities

1. **Monte Carlo Visualization** - Charts and graphs for scenario analysis
2. **Forecast Validation** - Backtesting and accuracy metrics for Prophet models
3. **Property-Specific Analysis** - Integration with specific property data inputs
4. **Scenario Export** - Export capabilities for analysis results
5. **User Interface** - Web or desktop interface for scenario analysis

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