#!/usr/bin/env python3
"""
Input File Processor

Reads hardcoded property parameters from JSON/YAML files and loads them into the database
for downstream pro forma valuation processing.
"""

import json
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, Optional
import sys

# Optional YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from property_data import (
    SimplifiedPropertyInput, ResidentialUnits, CommercialUnits,
    RenovationInfo, InvestorEquityStructure, RenovationStatus,
    property_manager as simplified_property_manager
)
from database.property_database import property_db
from core.logging_config import get_logger

logger = get_logger(__name__)


class InputFileProcessor:
    """Processes property input files and loads them into the database."""
    
    def __init__(self):
        self.supported_formats = ['.json']
        if YAML_AVAILABLE:
            self.supported_formats.extend(['.yaml', '.yml'])
    
    def process_file(self, file_path: str) -> Optional[SimplifiedPropertyInput]:
        """Process a property input file and return property data."""
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"Input file not found: {file_path}")
            return None
            
        if path.suffix.lower() not in self.supported_formats:
            logger.error(f"Unsupported file format: {path.suffix}")
            return None
        
        try:
            # Load file content
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() == '.json':
                    data = json.load(f)
                elif YAML_AVAILABLE and path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    logger.error(f"Unsupported file format or YAML not available: {path.suffix}")
                    return None
            
            # Convert to property data
            property_data = self._convert_to_property_data(data, path.stem)
            
            if property_data:
                logger.info(f"Successfully processed input file: {file_path}")
                return property_data
            else:
                logger.error(f"Failed to convert data from: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def _convert_to_property_data(self, data: Dict[str, Any], file_stem: str) -> Optional[SimplifiedPropertyInput]:
        """Convert raw data dictionary to SimplifiedPropertyInput."""
        try:
            # Generate property ID if not provided
            property_id = data.get('property_id', f"FILE_{file_stem.upper()}")
            
            # Parse analysis date
            analysis_date_str = data.get('analysis_date', date.today().isoformat())
            if isinstance(analysis_date_str, str):
                analysis_date = datetime.fromisoformat(analysis_date_str).date()
            else:
                analysis_date = date.today()
            
            # Extract basic parameters
            basic = data.get('basic_parameters', {})
            
            # Create residential units
            residential_units = ResidentialUnits(
                total_units=basic.get('residential_units', 0),
                average_rent_per_unit=basic.get('residential_rent_per_unit', 0)
            )
            
            # Create commercial units (optional)
            commercial_units = None
            if basic.get('commercial_units', 0) > 0:
                commercial_units = CommercialUnits(
                    total_units=basic.get('commercial_units', 0),
                    average_rent_per_unit=basic.get('commercial_rent_per_unit', 0)
                )
            
            # Create renovation info
            renovation_months = basic.get('renovation_time_months', 0)
            renovation_info = RenovationInfo(
                status=RenovationStatus.PLANNED if renovation_months > 0 else RenovationStatus.NOT_NEEDED,
                anticipated_duration_months=renovation_months if renovation_months > 0 else None
            )
            
            # Create equity structure
            equity_structure = InvestorEquityStructure(
                investor_equity_share_pct=basic.get('investor_equity_share_pct', 50.0),
                self_cash_percentage=basic.get('self_cash_percentage', 25.0)
            )
            
            # Extract location info
            location = data.get('location', {})
            
            # Extract financial info
            financial = data.get('financial', {})
            
            # Create property data
            property_data = SimplifiedPropertyInput(
                property_id=property_id,
                property_name=data.get('property_name', f'Property from {file_stem}'),
                analysis_date=analysis_date,
                residential_units=residential_units,
                commercial_units=commercial_units,
                renovation_info=renovation_info,
                equity_structure=equity_structure,
                city=location.get('city', ''),
                state=location.get('state', ''),
                msa_code=location.get('msa_code', ''),
                purchase_price=financial.get('purchase_price')
            )
            
            # Store additional data in notes field for downstream processing
            additional_info = []
            if 'physical' in data:
                additional_info.append(f"Physical: {data['physical']}")
            if 'operating' in data:
                additional_info.append(f"Operating: {data['operating']}")
            
            if additional_info:
                property_data.notes = "; ".join(additional_info)
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error converting data to property format: {e}")
            return None
    
    def load_to_database(self, property_data: SimplifiedPropertyInput, user_id: str = "file_user") -> bool:
        """Load property data into the database."""
        try:
            # Add to in-memory manager
            simplified_property_manager.add_property(property_data)
            
            # Save to database
            if property_db.save_property(property_data):
                logger.info(f"Property {property_data.property_id} saved to database")
                
                # Create user listing
                listing_id = property_db.create_user_listing(user_id, property_data.property_id)
                if listing_id:
                    logger.info(f"User listing created: {listing_id}")
                
                return True
            else:
                logger.error(f"Failed to save property {property_data.property_id} to database")
                return False
                
        except Exception as e:
            logger.error(f"Error loading property to database: {e}")
            return False
    
    def process_and_load(self, file_path: str, user_id: str = "file_user") -> Optional[SimplifiedPropertyInput]:
        """Process file and load directly to database in one step."""
        property_data = self.process_file(file_path)
        
        if property_data:
            if self.load_to_database(property_data, user_id):
                return property_data
        
        return None


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process property input files')
    parser.add_argument('file_path', help='Path to property input file')
    parser.add_argument('--user-id', default='file_user', help='User ID for database entry')
    parser.add_argument('--dry-run', action='store_true', help='Process file without saving to database')
    parser.add_argument('--run-analysis', action='store_true', help='Run Monte Carlo analysis after loading')
    
    args = parser.parse_args()
    
    processor = InputFileProcessor()
    
    print(f"Processing input file: {args.file_path}")
    print("=" * 60)
    
    if args.dry_run:
        # Just process the file, don't save
        property_data = processor.process_file(args.file_path)
        if property_data:
            print("File processed successfully!")
            print(f"Property: {property_data.property_name}")
            print(f"ID: {property_data.property_id}")
            
            metrics = property_data.calculate_key_metrics()
            print(f"Total Units: {metrics['total_units']}")
            print(f"Annual Gross Rent: ${metrics['annual_gross_rent']:,.0f}")
            print(f"Property Type: {metrics['property_type'].replace('_', ' ').title()}")
        else:
            print("Failed to process file")
    else:
        # Process and load to database
        property_data = processor.process_and_load(args.file_path, args.user_id)
        if property_data:
            print("File processed and loaded to database successfully!")
            print(f"Property: {property_data.property_name}")
            print(f"ID: {property_data.property_id}")
            
            # Show database stats
            stats = property_db.get_database_stats()
            print(f"\nDatabase Status:")
            print(f"Total Properties: {stats.get('total_properties', 0)}")
            
            # Run analysis if requested
            if args.run_analysis:
                print("\nRunning Monte Carlo analysis...")
                try:
                    from monte_carlo.simulation_engine import monte_carlo_engine
                    
                    legacy_property = property_data.to_legacy_format()
                    results = monte_carlo_engine.generate_scenarios(
                        property_data=legacy_property,
                        num_scenarios=50,
                        horizon_years=5,
                        use_correlations=True
                    )
                    
                    if results.scenarios:
                        print(f"Generated {len(results.scenarios)} scenarios")
                        
                        # Save results
                        if property_db.save_analysis_results(property_data.property_id, results):
                            print("Analysis results saved to database")
                        
                        # Show basic stats
                        growth_scores = [s.scenario_summary.get('growth_score', 0) for s in results.scenarios]
                        risk_scores = [s.scenario_summary.get('risk_score', 0) for s in results.scenarios]
                        
                        import numpy as np
                        print(f"Average Growth Score: {np.mean(growth_scores):.3f}")
                        print(f"Average Risk Score: {np.mean(risk_scores):.3f}")
                    
                except Exception as e:
                    print(f"Analysis failed: {e}")
        else:
            print("Failed to process and load file")


if __name__ == "__main__":
    main()