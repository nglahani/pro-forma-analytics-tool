"""
Integration tests for production data validation.

Tests the data population work completed to ensure all 11 pro-forma parameters
have adequate production-grade data coverage.
"""

import unittest
import sqlite3
import pandas as pd
from datetime import datetime, timedelta


class TestProductionDataValidation(unittest.TestCase):
    """Test cases for validating production-grade data coverage."""

    def setUp(self):
        """Set up database connections for testing."""
        self.market_db = sqlite3.connect('data/databases/market_data.db')
        self.property_db = sqlite3.connect('data/databases/property_data.db')
        self.economic_db = sqlite3.connect('data/databases/economic_data.db')
        
        # Expected MSAs for geographic coverage
        self.expected_msas = {
            '35620': 'New York-Newark-Jersey City, NY-NJ-PA',
            '31080': 'Los Angeles-Long Beach-Anaheim, CA', 
            '16980': 'Chicago-Naperville-Elgin, IL-IN-WI',
            '47900': 'Washington-Arlington-Alexandria, DC-VA-MD-WV',
            '33100': 'Miami-Fort Lauderdale-West Palm Beach, FL'
        }

    def tearDown(self):
        """Clean up database connections."""
        self.market_db.close()
        self.property_db.close()
        self.economic_db.close()

    def test_interest_rates_data_coverage(self):
        """Test that interest rate parameters have adequate coverage."""
        # Test treasury_10y coverage
        treasury_data = pd.read_sql_query(
            "SELECT * FROM interest_rates WHERE parameter_name = 'treasury_10y'",
            self.market_db
        )
        self.assertGreater(len(treasury_data), 50, "Treasury 10Y should have 50+ data points")
        
        # Test commercial_mortgage_rate coverage
        cmr_data = pd.read_sql_query(
            "SELECT * FROM interest_rates WHERE parameter_name = 'commercial_mortgage_rate'",
            self.market_db
        )
        self.assertGreater(len(cmr_data), 50, "Commercial mortgage rate should have 50+ data points")
        
        # Test date coverage spans multiple years
        treasury_dates = pd.to_datetime(treasury_data['date'])
        date_span = (treasury_dates.max() - treasury_dates.min()).days
        self.assertGreater(date_span, 365 * 10, "Data should span at least 10 years")
        
        # Test that commercial mortgage rates are higher than treasury rates
        for _, treasury_row in treasury_data.iterrows():
            cmr_row = cmr_data[cmr_data['date'] == treasury_row['date']]
            if not cmr_row.empty:
                self.assertGreater(
                    cmr_row.iloc[0]['value'], 
                    treasury_row['value'],
                    f"Commercial mortgage rate should exceed treasury rate on {treasury_row['date']}"
                )

    def test_cap_rates_data_coverage(self):
        """Test that cap rate data has adequate MSA coverage."""
        cap_data = pd.read_sql_query("SELECT * FROM cap_rates", self.market_db)
        
        # Test minimum record count
        self.assertGreater(len(cap_data), 100, "Cap rates should have 100+ data points")
        
        # Test MSA coverage
        unique_msas = cap_data['geographic_code'].nunique()
        self.assertGreaterEqual(unique_msas, 3, "Cap rates should cover at least 3 MSAs")
        
        # Test value ranges are reasonable (3% to 12%)
        self.assertTrue(
            (cap_data['value'] >= 0.03).all() and (cap_data['value'] <= 0.12).all(),
            "Cap rates should be between 3% and 12%"
        )

    def test_rental_market_data_coverage(self):
        """Test vacancy rate and rent growth data coverage."""
        # Test vacancy rate coverage
        vacancy_data = pd.read_sql_query(
            "SELECT * FROM rental_market_data WHERE metric_name = 'vacancy_rate'",
            self.property_db
        )
        self.assertGreater(len(vacancy_data), 100, "Vacancy rates should have 100+ data points")
        
        # Test rent growth coverage
        rent_growth_data = pd.read_sql_query(
            "SELECT * FROM rental_market_data WHERE metric_name = 'rent_growth'",
            self.property_db
        )
        self.assertGreater(len(rent_growth_data), 500, "Rent growth should have 500+ data points")
        
        # Test MSA coverage for both metrics
        vacancy_msas = vacancy_data['geographic_code'].nunique()
        rent_msas = rent_growth_data['geographic_code'].nunique()
        
        self.assertGreaterEqual(vacancy_msas, 5, "Vacancy rates should cover 5+ MSAs")
        self.assertGreaterEqual(rent_msas, 5, "Rent growth should cover 5+ MSAs")
        
        # Test reasonable value ranges
        self.assertTrue(
            (vacancy_data['value'] >= 0.01).all() and (vacancy_data['value'] <= 0.15).all(),
            "Vacancy rates should be between 1% and 15%"
        )
        self.assertTrue(
            (rent_growth_data['value'] >= -0.05).all() and (rent_growth_data['value'] <= 0.20).all(),
            "Rent growth should be between -5% and 20%"
        )

    def test_property_growth_data_coverage(self):
        """Test property growth data in economic database."""
        property_growth_data = pd.read_sql_query(
            "SELECT * FROM property_growth",
            self.economic_db
        )
        
        # Test minimum record count
        self.assertGreater(len(property_growth_data), 200, "Property growth should have 200+ data points")
        
        # Test MSA coverage
        unique_msas = property_growth_data['geographic_code'].nunique()
        self.assertGreaterEqual(unique_msas, 5, "Property growth should cover 5+ MSAs")
        
        # Test date coverage
        dates = pd.to_datetime(property_growth_data['date'])
        date_span = (dates.max() - dates.min()).days
        self.assertGreater(date_span, 365 * 8, "Property growth data should span 8+ years")
        
        # Test reasonable value ranges (-10% to 30%)
        self.assertTrue(
            (property_growth_data['property_growth'] >= -0.10).all() and 
            (property_growth_data['property_growth'] <= 0.30).all(),
            "Property growth should be between -10% and 30%"
        )

    def test_expense_growth_data_coverage(self):
        """Test expense growth data coverage."""
        expense_data = pd.read_sql_query(
            "SELECT * FROM operating_expenses",
            self.property_db
        )
        
        # Test minimum record count
        self.assertGreater(len(expense_data), 200, "Expense growth should have 200+ data points")
        
        # Test MSA coverage
        unique_msas = expense_data['geographic_code'].nunique()
        self.assertGreaterEqual(unique_msas, 5, "Expense growth should cover 5+ MSAs")
        
        # Test reasonable value ranges (0% to 15%)
        self.assertTrue(
            (expense_data['expense_growth'] >= 0.0).all() and 
            (expense_data['expense_growth'] <= 0.15).all(),
            "Expense growth should be between 0% and 15%"
        )

    def test_lending_requirements_data_coverage(self):
        """Test all lending requirement parameters have adequate coverage."""
        lending_params = ['ltv_ratio', 'closing_cost_pct', 'lender_reserves']
        
        for param in lending_params:
            with self.subTest(parameter=param):
                data = pd.read_sql_query(
                    f"SELECT * FROM lending_requirements WHERE metric_name = '{param}'",
                    self.economic_db
                )
                
                # Test minimum record count
                self.assertGreater(len(data), 200, f"{param} should have 200+ data points")
                
                # Test MSA coverage
                unique_msas = data['geographic_code'].nunique()
                self.assertGreaterEqual(unique_msas, 5, f"{param} should cover 5+ MSAs")
                
                # Test parameter-specific value ranges
                if param == 'ltv_ratio':
                    self.assertTrue(
                        (data['value'] >= 0.50).all() and (data['value'] <= 0.85).all(),
                        "LTV ratios should be between 50% and 85%"
                    )
                elif param == 'closing_cost_pct':
                    self.assertTrue(
                        (data['value'] >= 0.015).all() and (data['value'] <= 0.050).all(),
                        "Closing costs should be between 1.5% and 5.0%"
                    )
                elif param == 'lender_reserves':
                    self.assertTrue(
                        (data['value'] >= 3.0).all() and (data['value'] <= 12.0).all(),
                        "Lender reserves should be between 3 and 12 months"
                    )

    def test_data_temporal_consistency(self):
        """Test that data shows realistic temporal patterns."""
        # Test that commercial mortgage rates generally track treasury rates
        treasury_data = pd.read_sql_query(
            "SELECT date, value FROM interest_rates WHERE parameter_name = 'treasury_10y' ORDER BY date",
            self.market_db
        )
        cmr_data = pd.read_sql_query(
            "SELECT date, value FROM interest_rates WHERE parameter_name = 'commercial_mortgage_rate' ORDER BY date",
            self.market_db
        )
        
        # Calculate correlation between treasury and commercial mortgage rates
        merged = pd.merge(treasury_data, cmr_data, on='date', suffixes=('_treasury', '_cmr'))
        if len(merged) > 10:
            correlation = merged['value_treasury'].corr(merged['value_cmr'])
            self.assertGreater(correlation, 0.7, "Commercial mortgage rates should correlate with treasury rates")

    def test_geographic_variation(self):
        """Test that data shows realistic geographic variation."""
        # Test that different MSAs have different average rent growth rates
        rent_growth_by_msa = pd.read_sql_query(
            """SELECT geographic_code, AVG(value) as avg_growth 
               FROM rental_market_data 
               WHERE metric_name = 'rent_growth' 
               GROUP BY geographic_code""",
            self.property_db
        )
        
        if len(rent_growth_by_msa) >= 2:
            # Test that there's variation across MSAs
            std_deviation = rent_growth_by_msa['avg_growth'].std()
            self.assertGreater(std_deviation, 0.005, "MSAs should show variation in rent growth")

    def test_complete_parameter_coverage(self):
        """Test that all 11 required parameters have data."""
        parameter_coverage = {}
        
        # Interest rates (2 parameters)
        treasury_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM interest_rates WHERE parameter_name = 'treasury_10y'",
            self.market_db
        ).iloc[0]['count']
        parameter_coverage['treasury_10y'] = treasury_count > 0
        
        cmr_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM interest_rates WHERE parameter_name = 'commercial_mortgage_rate'",
            self.market_db
        ).iloc[0]['count']
        parameter_coverage['commercial_mortgage_rate'] = cmr_count > 0
        
        # Cap rates (1 parameter)
        cap_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM cap_rates",
            self.market_db
        ).iloc[0]['count']
        parameter_coverage['cap_rate'] = cap_count > 0
        
        # Rental market (2 parameters)
        vacancy_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM rental_market_data WHERE metric_name = 'vacancy_rate'",
            self.property_db
        ).iloc[0]['count']
        parameter_coverage['vacancy_rate'] = vacancy_count > 0
        
        rent_growth_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM rental_market_data WHERE metric_name = 'rent_growth'",
            self.property_db
        ).iloc[0]['count']
        parameter_coverage['rent_growth'] = rent_growth_count > 0
        
        # Property and expense growth (2 parameters)
        property_growth_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM property_growth",
            self.economic_db
        ).iloc[0]['count']
        parameter_coverage['property_growth'] = property_growth_count > 0
        
        expense_growth_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM operating_expenses",
            self.property_db
        ).iloc[0]['count']
        parameter_coverage['expense_growth'] = expense_growth_count > 0
        
        # Lending requirements (3 parameters)
        for param in ['ltv_ratio', 'closing_cost_pct', 'lender_reserves']:
            count = pd.read_sql_query(
                f"SELECT COUNT(*) as count FROM lending_requirements WHERE metric_name = '{param}'",
                self.economic_db
            ).iloc[0]['count']
            parameter_coverage[param] = count > 0
        
        # Assert all parameters have data
        missing_params = [param for param, has_data in parameter_coverage.items() if not has_data]
        self.assertEqual(
            len(missing_params), 0,
            f"The following parameters are missing data: {missing_params}"
        )
        
        # Assert completion rate is 100%
        completion_rate = sum(parameter_coverage.values()) / len(parameter_coverage)
        self.assertEqual(completion_rate, 1.0, "All 11 parameters should have data (100% completion)")

    def test_business_rule_commercial_mortgage_spread(self):
        """Test that commercial mortgage rates maintain proper spread over treasury."""
        query = """
        SELECT t.date, t.value as treasury_rate, c.value as cmr_rate
        FROM interest_rates t
        JOIN interest_rates c ON t.date = c.date
        WHERE t.parameter_name = 'treasury_10y'
        AND c.parameter_name = 'commercial_mortgage_rate'
        """
        
        spread_data = pd.read_sql_query(query, self.market_db)
        spread_data['spread'] = spread_data['cmr_rate'] - spread_data['treasury_rate']
        
        # Spread should be between 1% and 5%
        min_spread = spread_data['spread'].min()
        max_spread = spread_data['spread'].max()
        
        self.assertGreaterEqual(min_spread, 0.01, "Commercial mortgage spread should be at least 1%")
        self.assertLessEqual(max_spread, 0.05, "Commercial mortgage spread should be at most 5%")

    def test_business_rule_ltv_ratio_bounds(self):
        """Test that LTV ratios are within reasonable business bounds."""
        ltv_data = pd.read_sql_query(
            "SELECT value FROM lending_requirements WHERE metric_name = 'ltv_ratio'",
            self.economic_db
        )
        
        # All LTV ratios should be between 50% and 85%
        self.assertTrue((ltv_data['value'] >= 0.50).all(), "All LTV ratios should be >= 50%")
        self.assertTrue((ltv_data['value'] <= 0.85).all(), "All LTV ratios should be <= 85%")
        
        # Average LTV should be reasonable (around 70-75%)
        avg_ltv = ltv_data['value'].mean()
        self.assertGreater(avg_ltv, 0.65, "Average LTV should be > 65%")
        self.assertLess(avg_ltv, 0.80, "Average LTV should be < 80%")

    def test_data_quality_metrics(self):
        """Test overall data quality metrics."""
        # Count total records across all databases
        total_records = 0
        
        # Market data records
        market_records = pd.read_sql_query("SELECT COUNT(*) as count FROM interest_rates", self.market_db).iloc[0]['count']
        market_records += pd.read_sql_query("SELECT COUNT(*) as count FROM cap_rates", self.market_db).iloc[0]['count']
        total_records += market_records
        
        # Property data records
        property_records = pd.read_sql_query("SELECT COUNT(*) as count FROM rental_market_data", self.property_db).iloc[0]['count']
        property_records += pd.read_sql_query("SELECT COUNT(*) as count FROM operating_expenses", self.property_db).iloc[0]['count']
        total_records += property_records
        
        # Economic data records
        economic_records = pd.read_sql_query("SELECT COUNT(*) as count FROM property_growth", self.economic_db).iloc[0]['count']
        economic_records += pd.read_sql_query("SELECT COUNT(*) as count FROM lending_requirements", self.economic_db).iloc[0]['count']
        total_records += economic_records
        
        # Test minimum total record count for production readiness
        self.assertGreater(total_records, 2000, "Total records should exceed 2000 for production readiness")


if __name__ == '__main__':
    unittest.main()