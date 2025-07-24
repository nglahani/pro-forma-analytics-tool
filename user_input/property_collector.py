"""
Interactive Property Data Collector

Provides a user-friendly interface for collecting property data
with validation, formatting, and helpful prompts.
"""

import sys
from typing import Dict, List, Optional, Any
from datetime import date
import uuid

from core.property_inputs import (
    PropertyInputData, PropertyPhysicalInfo, PropertyFinancialInfo,
    PropertyLocationInfo, PropertyOperatingInfo, UnitMix,
    PropertyType, PropertyClass, property_manager
)
from user_input.input_validation import PropertyInputValidator, PropertyInputHelper, ValidationResult
from core.logging_config import get_logger


class PropertyInputCollector:
    """Interactive collector for property input data."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.validator = PropertyInputValidator()
        self.helper = PropertyInputHelper()
        
    def collect_property_data(self, property_id: Optional[str] = None) -> PropertyInputData:
        """Main method to collect complete property data from user."""
        
        print("\n" + "="*60)
        print("🏢 PROPERTY DATA COLLECTION")
        print("="*60)
        print("Please provide information about the property for analysis.")
        print("You can enter amounts with or without $ signs and commas.")
        print("Percentages can be entered as decimals (0.25) or percentages (25%).")
        print()
        
        try:
            # Generate property ID if not provided
            if not property_id:
                property_id = f"PROP_{uuid.uuid4().hex[:8].upper()}"
            
            # Collect each section
            basic_info = self._collect_basic_info(property_id)
            physical_info = self._collect_physical_info()
            financial_info = self._collect_financial_info()
            location_info = self._collect_location_info()
            operating_info = self._collect_operating_info(physical_info)
            
            # Create property data object
            property_data = PropertyInputData(
                property_id=property_id,
                property_name=basic_info['property_name'],
                analysis_date=basic_info['analysis_date'],
                physical_info=physical_info,
                financial_info=financial_info,
                location_info=location_info,
                operating_info=operating_info
            )
            
            # Display summary and confirmation
            self._display_property_summary(property_data)
            
            if self._confirm_property_data():
                # Add to property manager
                property_manager.add_property(property_data)
                print(f"\n✅ Property '{property_data.property_name}' saved successfully!")
                print(f"   Property ID: {property_data.property_id}")
                return property_data
            else:
                print("\n❌ Property data not saved.")
                return None
                
        except KeyboardInterrupt:
            print("\n\n❌ Data collection cancelled by user.")
            return None
        except Exception as e:
            self.logger.error(f"Error collecting property data: {e}")
            print(f"\n❌ Error collecting property data: {e}")
            return None
    
    def _collect_basic_info(self, property_id: str) -> Dict[str, Any]:
        """Collect basic property information."""
        print("\n📋 BASIC INFORMATION")
        print("-" * 30)
        
        # Property name
        property_name = self._get_text_input(
            "Property name (e.g., 'Sunset Apartments', 'Downtown Office Complex'): ",
            required=True
        )
        
        # Analysis date (default to today)
        date_input = self._get_text_input(
            f"Analysis date (YYYY-MM-DD, or press Enter for today): ",
            required=False
        )
        
        if date_input:
            try:
                analysis_date = date.fromisoformat(date_input)
            except ValueError:
                print("Invalid date format, using today's date.")
                analysis_date = date.today()
        else:
            analysis_date = date.today()
        
        return {
            'property_name': property_name,
            'analysis_date': analysis_date
        }
    
    def _collect_physical_info(self) -> PropertyPhysicalInfo:
        """Collect physical property information."""
        print("\n🏗️ PHYSICAL CHARACTERISTICS")
        print("-" * 30)
        
        # Property type
        print("Property type options:")
        type_options = self.helper.get_property_type_options()
        for i, (value, display) in enumerate(type_options, 1):
            print(f"  {i}. {display}")
        
        type_choice = self._get_choice_input(
            "Select property type (1-5): ",
            len(type_options)
        )
        property_type = PropertyType(type_options[type_choice - 1][0])
        
        # Property class
        print("\nProperty class options:")
        class_options = self.helper.get_property_class_options()
        for i, (value, display) in enumerate(class_options, 1):
            print(f"  {i}. {display}")
        
        class_choice = self._get_choice_input(
            "Select property class (1-3): ",
            len(class_options)
        )
        property_class = PropertyClass(class_options[class_choice - 1][0])
        
        # Total units
        total_units = self._get_validated_input(
            "Total number of units: ",
            self.validator.validate_integer,
            "total units", 1
        )
        
        # Total square feet
        total_square_feet = self._get_validated_input(
            "Total square feet: ",
            self.validator.validate_integer,
            "total square feet", 1000
        )
        
        # Year built
        year_built = self._get_validated_input(
            "Year built: ",
            self.validator.validate_year
        )
        
        # Optional fields
        year_renovated = self._get_optional_year("Year of last major renovation (optional): ")
        parking_spaces = self._get_optional_integer("Number of parking spaces (optional): ")
        stories = self._get_optional_integer("Number of stories (optional): ")
        lot_size_sf = self._get_optional_integer("Lot size in square feet (optional): ")
        
        return PropertyPhysicalInfo(
            property_type=property_type,
            property_class=property_class,
            total_units=total_units,
            total_square_feet=total_square_feet,
            year_built=year_built,
            year_renovated=year_renovated,
            parking_spaces=parking_spaces,
            stories=stories,
            lot_size_sf=lot_size_sf
        )
    
    def _collect_financial_info(self) -> PropertyFinancialInfo:
        """Collect financial information."""
        print("\n💰 FINANCIAL INFORMATION")
        print("-" * 30)
        
        # Purchase price
        purchase_price = self._get_validated_input(
            "Purchase price ($): ",
            self.validator.validate_currency,
            "purchase price"
        )
        
        # Down payment percentage
        down_payment_pct = self._get_validated_input(
            "Down payment (% or decimal, e.g., 25% or 0.25): ",
            self.validator.validate_percentage,
            "down payment percentage"
        )
        
        # Optional financial data
        current_noi = self._get_optional_currency("Current annual NOI (Net Operating Income): ")
        current_gross_rent = self._get_optional_currency("Current annual gross rent: ")
        current_expenses = self._get_optional_currency("Current annual expenses: ")
        annual_debt_service = self._get_optional_currency("Annual debt service (if known): ")
        
        return PropertyFinancialInfo(
            purchase_price=purchase_price,
            down_payment_pct=down_payment_pct,
            current_noi=current_noi,
            current_gross_rent=current_gross_rent,
            current_expenses=current_expenses,
            annual_debt_service=annual_debt_service
        )
    
    def _collect_location_info(self) -> PropertyLocationInfo:
        """Collect location information."""
        print("\n📍 LOCATION INFORMATION")
        print("-" * 30)
        
        # Address
        address = self._get_validated_input(
            "Street address: ",
            self.validator.validate_address
        )
        
        # City, State, ZIP
        while True:
            city = self._get_text_input("City: ", required=True)
            state = self._get_text_input("State (2-letter code, e.g., CA, NY): ", required=True)
            zip_code = self._get_text_input("ZIP code: ", required=True)
            
            location_result = self.validator.validate_city_state_zip(city, state, zip_code)
            
            if location_result.is_valid:
                city = location_result.formatted_value['city']
                state = location_result.formatted_value['state']
                zip_code = location_result.formatted_value['zip_code']
                break
            else:
                print("❌ Location validation errors:")
                for error in location_result.errors:
                    print(f"   - {error}")
                print("Please try again.\n")
        
        # MSA code lookup
        msa_code = self.validator.lookup_msa_code(city, state)
        
        if msa_code:
            print(f"✅ Automatically detected MSA: {msa_code}")
            from config.geography import MSA_MAPPINGS
            msa_name = MSA_MAPPINGS[msa_code]['name']
            print(f"   ({msa_name})")
        else:
            print("⚠️  Could not automatically detect MSA.")
            print("Supported MSAs:")
            msa_options = self.helper.get_supported_msas()
            for i, (code, name) in enumerate(msa_options, 1):
                print(f"  {i}. {name} ({code})")
            
            msa_choice = self._get_choice_input(
                "Select the closest MSA (1-5): ",
                len(msa_options)
            )
            msa_code = msa_options[msa_choice - 1][0]
        
        return PropertyLocationInfo(
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            msa_code=msa_code
        )
    
    def _collect_operating_info(self, physical_info: PropertyPhysicalInfo) -> PropertyOperatingInfo:
        """Collect operating information."""
        print("\n⚙️ OPERATING INFORMATION")
        print("-" * 30)
        
        # Management fee
        mgmt_fee = self._get_validated_input(
            "Management fee (% or decimal, default 5%): ",
            self.validator.validate_percentage,
            "management fee",
            default=0.05
        )
        
        # Maintenance reserve
        maint_reserve = self._get_validated_input(
            "Maintenance reserve (% or decimal, default 2%): ",
            self.validator.validate_percentage,
            "maintenance reserve",
            default=0.02
        )
        
        # Optional operating expenses
        insurance_annual = self._get_optional_currency("Annual insurance cost: ")
        property_tax_annual = self._get_optional_currency("Annual property taxes: ")
        utilities_annual = self._get_optional_currency("Annual utilities cost: ")
        other_expenses_annual = self._get_optional_currency("Other annual expenses: ")
        
        # Unit mix (for multifamily properties)
        unit_mix = []
        if physical_info.property_type == PropertyType.MULTIFAMILY:
            unit_mix = self._collect_unit_mix(physical_info.total_units)
        
        return PropertyOperatingInfo(
            management_fee_pct=mgmt_fee,
            maintenance_reserve_pct=maint_reserve,
            insurance_annual=insurance_annual,
            property_tax_annual=property_tax_annual,
            utilities_annual=utilities_annual,
            other_expenses_annual=other_expenses_annual,
            unit_mix=unit_mix
        )
    
    def _collect_unit_mix(self, total_units: int) -> List[UnitMix]:
        """Collect unit mix information for multifamily properties."""
        print("\n🏠 UNIT MIX (Multifamily Property)")
        print("-" * 30)
        print(f"Total units to account for: {total_units}")
        
        collect_mix = self._get_yes_no_input(
            "Would you like to specify unit mix details? (y/n, default: n): ",
            default=False
        )
        
        if not collect_mix:
            return []
        
        unit_mix = []
        remaining_units = total_units
        
        while remaining_units > 0:
            print(f"\nRemaining units to specify: {remaining_units}")
            
            unit_type = self._get_text_input(
                "Unit type (e.g., '1BR/1BA', '2BR/2BA', 'Studio'): ",
                required=True
            )
            
            max_count = remaining_units
            count = self._get_validated_input(
                f"Number of {unit_type} units (max {max_count}): ",
                self.validator.validate_integer,
                "unit count", 1
            )
            
            if count > max_count:
                print(f"❌ Cannot specify more than {max_count} units.")
                continue
            
            avg_sqft = self._get_validated_input(
                f"Average square feet per {unit_type} unit: ",
                self.validator.validate_integer,
                "square feet", 200
            )
            
            current_rent = self._get_validated_input(
                f"Current monthly rent for {unit_type} units ($): ",
                self.validator.validate_currency,
                "monthly rent"
            )
            
            unit_mix.append(UnitMix(
                unit_type=unit_type,
                count=count,
                avg_square_feet=avg_sqft,
                current_rent=current_rent
            ))
            
            remaining_units -= count
            
            if remaining_units > 0:
                continue_mix = self._get_yes_no_input(
                    f"Add another unit type? ({remaining_units} units remaining) (y/n): ",
                    default=True
                )
                if not continue_mix:
                    print(f"⚠️  Warning: {remaining_units} units not specified in mix.")
                    break
        
        return unit_mix
    
    def _display_property_summary(self, property_data: PropertyInputData):
        """Display a summary of the collected property data."""
        print("\n" + "="*60)
        print("📊 PROPERTY SUMMARY")
        print("="*60)
        
        print(f"Property Name: {property_data.property_name}")
        print(f"Property ID: {property_data.property_id}")
        print(f"Analysis Date: {property_data.analysis_date}")
        
        print(f"\n🏗️ Physical:")
        print(f"   Type: {property_data.physical_info.property_type.value.title()}")
        print(f"   Class: {property_data.physical_info.property_class.value.replace('_', ' ').title()}")
        print(f"   Units: {property_data.physical_info.total_units:,}")
        print(f"   Square Feet: {property_data.physical_info.total_square_feet:,}")
        print(f"   Year Built: {property_data.physical_info.year_built}")
        
        print(f"\n💰 Financial:")
        print(f"   Purchase Price: {self.helper.format_currency(property_data.financial_info.purchase_price)}")
        print(f"   Down Payment: {self.helper.format_percentage(property_data.financial_info.down_payment_pct)}")
        print(f"   Loan Amount: {self.helper.format_currency(property_data.financial_info.loan_amount)}")
        
        print(f"\n📍 Location:")
        print(f"   Address: {property_data.location_info.address}")
        print(f"   City: {property_data.location_info.city}, {property_data.location_info.state} {property_data.location_info.zip_code}")
        print(f"   MSA Code: {property_data.location_info.msa_code}")
        
        # Calculate and display key metrics
        metrics = self.helper.calculate_financial_metrics(property_data)
        print(f"\n📈 Key Metrics:")
        print(f"   Price per Unit: {self.helper.format_currency(metrics['price_per_unit'])}")
        print(f"   Price per SF: ${metrics['price_per_sf']:.0f}")
        if 'current_cap_rate' in metrics:
            print(f"   Current Cap Rate: {self.helper.format_percentage(metrics['current_cap_rate'])}")
        print(f"   Cash Required: {self.helper.format_currency(metrics['down_payment'])}")
        
        # Unit mix summary
        if property_data.operating_info.unit_mix:
            print(f"\n🏠 Unit Mix:")
            for unit in property_data.operating_info.unit_mix:
                monthly_income = unit.count * unit.current_rent
                print(f"   {unit.unit_type}: {unit.count} units @ ${unit.current_rent:,.0f}/mo "
                      f"({unit.avg_square_feet} SF) = ${monthly_income:,.0f}/mo")
    
    def _confirm_property_data(self) -> bool:
        """Confirm if the user wants to save the property data."""
        return self._get_yes_no_input("\n💾 Save this property data? (y/n): ", default=True)
    
    # Helper methods for input collection
    
    def _get_text_input(self, prompt: str, required: bool = True) -> str:
        """Get text input with validation."""
        while True:
            value = input(prompt).strip()
            
            if value or not required:
                return value
            
            print("❌ This field is required. Please enter a value.")
    
    def _get_choice_input(self, prompt: str, max_choice: int) -> int:
        """Get choice input (1-N)."""
        while True:
            try:
                choice = int(input(prompt))
                if 1 <= choice <= max_choice:
                    return choice
                else:
                    print(f"❌ Please enter a number between 1 and {max_choice}.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def _get_validated_input(self, prompt: str, validator_func, *args, **kwargs):
        """Get input with validation function."""
        default = kwargs.pop('default', None)
        
        while True:
            if default is not None:
                display_prompt = f"{prompt}(default: {default}): "
            else:
                display_prompt = prompt
            
            value = input(display_prompt).strip()
            
            # Use default if no input provided
            if not value and default is not None:
                return default
            
            # Validate input
            result = validator_func(value, *args, **kwargs)
            
            # Display warnings
            for warning in result.warnings:
                print(f"⚠️  {warning}")
            
            if result.is_valid:
                return result.formatted_value
            else:
                print("❌ Validation errors:")
                for error in result.errors:
                    print(f"   - {error}")
                print("Please try again.")
    
    def _get_yes_no_input(self, prompt: str, default: bool = None) -> bool:
        """Get yes/no input."""
        if default is True:
            prompt += " (Y/n): "
        elif default is False:
            prompt += " (y/N): "
        else:
            prompt += " (y/n): "
        
        while True:
            value = input(prompt).strip().lower()
            
            if not value and default is not None:
                return default
            
            if value in ['y', 'yes']:
                return True
            elif value in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")
    
    def _get_optional_currency(self, prompt: str) -> Optional[float]:
        """Get optional currency input."""
        value = input(prompt + "(optional): ").strip()
        if not value:
            return None
        
        result = self.validator.validate_currency(value)
        
        for warning in result.warnings:
            print(f"⚠️  {warning}")
        
        if result.is_valid:
            return result.formatted_value
        else:
            print("❌ Invalid currency format, skipping.")
            return None
    
    def _get_optional_integer(self, prompt: str) -> Optional[int]:
        """Get optional integer input."""
        value = input(prompt + "(optional): ").strip()
        if not value:
            return None
        
        result = self.validator.validate_integer(value)
        
        if result.is_valid:
            return result.formatted_value
        else:
            print("❌ Invalid number format, skipping.")
            return None
    
    def _get_optional_year(self, prompt: str) -> Optional[int]:
        """Get optional year input."""
        value = input(prompt).strip()
        if not value:
            return None
        
        result = self.validator.validate_year(value)
        
        for warning in result.warnings:
            print(f"⚠️  {warning}")
        
        if result.is_valid:
            return result.formatted_value
        else:
            print("❌ Invalid year format, skipping.")
            return None


def main():
    """Main function for testing the property collector."""
    collector = PropertyInputCollector()
    
    try:
        property_data = collector.collect_property_data()
        
        if property_data:
            print(f"\n🎉 Successfully collected property data!")
            print(f"Property can now be analyzed using Monte Carlo simulation.")
            
            # Option to run Monte Carlo analysis
            run_analysis = collector._get_yes_no_input(
                "\n🎲 Run Monte Carlo analysis now? (y/n): ",
                default=True
            )
            
            if run_analysis:
                print("\n🚀 Starting Monte Carlo analysis...")
                try:
                    from monte_carlo.simulation_engine import monte_carlo_engine
                    
                    results = monte_carlo_engine.generate_scenarios(
                        property_data=property_data,
                        num_scenarios=100,
                        horizon_years=5,
                        use_correlations=True
                    )
                    
                    print(f"✅ Generated {len(results.scenarios)} scenarios successfully!")
                    print(f"   Growth scores: {min(s.scenario_summary.get('growth_score', 0) for s in results.scenarios):.3f} - {max(s.scenario_summary.get('growth_score', 0) for s in results.scenarios):.3f}")
                    print(f"   Risk scores: {min(s.scenario_summary.get('risk_score', 0) for s in results.scenarios):.3f} - {max(s.scenario_summary.get('risk_score', 0) for s in results.scenarios):.3f}")
                    
                except Exception as e:
                    print(f"❌ Error running Monte Carlo analysis: {e}")
        else:
            print("\n❌ No property data collected.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()