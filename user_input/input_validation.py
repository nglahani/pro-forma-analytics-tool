"""
Enhanced Input Validation for User Property Data

Provides user-friendly validation, formatting, and helper functions
for collecting property data from users.
"""

import re
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import date
from dataclasses import dataclass

from core.property_inputs import (
    PropertyType, PropertyClass, PropertyInputData,
    PropertyPhysicalInfo, PropertyFinancialInfo, 
    PropertyLocationInfo, PropertyOperatingInfo, UnitMix
)
from core.exceptions import ValidationError
from config.geography import MSA_MAPPINGS


@dataclass
class ValidationResult:
    """Result of input validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    formatted_value: Any = None
    
    def add_error(self, message: str):
        """Add validation error."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add validation warning."""
        self.warnings.append(message)


class PropertyInputValidator:
    """Validates and formats user input for property data."""
    
    @staticmethod
    def validate_currency(value: Union[str, float, int], field_name: str = "amount") -> ValidationResult:
        """Validate and format currency input."""
        result = ValidationResult(True, [], [])
        
        if isinstance(value, str):
            # Remove common currency formatting
            cleaned = re.sub(r'[$,\s]', '', value.strip())
            
            # Handle percentage notation
            if cleaned.endswith('%'):
                result.add_error(f"{field_name} should be a dollar amount, not a percentage")
                return result
            
            try:
                value = float(cleaned)
            except ValueError:
                result.add_error(f"{field_name} must be a valid number")
                return result
        
        if not isinstance(value, (int, float)):
            result.add_error(f"{field_name} must be a number")
            return result
        
        if value <= 0:
            result.add_error(f"{field_name} must be greater than zero")
            return result
        
        # Format as currency
        result.formatted_value = float(value)
        
        # Add warnings for extreme values
        if value > 100_000_000:  # $100M
            result.add_warning(f"{field_name} is unusually high (${value:,.0f})")
        elif value < 100_000:  # $100K
            result.add_warning(f"{field_name} is unusually low (${value:,.0f})")
        
        return result
    
    @staticmethod
    def validate_percentage(value: Union[str, float, int], field_name: str = "percentage") -> ValidationResult:
        """Validate and format percentage input (0-1 or 0-100)."""
        result = ValidationResult(True, [], [])
        
        if isinstance(value, str):
            cleaned = value.strip()
            
            # Handle percentage notation
            if cleaned.endswith('%'):
                cleaned = cleaned[:-1]
                try:
                    value = float(cleaned) / 100  # Convert percentage to decimal
                except ValueError:
                    result.add_error(f"{field_name} must be a valid percentage")
                    return result
            else:
                try:
                    value = float(cleaned)
                except ValueError:
                    result.add_error(f"{field_name} must be a valid number")
                    return result
        
        if not isinstance(value, (int, float)):
            result.add_error(f"{field_name} must be a number")
            return result
        
        # Auto-detect if user entered percentage (25) vs decimal (0.25)
        if value > 1 and value <= 100:
            result.add_warning(f"Converting {value}% to decimal format ({value/100:.3f})")
            value = value / 100
        elif value > 100:
            result.add_error(f"{field_name} cannot exceed 100%")
            return result
        elif value < 0:
            result.add_error(f"{field_name} cannot be negative")
            return result
        
        result.formatted_value = float(value)
        return result
    
    @staticmethod
    def validate_integer(value: Union[str, int], field_name: str = "value", min_val: int = 0) -> ValidationResult:
        """Validate integer input."""
        result = ValidationResult(True, [], [])
        
        if isinstance(value, str):
            try:
                value = int(value.strip().replace(',', ''))
            except ValueError:
                result.add_error(f"{field_name} must be a whole number")
                return result
        
        if not isinstance(value, int):
            result.add_error(f"{field_name} must be a whole number")
            return result
        
        if value < min_val:
            result.add_error(f"{field_name} must be at least {min_val}")
            return result
        
        result.formatted_value = int(value)
        return result
    
    @staticmethod
    def validate_year(value: Union[str, int], field_name: str = "year") -> ValidationResult:
        """Validate year input."""
        result = PropertyInputValidator.validate_integer(value, field_name, 1800)
        
        if result.is_valid:
            current_year = date.today().year
            if result.formatted_value > current_year:
                result.add_error(f"{field_name} cannot be in the future")
            elif result.formatted_value < 1900:
                result.add_warning(f"{field_name} ({result.formatted_value}) is quite old")
        
        return result
    
    @staticmethod
    def validate_address(address: str) -> ValidationResult:
        """Validate address input."""
        result = ValidationResult(True, [], [])
        
        if not address or not address.strip():
            result.add_error("Address is required")
            return result
        
        address = address.strip()
        
        # Basic address validation
        if len(address) < 5:
            result.add_error("Address seems too short")
            return result
        
        # Check for common address components
        has_number = any(char.isdigit() for char in address)
        if not has_number:
            result.add_warning("Address may be missing a street number")
        
        result.formatted_value = address
        return result
    
    @staticmethod
    def validate_city_state_zip(city: str, state: str, zip_code: str) -> ValidationResult:
        """Validate city, state, zip combination."""
        result = ValidationResult(True, [], [])
        
        # Validate city
        if not city or not city.strip():
            result.add_error("City is required")
        else:
            city = city.strip().title()  # Format as Title Case
        
        # Validate state
        if not state or not state.strip():
            result.add_error("State is required")
        else:
            state = state.strip().upper()
            if len(state) != 2:
                result.add_error("State must be 2-letter abbreviation (e.g., 'CA', 'NY')")
        
        # Validate ZIP code
        if not zip_code or not zip_code.strip():
            result.add_error("ZIP code is required")
        else:
            zip_code = zip_code.strip()
            # Basic ZIP validation (5 digits or 5+4 format)
            if not re.match(r'^\d{5}(-\d{4})?$', zip_code):
                result.add_error("ZIP code must be 5 digits (e.g., '90210') or 9 digits (e.g., '90210-1234')")
        
        if result.is_valid:
            result.formatted_value = {
                'city': city,
                'state': state,
                'zip_code': zip_code
            }
        
        return result
    
    @staticmethod
    def lookup_msa_code(city: str, state: str) -> Optional[str]:
        """Look up MSA code based on city and state."""
        city_key = f"{city.strip().title()}, {state.strip().upper()}"
        
        # Check if city is in our MSA mappings
        for msa_code, msa_info in MSA_MAPPINGS.items():
            if city_key in msa_info.get('major_cities', []):
                return msa_code
        
        return None
    
    @staticmethod
    def validate_unit_mix(unit_mix_data: List[Dict[str, Any]], total_units: int) -> ValidationResult:
        """Validate unit mix data."""
        result = ValidationResult(True, [], [])
        
        if not unit_mix_data:
            result.add_warning("No unit mix provided - will use defaults")
            return result
        
        validated_units = []
        total_units_in_mix = 0
        
        for i, unit_data in enumerate(unit_mix_data):
            unit_errors = []
            
            # Validate unit type
            unit_type = unit_data.get('unit_type', '').strip()
            if not unit_type:
                unit_errors.append(f"Unit {i+1}: Unit type is required")
            
            # Validate count
            count_result = PropertyInputValidator.validate_integer(
                unit_data.get('count', 0), f"Unit {i+1} count", 1
            )
            if not count_result.is_valid:
                unit_errors.extend(count_result.errors)
            else:
                count = count_result.formatted_value
                total_units_in_mix += count
            
            # Validate square feet
            sqft_result = PropertyInputValidator.validate_integer(
                unit_data.get('avg_square_feet', 0), f"Unit {i+1} square feet", 100
            )
            if not sqft_result.is_valid:
                unit_errors.extend(sqft_result.errors)
            else:
                avg_sqft = sqft_result.formatted_value
            
            # Validate rent
            rent_result = PropertyInputValidator.validate_currency(
                unit_data.get('current_rent', 0), f"Unit {i+1} rent"
            )
            if not rent_result.is_valid:
                unit_errors.extend(rent_result.errors)
            else:
                rent = rent_result.formatted_value
            
            if unit_errors:
                result.errors.extend(unit_errors)
                result.is_valid = False
            else:
                validated_units.append(UnitMix(
                    unit_type=unit_type,
                    count=count,
                    avg_square_feet=avg_sqft,
                    current_rent=rent
                ))
        
        # Check if unit mix matches total units
        if total_units_in_mix != total_units:
            result.add_error(
                f"Unit mix total ({total_units_in_mix}) doesn't match "
                f"total property units ({total_units})"
            )
        
        if result.is_valid:
            result.formatted_value = validated_units
        
        return result


class PropertyInputHelper:
    """Helper functions for property input collection."""
    
    @staticmethod
    def get_property_type_options() -> List[Tuple[str, str]]:
        """Get property type options for forms."""
        return [
            (prop_type.value, prop_type.value.replace('_', ' ').title())
            for prop_type in PropertyType
        ]
    
    @staticmethod
    def get_property_class_options() -> List[Tuple[str, str]]:
        """Get property class options for forms."""
        return [
            (prop_class.value, prop_class.value.replace('_', ' ').title())
            for prop_class in PropertyClass
        ]
    
    @staticmethod
    def get_supported_msas() -> List[Tuple[str, str]]:
        """Get list of supported MSAs."""
        return [
            (msa_code, msa_info['name'])
            for msa_code, msa_info in MSA_MAPPINGS.items()
        ]
    
    @staticmethod
    def calculate_financial_metrics(property_data: PropertyInputData) -> Dict[str, float]:
        """Calculate helpful financial metrics for display."""
        metrics = {}
        
        # Price per unit and per sqft
        metrics['price_per_unit'] = property_data.calculate_price_per_unit()
        metrics['price_per_sf'] = property_data.calculate_price_per_sf()
        
        # Current cap rate
        cap_rate = property_data.get_current_cap_rate()
        if cap_rate:
            metrics['current_cap_rate'] = cap_rate
        
        # Loan calculations
        loan_amount = property_data.financial_info.loan_amount
        if loan_amount:
            metrics['loan_amount'] = loan_amount
            metrics['ltv_ratio'] = loan_amount / property_data.financial_info.purchase_price
        
        # Cash required
        down_payment = property_data.financial_info.purchase_price * property_data.financial_info.down_payment_pct
        metrics['down_payment'] = down_payment
        
        return metrics
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency string."""
        if amount >= 1_000_000:
            return f"${amount/1_000_000:.2f}M"
        elif amount >= 1_000:
            return f"${amount/1_000:.0f}K"
        else:
            return f"${amount:,.0f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format decimal as percentage string."""
        return f"{value*100:.1f}%"