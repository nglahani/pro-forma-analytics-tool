# Database Documentation

## Current State
All data is currently mock/test data. No live API integrations yet. The following tables exist in the SQLite databases:

### Tables and Key Fields
- **interest_rates**: `parameter_name` (e.g., 'treasury_10y', 'commercial_mortgage_rate')
- **cap_rates**: `property_type` (e.g., 'multifamily', 'office')
- **economic_indicators**: `indicator_name` (e.g., 'cpi_housing', 'unemployment_rate')
- **rental_market_data**: `metric_name` (e.g., 'rent_growth', 'vacancy_rate')
- **property_tax_data**: `tax_rate`
- **operating_expenses**: `expense_growth`
- **regional_economic_indicators**: `indicator_name` (e.g., 'unemployment_rate', 'employment_growth')
- **property_growth**: `property_growth`
- **lending_requirements**: `metric_name` (e.g., 'ltv_ratio', 'closing_cost_pct', 'lender_reserves')

## Planned API Integrations
For each metric, we plan to connect to real-world data sources:

| Metric/Table                  | Planned API/Data Source Examples                |
|-------------------------------|-----------------------------------------------|
| interest_rates                | FRED, Bankrate, Freddie Mac                   |
| cap_rates                     | CBRE, Real Capital Analytics                  |
| economic_indicators           | FRED, BLS, U.S. Census                        |
| rental_market_data            | Rentometer, Zillow, ApartmentList             |
| property_tax_data             | County Assessor APIs, ATTOM Data              |
| operating_expenses            | IREM, NAA, local property managers            |
| regional_economic_indicators  | FRED, BLS, U.S. Census                        |
| property_growth               | CoreLogic, Zillow, Redfin                     |
| lending_requirements          | Fannie Mae, Freddie Mac, lender APIs          |

## Roadmap
- Replace mock data with live API data for each metric
- Add automated data ingestion scripts
- Update analytics to use real data