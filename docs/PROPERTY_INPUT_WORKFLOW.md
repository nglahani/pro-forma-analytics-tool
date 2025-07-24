# Property Input Workflow

## Overview

The property input workflow provides multiple methods for collecting property data and integrating it with the pro forma analytics system. The system supports both interactive console input and file-based batch processing.

## Input Methods

### File-Based Input (Recommended)

The file-based approach uses JSON templates to define property parameters that are automatically processed and loaded into the database.

#### Template Structure

The `property_input_template.json` file defines the complete property data structure:

```json
{
  "property_name": "Property identifier",
  "analysis_date": "YYYY-MM-DD",
  "basic_parameters": {
    "residential_units": 0,
    "renovation_time_months": 0,
    "commercial_units": 0,
    "investor_equity_share_pct": 0.0,
    "residential_rent_per_unit": 0,
    "commercial_rent_per_unit": 0,
    "self_cash_percentage": 0.0
  },
  "location": {
    "address": "Street address",
    "city": "City name",
    "state": "State code",
    "zip_code": "ZIP code",
    "msa_code": "MSA identifier"
  },
  "financial": {
    "purchase_price": 0,
    "down_payment_pct": 0.0,
    "current_gross_rent": 0,
    "estimated_expenses": 0
  },
  "physical": {
    "total_square_feet": 0,
    "year_built": 0,
    "parking_spaces": 0,
    "property_class": "class_b"
  },
  "operating": {
    "management_fee_pct": 0.0,
    "maintenance_reserve_pct": 0.0,
    "insurance_annual": 0,
    "property_tax_annual": 0
  }
}
```

#### Required Fields

The system requires seven core data fields:
1. Residential units count
2. Renovation time in months
3. Commercial units count
4. Investor equity share percentage
5. Residential rent per unit
6. Commercial rent per unit
7. Self cash percentage

#### Supported MSA Codes

The system provides market analysis for the following Metropolitan Statistical Areas:
- `35620`: New York-Newark-Jersey City MSA
- `31080`: Los Angeles-Long Beach-Anaheim MSA
- `16980`: Chicago-Naperville-Elgin MSA
- `47900`: Washington-Arlington-Alexandria MSA
- `33100`: Miami-Fort Lauderdale-West Palm Beach MSA

### Interactive Console Input

The console interface provides guided data collection with validation and real-time feedback.

#### Usage

```bash
python simplified_input_form.py
```

The interactive form collects the same core parameters as the file-based approach with step-by-step prompts and validation.

## Processing Workflow

### File Processing

1. **Input File Creation**: Create or modify a JSON file following the template structure
2. **File Processing**: Use the input file processor to parse and validate data
3. **Database Storage**: Property data is automatically stored in the SQLite database
4. **Analysis Integration**: Processed properties integrate with the Monte Carlo analysis engine

#### Command-Line Usage

```bash
# Process single file with analysis
python quick_analysis_workflow.py property_input_template.json

# Process file without analysis
python input_file_processor.py property_file.json --dry-run

# Process file and run analysis
python input_file_processor.py property_file.json --run-analysis
```

### Database Integration

The workflow automatically handles:
- Property data validation and storage
- User listing creation and tracking
- Analysis results persistence
- Database schema compliance

### Analysis Pipeline

After successful property input processing:
1. Property data is converted to internal format
2. Monte Carlo scenarios are generated using forecasted market parameters
3. Investment metrics are calculated and stored
4. Results are available for review and comparison

## Validation and Error Handling

The system provides comprehensive validation including:
- Data type and range validation
- Business rule enforcement
- MSA code verification
- Database constraint compliance

Error messages provide specific guidance for resolving validation issues.

## Output and Results

### Property Metrics

The system calculates standard investment metrics:
- Price per unit
- Gross capitalization rate
- Cash requirements
- Annual gross rent projections

### Analysis Results

Monte Carlo analysis provides:
- Growth potential scoring
- Risk assessment metrics
- Investment recommendations
- Scenario distribution analysis

## Integration Points

The property input workflow integrates with:
- Market forecasting system (Prophet-based)
- Monte Carlo simulation engine
- Database persistence layer
- Reporting and visualization components

## File Management

Input files should be:
- Stored in the project root directory
- Named descriptively (e.g., `manhattan_apartment_2024.json`)
- Validated before processing
- Archived after successful processing

## Technical Requirements

- Python 3.8 or higher
- SQLite database system
- Required Python packages per requirements.txt
- Access to market data databases